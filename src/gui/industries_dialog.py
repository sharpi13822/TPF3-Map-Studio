"""
Dialog "Industrien aus OSM": erzeugt aus den geladenen OSM-Objekten
(Bauernhoefe, Steinbrueche, Saegewerke, Ziegeleien, ...) eine Lua-Datei fuer
den Ordner towns_industries. Die Datei enthaelt nur Industrien; beim Import
im Spiel "Staedte behalten: Ja" waehlen.

Die Zuordnung OSM-Objekt -> Industrie ist ein Vorschlag. Ob das Spiel jede
Position annimmt, ist ungeprueft.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from src.heightmap.industries_export import (
    RULES,
    collect_industries,
    write_industries_lua,
)
from src.heightmap.tpf3_paths import find_tpf3_heightmaps_folder


class IndustriesDialog(QDialog):

    def __init__(self, parent, selection, osm, terrain=None):
        super().__init__(parent)

        self.selection = selection
        self.osm = osm
        self.terrain = terrain
        self._items = []
        self._unchecked: set[tuple] = set()

        self.setWindowTitle("Industrien aus OSM")
        self.setMinimumWidth(640)
        self.resize(720, 820)

        layout = QVBoxLayout(self)

        info = QLabel(
            "Erzeugt aus den geladenen OSM-Objekten eine Industrien-Datei "
            "für den Ordner towns_industries. Der Nullpunkt ist die "
            "Kartenmitte. Im Spiel beim Import \"Städte behalten: Ja\" "
            "wählen, die Datei enthält keine Städte. Die Zuordnung ist ein "
            "Vorschlag, ob das Spiel jede Position annimmt, ist ungeprüft."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        self.rule_boxes: dict[str, QCheckBox] = {}

        rules_grid = QGridLayout()
        layout.addLayout(rules_grid)

        for index, rule in enumerate(RULES):

            box = QCheckBox(rule.label)
            box.setChecked(rule.default_on)
            box.stateChanged.connect(self._refresh)

            self.rule_boxes[rule.key] = box
            rules_grid.addWidget(box, index // 2, index % 2)

        self.forest_spin = QDoubleSpinBox()
        self.forest_spin.setRange(10.0, 100000.0)
        self.forest_spin.setDecimals(0)
        self.forest_spin.setSingleStep(50.0)
        self.forest_spin.setValue(200.0)
        self.forest_spin.setSuffix(" ha")
        self.forest_spin.setMinimumWidth(130)
        self.forest_spin.valueChanged.connect(self._refresh)
        layout.addLayout(self._row("Forst ab Größe:", self.forest_spin))

        self.distance_spin = QSpinBox()
        self.distance_spin.setRange(0, 20000)
        self.distance_spin.setSingleStep(100)
        self.distance_spin.setValue(800)
        self.distance_spin.setSuffix(" m")
        self.distance_spin.setMinimumWidth(130)
        self.distance_spin.setToolTip(
            "Gleichartige Industrien müssen mindestens so weit auseinander "
            "liegen."
        )
        self.distance_spin.valueChanged.connect(self._refresh)
        layout.addLayout(
            self._row("Mindestabstand je Art:", self.distance_spin)
        )

        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 500)
        self.max_spin.setValue(20)
        self.max_spin.setMinimumWidth(130)
        self.max_spin.setToolTip(
            "Höchstens so viele Industrien je Art, die größten zuerst."
        )
        self.max_spin.valueChanged.connect(self._refresh)
        layout.addLayout(self._row("Höchstens je Art:", self.max_spin))

        self.relief_spin = QSpinBox()
        self.relief_spin.setRange(0, 200)
        self.relief_spin.setValue(15)
        self.relief_spin.setSuffix(" m")
        self.relief_spin.setMinimumWidth(130)
        self.relief_spin.setToolTip(
            "Höchster Höhenunterschied im Umkreis von 150 m. Industrien auf "
            "steileren Hängen werden aussortiert. 0 = nicht prüfen."
        )
        self.relief_spin.valueChanged.connect(self._refresh)
        layout.addLayout(
            self._row("Höchster Höhenunterschied (150 m):", self.relief_spin)
        )

        self.water_spin = QSpinBox()
        self.water_spin.setRange(0, 1000)
        self.water_spin.setSingleStep(50)
        self.water_spin.setValue(150)
        self.water_spin.setSuffix(" m")
        self.water_spin.setMinimumWidth(130)
        self.water_spin.setToolTip(
            "Mindestabstand zu Gewässern. 0 = nicht prüfen."
        )
        self.water_spin.valueChanged.connect(self._refresh)
        layout.addLayout(self._row("Abstand zu Wasser:", self.water_spin))

        if self.terrain is None:
            note = QLabel(
                "Hinweis: Es sind keine Höhendaten geladen. Hang- und "
                "Wasserprüfung sind aus. Zuerst im Heightmap-Dialog die "
                "Höhendaten herunterladen."
            )
            note.setWordWrap(True)
            layout.addWidget(note)
            self.relief_spin.setEnabled(False)
            self.water_spin.setEnabled(False)

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

    @staticmethod
    def _row(label: str, widget) -> QHBoxLayout:

        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        row.addWidget(widget)
        row.addStretch(1)

        return row

    @staticmethod
    def _key(item) -> tuple:
        return (item.key, round(item.x), round(item.y))

    def _enabled(self) -> list[str]:

        return [k for k, box in self.rule_boxes.items() if box.isChecked()]

    def _refresh(self, *_args):

        self._items = collect_industries(
            self.osm,
            self.selection,
            enabled=self._enabled(),
            min_forest_ha=self.forest_spin.value(),
            min_distance_m=self.distance_spin.value(),
            max_per_type=self.max_spin.value(),
            terrain=self.terrain,
            max_relief_m=self.relief_spin.value(),
            water_clear_m=self.water_spin.value(),
        )

        self.list_widget.blockSignals(True)
        self.list_widget.clear()

        for item in self._items:

            size = f", {item.area_ha:.0f} ha" if item.area_ha else ""

            entry = QListWidgetItem(
                f"{item.key}: {item.name}{size}  "
                f"x {item.x:.0f} m, y {item.y:.0f} m"
            )
            entry.setFlags(entry.flags() | Qt.ItemIsUserCheckable)
            entry.setCheckState(
                Qt.Unchecked
                if self._key(item) in self._unchecked
                else Qt.Checked
            )

            self.list_widget.addItem(entry)

        self.list_widget.blockSignals(False)

        self._update_status()

    def _selected(self) -> list:

        chosen = []

        for row, item in enumerate(self._items):
            entry = self.list_widget.item(row)
            if entry is not None and entry.checkState() == Qt.Checked:
                chosen.append(item)

        return chosen

    def _update_status(self):

        chosen = len(self._selected())

        if self._items:
            self.status_label.setText(
                f"{len(self._items)} Objekte gefunden, {chosen} "
                "ausgewählt. Nur die angehakten werden exportiert."
            )
        else:
            self.status_label.setText(
                "Keine passenden Objekte gefunden. Entweder fehlen sie in "
                "den geladenen OSM-Daten (im Overpass-Baukasten den Haken "
                "\"Industrie-Objekte\" und für Steinbrüche \"Siedlung, "
                "Heide, Moor, Fels\" setzen, dann neu laden) oder die "
                "Filter sind zu streng."
            )

        self.export_button.setEnabled(chosen > 0)

    def _on_item_changed(self, entry):

        row = self.list_widget.row(entry)

        if 0 <= row < len(self._items):
            key = self._key(self._items[row])

            if entry.checkState() == Qt.Checked:
                self._unchecked.discard(key)
            else:
                self._unchecked.add(key)

        self._update_status()

    def _set_all(self, checked: bool):

        self.list_widget.blockSignals(True)

        for row, item in enumerate(self._items):
            entry = self.list_widget.item(row)
            if entry is None:
                continue
            entry.setCheckState(Qt.Checked if checked else Qt.Unchecked)
            key = self._key(item)
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

        items = self._selected()

        if not items:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Industrien speichern",
            str(self._default_folder() / "industrien_osm.lua"),
            "Lua (*.lua)",
        )

        if not path:
            return

        try:
            write_industries_lua(path, items)
        except OSError as error:
            QMessageBox.warning(
                self,
                "Industrien aus OSM",
                f"Die Datei konnte nicht gespeichert werden:\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "Industrien aus OSM",
            f"Gespeichert ({len(items)} Industrien):\n{path}\n\n"
            "Im Spiel: Karteneditor → Reiter Städte/Industrien → Import → "
            "diese Datei wählen, \"Städte behalten\" auf Ja, "
            "\"Industrien behalten\" auf Nein → Import.",
        )
