from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QCheckBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QFileDialog,
    QMessageBox,
    QDialogButtonBox,
)

from src.osm.short_edge_simplifier import (
    DEFAULT_LINK_TYPES,
    DEFAULT_THRESHOLD_M,
    analyze_short_segments,
    simplify_short_segments,
)
from src.export.osm_xml_exporter import export_osm_xml
from src.features import VACUUMTUBE_IMPORTER


LINK_TYPE_LABELS = (
    ("motorway_link", "Autobahn-Ab-/Auffahrten"),
    ("trunk_link", "Schnellstraßen-Ab-/Auffahrten"),
    ("primary_link", "Bundesstraßen-Verbindungen"),
    ("secondary_link", "Landstraßen-Verbindungen"),
    ("tertiary_link", "Kreisstraßen-Verbindungen"),
)


class ShortSegmentDialog(QDialog):
    """
    Analysiert sehr kurze Wegsegmente bei _link-Typen (Ab-/Auffahrten)
    und bietet eine SICHERE Vereinfachung an (siehe
    src/osm/short_edge_simplifier.py für die Sicherheitsgarantien -
    echte Kreuzungen werden nie verändert).

    Hintergrund: Eine echte Analyse zeigte, dass fehlgeschlagene
    secondary_link-Kanten im Median ~6.9m lang waren, erfolgreiche
    ~23.1m. Das ist eine Korrelation, kein bewiesener Kausalzusammenhang -
    dieser Dialog macht das transparent, statt eine Garantie zu geben.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.last_report = None

        self.setWindowTitle("Kurze Verbindungssegmente")
        self.setMinimumSize(720, 560)

        layout = QVBoxLayout(self)

        intro = QLabel(
            "Prüft, ob sehr kurze Segmente bei Ab-/Auffahrten-Straßentypen "
            "vorkommen. Eine Analyse eines echten Baulaufs zeigte: "
            "fehlgeschlagene secondary_link-Kanten waren im Median ~6,9 m "
            "lang, erfolgreiche ~23,1 m - das ist eine beobachtete "
            "Korrelation, kein bewiesener Grund. Die Vereinfachung entfernt "
            "ausschließlich Formpunkte, die garantiert zu keiner echten "
            "Kreuzung gehören - Kreuzungen bleiben immer unangetastet."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        # -------------------------------------------------
        # Einstellungen
        # -------------------------------------------------

        settings_row = QHBoxLayout()

        settings_row.addWidget(QLabel("Schwellenwert:"))

        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setRange(1.0, 200.0)
        self.threshold_input.setValue(DEFAULT_THRESHOLD_M)
        self.threshold_input.setSuffix(" m")
        settings_row.addWidget(self.threshold_input)

        settings_row.addStretch()

        layout.addLayout(settings_row)

        self.link_type_checkboxes: dict[str, QCheckBox] = {}

        types_row = QHBoxLayout()

        for key, label in LINK_TYPE_LABELS:

            checkbox = QCheckBox(label)
            checkbox.setChecked(key in DEFAULT_LINK_TYPES)

            self.link_type_checkboxes[key] = checkbox

            types_row.addWidget(checkbox)

        layout.addLayout(types_row)

        analyze_button = QPushButton("Analysieren")
        analyze_button.clicked.connect(self._analyze)
        layout.addWidget(analyze_button)

        # -------------------------------------------------
        # Ergebnis
        # -------------------------------------------------

        self.summary_label = QLabel("Noch nicht analysiert.")
        layout.addWidget(self.summary_label)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Weg-ID", "Typ", "Länge"])
        layout.addWidget(self.tree)

        # Der .osm-Export gehoert zum Importer von VacuumTube (src/features.py).
        if VACUUMTUBE_IMPORTER:

            export_button = QPushButton(
                "Vereinfacht als .osm exportieren..."
            )
            export_button.clicked.connect(self._export_simplified)
            layout.addWidget(export_button)

        # -------------------------------------------------
        # Schließen
        # -------------------------------------------------

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    # ---------------------------------------------------------
    # Analyse
    # ---------------------------------------------------------

    def _selected_link_types(self) -> frozenset[str]:

        return frozenset(
            key
            for key, checkbox in self.link_type_checkboxes.items()
            if checkbox.isChecked()
        )

    def _analyze(self):

        osm = self.controller.project.osm

        if osm.node_count == 0 and osm.way_count == 0:

            QMessageBox.warning(
                self,
                "Keine OSM-Daten",
                "Es sind keine OSM-Daten geladen. Zuerst 'OSM laden' "
                "ausführen."
            )

            return

        link_types = self._selected_link_types()

        if not link_types:

            QMessageBox.warning(
                self,
                "Keine Kategorie ausgewählt",
                "Mindestens einen Straßentyp auswählen."
            )

            return

        self.last_report = analyze_short_segments(
            osm,
            link_types=link_types,
            threshold_m=self.threshold_input.value(),
        )

        self.summary_label.setText(
            f"{len(self.last_report.short_segments)} kurze Segmente in "
            f"{len(self.last_report.affected_way_ids)} Wegen gefunden. "
            f"{len(self.last_report.removable_nodes)} Formpunkte könnten "
            f"sicher entfernt werden (keine Kreuzungen darunter)."
        )

        self.tree.clear()

        segments_sorted = sorted(
            self.last_report.short_segments,
            key=lambda s: s.length_m,
        )

        for segment in segments_sorted:

            item = QTreeWidgetItem([
                str(segment.way_id),
                segment.highway_type,
                f"{segment.length_m:.1f} m",
            ])

            self.tree.addTopLevelItem(item)

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def _export_simplified(self):

        if self.last_report is None:

            QMessageBox.warning(
                self,
                "Noch nicht analysiert",
                "Zuerst auf 'Analysieren' klicken."
            )

            return

        if not self.last_report.removable_nodes:

            QMessageBox.information(
                self,
                "Nichts zu vereinfachen",
                "Keine sicher entfernbaren Formpunkte gefunden."
            )

            return

        osm = self.controller.project.osm

        simplified = simplify_short_segments(
            osm,
            self.last_report.removable_nodes,
        )

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Vereinfachte OSM-Datei exportieren",
            "map_simplified.osm",
            "OSM-Dateien (*.osm)"
        )

        if not filename:
            return

        selection = self.controller.project.selection

        bounds = None

        if selection is not None:

            bounds = (
                selection.min_lat,
                selection.min_lon,
                selection.max_lat,
                selection.max_lon,
            )

        try:
            export_osm_xml(
                simplified,
                Path(filename),
                bounds=bounds,
            )
        except Exception as exc:

            QMessageBox.critical(
                self,
                "Export fehlgeschlagen",
                str(exc)
            )

            return

        QMessageBox.information(
            self,
            "Export abgeschlossen",
            f"Vereinfachte OSM-Datei gespeichert unter:\n{filename}\n\n"
            f"{len(self.last_report.removable_nodes)} Formpunkte entfernt "
            f"(nur nicht-Kreuzungs-Knoten). Das ursprüngliche Projekt im "
            f"Studio ist unverändert."
        )
