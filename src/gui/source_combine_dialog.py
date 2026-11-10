"""Dialog: weitere Hoehenquellen zur gewaehlten Quelle dazunehmen (Vorrang per Pfeilen)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from src.heightmap.heightmap_exporter import (
    SOURCE_AHN_NL,
    SOURCE_BEV_AT,
    SOURCE_COPERNICUS,
    SOURCE_DGM1_DE,
    SOURCE_DGM1_FOLDER,
    SOURCE_LUX,
    SOURCE_SWISSALTI3D,
)
from src.heightmap.source_combine import (
    DEFAULT_BLEND_M,
    MAX_SOURCES,
    source_bounds,
    source_name,
    touches,
)
from src.i18n import tr

# Quellen, die sich kombinieren lassen (die eigene TPF2-PNG nicht)
COMBINABLE = (
    SOURCE_DGM1_DE,
    SOURCE_LUX,
    SOURCE_BEV_AT,
    SOURCE_SWISSALTI3D,
    SOURCE_AHN_NL,
    SOURCE_DGM1_FOLDER,
    SOURCE_COPERNICUS,
)


def offered_sources(main_source, corners, has_folder: bool) -> list[str]:
    """Quellen, die der Dialog zusaetzlich anbietet (ohne die Hauptquelle)."""

    result = []

    for source in COMBINABLE:
        if source == main_source:
            continue
        if source == SOURCE_DGM1_FOLDER and not has_folder:
            continue
        if not touches(corners, source_bounds(source)):
            continue
        result.append(source)

    return result


class SourceCombineDialog(QDialog):

    def __init__(self, parent, main_source, offered, chosen, blend_m=DEFAULT_BLEND_M):
        super().__init__(parent)

        self.setWindowTitle(tr("Höhenquellen kombinieren"))

        layout = QVBoxLayout(self)

        note = QLabel(
            tr(
                "Hauptquelle: {name}. Hake bis zu zwei weitere Quellen an. Für jeden Punkt "
                "gilt die oberste Quelle mit Daten, wo sie endet, übernimmt die nächste. "
                "Mit den Pfeilen änderst du die Reihenfolge. Copernicus steht immer an letzter "
                "Stelle und füllt nur Lücken."
            ).format(name=source_name(main_source))
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        row = QHBoxLayout()

        self.list = QListWidget()
        order = [s for s in chosen if s in offered] + [s for s in offered if s not in chosen]

        for source in order:
            item = QListWidgetItem(source_name(source))
            item.setData(Qt.UserRole, source)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if source in chosen else Qt.Unchecked)
            self.list.addItem(item)

        self.list.itemChanged.connect(self._limit_checks)
        row.addWidget(self.list, 1)

        arrows = QVBoxLayout()
        up = QPushButton("↑")
        down = QPushButton("↓")
        up.setToolTip(tr("Nach oben (mehr Vorrang)"))
        down.setToolTip(tr("Nach unten (weniger Vorrang)"))
        up.clicked.connect(lambda: self._move(-1))
        down.clicked.connect(lambda: self._move(1))
        arrows.addWidget(up)
        arrows.addWidget(down)
        arrows.addStretch(1)
        row.addLayout(arrows)

        layout.addLayout(row)

        blend_row = QHBoxLayout()
        blend_row.addWidget(QLabel(tr("Weiche Naht an der Grenze:")))
        self.blend_spin = QSpinBox()
        self.blend_spin.setRange(0, 1000)
        self.blend_spin.setSingleStep(25)
        self.blend_spin.setSuffix(" m")
        self.blend_spin.setValue(int(round(blend_m)))
        self.blend_spin.setToolTip(
            tr("Auf dieser Breite wird an der Grenze von einer Quelle in die nächste übergeblendet. "
               "0 m = harte Kante. Ein fester Höhenversatz zwischen den Quellen wird immer ausgeglichen.")
        )
        blend_row.addWidget(self.blend_spin)
        blend_row.addStretch(1)
        layout.addLayout(blend_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _move(self, step: int):
        row = self.list.currentRow()
        target = row + step

        if row < 0 or not (0 <= target < self.list.count()):
            return

        item = self.list.takeItem(row)
        self.list.insertItem(target, item)
        self.list.setCurrentRow(target)

    def _limit_checks(self, changed):
        if changed.checkState() != Qt.Checked:
            return

        if len(self.chosen_sources()) > MAX_SOURCES - 1:
            self.list.blockSignals(True)
            changed.setCheckState(Qt.Unchecked)
            self.list.blockSignals(False)

    def chosen_sources(self) -> list[str]:
        result = []

        for row in range(self.list.count()):
            item = self.list.item(row)
            if item.checkState() == Qt.Checked:
                result.append(item.data(Qt.UserRole))

        return result

    def blend_m(self) -> float:
        return float(self.blend_spin.value())
