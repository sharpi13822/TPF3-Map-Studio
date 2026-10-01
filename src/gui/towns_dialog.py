"""
Dialog "Staedte aus OSM": erzeugt aus den geladenen OSM-Orten (place=city,
town, village, hamlet) eine Lua-Datei fuer den Ordner towns_industries.

Koordinatenursprung = Kartenmitte (im Spiel getestet). Was sizeFactors und
die Frachtbeduerfnisse bewirken, ist ungeprueft: es stehen neutrale
Standardwerte darin.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from src.heightmap.towns_export import (
    DEFAULT_KINDS,
    DEFAULT_MAX_FACTOR,
    DEFAULT_MIN_FACTOR,
    DEFAULT_SCALE,
    PLACE_KINDS,
    collect_places,
    size_factor,
    write_towns_lua,
)
from src.heightmap.tpf3_paths import find_tpf3_heightmaps_folder


class TownsDialog(QDialog):

    def __init__(self, parent, selection, osm):
        super().__init__(parent)

        self.selection = selection
        self.osm = osm
        self._places = []
        self._unchecked: set[tuple] = set()

        self.setWindowTitle("Städte aus OSM")
        self.setMinimumWidth(520)
        self.resize(560, 640)

        layout = QVBoxLayout(self)

        info = QLabel(
            "Erzeugt aus den geladenen OSM-Orten eine Städte-Datei für den "
            "Ordner towns_industries. Der Nullpunkt ist die Kartenmitte. "
            "Die Anfangsgröße der Stadt im Spiel wird aus der OSM-Einwohnerzahl "
            "abgeleitet: Faktor = Maßstab × Wurzel(Einwohner). Faktor 1 sind "
            "im Spiel etwa 100 Einwohner. Große Städte starten größer, "
            "kleine Dörfer kleiner. Industrien werden noch nicht erzeugt."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        self.kind_boxes: dict[str, QCheckBox] = {}

        for kind, label in PLACE_KINDS.items():

            box = QCheckBox(label)
            box.setChecked(kind in DEFAULT_KINDS)
            box.stateChanged.connect(self._refresh)

            self.kind_boxes[kind] = box
            layout.addWidget(box)

        population_row = QHBoxLayout()
        layout.addLayout(population_row)

        population_row.addWidget(QLabel("Mindestens Einwohner:"))

        self.population_spin = QSpinBox()
        self.population_spin.setRange(0, 10_000_000)
        self.population_spin.setSingleStep(500)
        self.population_spin.setMinimumWidth(130)
        self.population_spin.valueChanged.connect(self._refresh)
        population_row.addWidget(self.population_spin)

        population_row.addStretch(1)

        self.size_checkbox = QCheckBox(
            "Größe aus der OSM-Einwohnerzahl ableiten"
        )
        self.size_checkbox.setChecked(True)
        self.size_checkbox.stateChanged.connect(self._refresh)
        layout.addWidget(self.size_checkbox)

        scale_row = QHBoxLayout()
        layout.addLayout(scale_row)

        scale_row.addWidget(QLabel("Maßstab:"))

        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.01, 1.0)
        self.scale_spin.setSingleStep(0.01)
        self.scale_spin.setDecimals(2)
        self.scale_spin.setValue(DEFAULT_SCALE)
        self.scale_spin.setMinimumWidth(130)
        self.scale_spin.setToolTip(
            "Faktor = Maßstab × Wurzel(Einwohner). Bei 0,03 bekommt "
            "Koblenz (110 000) etwa Faktor 10, ein Dorf mit 300 etwa 0,5."
        )
        self.scale_spin.valueChanged.connect(self._refresh)
        scale_row.addWidget(self.scale_spin)

        scale_row.addStretch(1)

        min_row = QHBoxLayout()
        layout.addLayout(min_row)

        min_row.addWidget(QLabel("Kleinster Faktor:"))

        self.min_factor_spin = QDoubleSpinBox()
        self.min_factor_spin.setRange(0.2, 1.0)
        self.min_factor_spin.setSingleStep(0.1)
        self.min_factor_spin.setDecimals(1)
        self.min_factor_spin.setValue(DEFAULT_MIN_FACTOR)
        self.min_factor_spin.setMinimumWidth(130)
        self.min_factor_spin.setToolTip(
            "Faktor 1 sind etwa 100 Einwohner. Getestet: 0,2 gibt etwa 19 "
            "Einwohner. Werte darunter sind ungeprüft."
        )
        self.min_factor_spin.valueChanged.connect(self._refresh)
        min_row.addWidget(self.min_factor_spin)

        min_row.addStretch(1)

        factor_row = QHBoxLayout()
        layout.addLayout(factor_row)

        factor_row.addWidget(QLabel("Größter Faktor:"))

        self.max_factor_spin = QSpinBox()
        self.max_factor_spin.setRange(1, 100)
        self.max_factor_spin.setValue(int(DEFAULT_MAX_FACTOR))
        self.max_factor_spin.setMinimumWidth(130)
        self.max_factor_spin.setToolTip(
            "Faktor 30 ergab im Test 2892 Einwohner, Faktor 100 nur 4476. "
            "Höher als 30 ist ungetestet."
        )
        self.max_factor_spin.valueChanged.connect(self._refresh)
        factor_row.addWidget(self.max_factor_spin)

        factor_row.addStretch(1)

        self.list_widget = QListWidget()
        self.list_widget.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.list_widget)

        select_row = QHBoxLayout()
        layout.addLayout(select_row)

        all_button = QPushButton("Alle auswählen")
        all_button.clicked.connect(lambda: self._set_all(True))
        select_row.addWidget(all_button)

        none_button = QPushButton("Keine auswählen")
        none_button.clicked.connect(lambda: self._set_all(False))
        select_row.addWidget(none_button)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        row = QHBoxLayout()
        layout.addLayout(row)

        self.export_button = QPushButton("Exportieren...")
        self.export_button.clicked.connect(self._export)
        row.addWidget(self.export_button)

        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.reject)
        row.addWidget(close_button)

        self._refresh()

    # ---------------------------------------------------------

    def _kinds(self) -> list[str]:

        return [k for k, box in self.kind_boxes.items() if box.isChecked()]

    def _refresh(self, *_args):

        self._places = collect_places(
            self.osm,
            self.selection,
            kinds=self._kinds(),
            min_population=self.population_spin.value(),
        )

        self.list_widget.blockSignals(True)
        self.list_widget.clear()

        for place in self._places:

            population = (
                f", {place.population} Einwohner" if place.population else ""
            )

            factor = size_factor(
                place,
                self.max_factor_spin.value(),
                self.size_checkbox.isChecked(),
                self.scale_spin.value(),
                self.min_factor_spin.value(),
            )

            item = QListWidgetItem(
                f"{place.name} ({place.kind}{population})  "
                f"Faktor {factor:g}  "
                f"x {place.x:.0f} m, y {place.y:.0f} m"
            )
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(
                Qt.Unchecked
                if self._key(place) in self._unchecked
                else Qt.Checked
            )

            self.list_widget.addItem(item)

        self.list_widget.blockSignals(False)

        if self._places:
            self._update_status()
        else:
            self.status_label.setText(
                "Keine Orte gefunden. Entweder enthalten die geladenen "
                "OSM-Daten keine Ortsknoten (die Overpass-Abfrage muss "
                "place=city/town/village mitladen) oder der Filter ist zu "
                "streng."
            )

        self.export_button.setEnabled(bool(self._selected_places()))

    @staticmethod
    def _key(place) -> tuple:
        return (place.name, round(place.x), round(place.y))

    def _selected_places(self) -> list:
        """Orte, deren Haken in der Liste gesetzt ist."""

        selected = []

        for row, place in enumerate(self._places):
            item = self.list_widget.item(row)
            if item is not None and item.checkState() == Qt.Checked:
                selected.append(place)

        return selected

    def _update_status(self):

        chosen = len(self._selected_places())

        self.status_label.setText(
            f"{len(self._places)} Orte gefunden, {chosen} ausgewählt. "
            "Nur die angehakten Orte werden exportiert."
        )

        self.export_button.setEnabled(chosen > 0)

    def _on_item_changed(self, item):

        row = self.list_widget.row(item)

        if 0 <= row < len(self._places):
            key = self._key(self._places[row])

            if item.checkState() == Qt.Checked:
                self._unchecked.discard(key)
            else:
                self._unchecked.add(key)

        self._update_status()

    def _set_all(self, checked: bool):

        self.list_widget.blockSignals(True)

        for row, place in enumerate(self._places):
            item = self.list_widget.item(row)
            if item is None:
                continue
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
            key = self._key(place)
            if checked:
                self._unchecked.discard(key)
            else:
                self._unchecked.add(key)

        self.list_widget.blockSignals(False)

        self._update_status()

    def _default_folder(self) -> Path:

        heightmaps = find_tpf3_heightmaps_folder()

        if heightmaps is not None:
            folder = heightmaps.parent / "towns_industries"
            return folder if folder.is_dir() else heightmaps

        return Path.home()

    def _export(self):

        places = self._selected_places()

        if not places:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Städte speichern",
            str(self._default_folder() / "staedte_osm.lua"),
            "Lua (*.lua)",
        )

        if not path:
            return

        try:
            write_towns_lua(
                path,
                places,
                self.max_factor_spin.value(),
                self.size_checkbox.isChecked(),
                self.scale_spin.value(),
                self.min_factor_spin.value(),
            )
        except OSError as error:
            QMessageBox.warning(
                self,
                "Städte aus OSM",
                f"Die Datei konnte nicht gespeichert werden:\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "Städte aus OSM",
            f"Gespeichert ({len(places)} Städte):\n{path}\n\n"
            "Im Spiel: Karteneditor → Reiter Städte/Industrien → Import → "
            "diese Datei wählen → Import.",
        )
