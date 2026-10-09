"""
Dialog "Strassen und Gleise fuer das Spiel": erzeugt aus den geladenen
OSM-Wegen den Mod "Map Studio Import" fuer Transport Fever 3.

Der Mod liegt danach im Ordner mods des Spiels. Im Spiel baut er das Netz auf
Knopfdruck (Konsolenbefehl) auf die geladene Heightmap.

Im Spiel getestet ist der Mod mit einem Testnetz (Strassen, Gleise, Kreuzung,
Bruecke, Tunnel, Gitter mit 264 Wegen). Der Export aus echten OSM-Daten und
die Zuordnung OSM-Typ -> Strassenvorlage sind noch nicht im Spiel geprueft.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.heightmap.station_export import (
    collect_stations,
    summary as station_summary,
    write_stations,
)
from src.heightmap.network_export import (
    DEFAULT_HIGHWAYS,
    HIGHWAY_TEMPLATES,
    NetworkOptions,
    collect_network,
    find_tpf3_mods_folder,
    summary_text,
    write_mod,
)
from src.i18n import tr

HIGHWAY_LABELS = {
    "motorway": tr("Autobahn (motorway)"),
    "motorway_link": tr("Autobahn-Auffahrten (motorway_link)"),
    "trunk": tr("Schnellstraße (trunk)"),
    "trunk_link": tr("Schnellstraßen-Auffahrten (trunk_link)"),
    "primary": tr("Bundesstraße (primary)"),
    "primary_link": tr("Bundesstraßen-Auffahrten (primary_link)"),
    "secondary": tr("Landesstraße (secondary)"),
    "secondary_link": tr("Landesstraßen-Auffahrten (secondary_link)"),
    "tertiary": tr("Kreisstraße (tertiary)"),
    "tertiary_link": tr("Kreisstraßen-Auffahrten (tertiary_link)"),
    "unclassified": tr("Nebenstraße (unclassified)"),
    "residential": tr("Wohnstraße (residential)"),
    "living_street": tr("Verkehrsberuhigt (living_street)"),
    "service": tr("Zufahrten und Wirtschaftswege (service)"),
}

START_COMMAND = (
    'api.cmd.sendCommand(api.cmd.makeScriptingSendEventCmd('
    '"", "mapstudio", "import", true))'
)


class NetworkDialog(QDialog):

    def __init__(self, parent, selection, osm):
        super().__init__(parent)

        self.selection = selection
        self.osm = osm
        self._network = None

        self.setWindowTitle(tr("Straßen und Gleise für das Spiel"))
        self.setMinimumWidth(560)

        layout = QVBoxLayout(self)

        info = QLabel(
            tr("Erzeugt aus den geladenen OSM-Wegen einen Mod für Transport "
            "Fever 3. Der Mod baut im Spiel Straßen, Gleise, Brücken und "
            "Tunnel auf die geladene Heightmap. Die Höhen der Strecken plant "
            "der Mod selbst (aus dem Gelände, mit Steigungsgrenze). "
            "Nullpunkt ist die Kartenmitte, wie bei den Städten.")
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # --- Strassen ---------------------------------------------------
        street_group = QGroupBox(tr("Straßen"))
        street_layout = QVBoxLayout(street_group)

        self.highway_boxes: dict[str, QCheckBox] = {}

        for key in HIGHWAY_TEMPLATES:

            box = QCheckBox(HIGHWAY_LABELS.get(key, key))
            box.setChecked(key in DEFAULT_HIGHWAYS)
            box.stateChanged.connect(self._invalidate)

            self.highway_boxes[key] = box
            street_layout.addWidget(box)

        self.main_only_button = QPushButton(tr("Nur Hauptstrecken (ohne Wohn- und Nebenstraßen)"))
        self.main_only_button.setToolTip(
            tr("Nimmt die Haken bei Wohnstraße, Verkehrsberuhigt, Nebenstraße und Zufahrten heraus. "
            "Für einen ersten Test sinnvoll: weniger Wege, weniger Überschneidungen.")
        )
        self.main_only_button.clicked.connect(self._nur_hauptstrecken)
        street_layout.addWidget(self.main_only_button)

        layout.addWidget(street_group)

        # --- Gleise -----------------------------------------------------
        rail_group = QGroupBox(tr("Gleise"))
        rail_layout = QVBoxLayout(rail_group)

        self.rail_box = QCheckBox(tr("Eisenbahn (rail)"))
        self.rail_box.setChecked(True)
        self.light_rail_box = QCheckBox(tr("S-Bahn (light_rail)"))
        self.light_rail_box.setChecked(True)
        self.tram_box = QCheckBox(tr("Straßenbahn (tram) – im Spiel noch ungetestet"))
        self.tram_box.setChecked(False)

        for box in (self.rail_box, self.light_rail_box, self.tram_box):
            box.stateChanged.connect(self._invalidate)
            rail_layout.addWidget(box)

        layout.addWidget(rail_group)

        # --- Bruecken / Tunnel -------------------------------------------
        self.bridge_box = QCheckBox(tr("Brücken bauen (bridge=*)"))
        self.bridge_box.setChecked(True)
        self.bridge_box.stateChanged.connect(self._invalidate)
        layout.addWidget(self.bridge_box)

        self.tunnel_box = QCheckBox(tr("Tunnel bauen (tunnel=yes)"))
        self.tunnel_box.setChecked(True)
        self.tunnel_box.stateChanged.connect(self._invalidate)
        layout.addWidget(self.tunnel_box)

        self.oneway_box = QCheckBox(
            tr("Einbahnstraßen mit schmaler Einbahn-Vorlage bauen (empfohlen)")
        )
        self.oneway_box.setChecked(True)
        self.oneway_box.setToolTip(
            tr("Parallele Richtungsfahrbahnen (je ein OSM-Weg mit oneway=yes) "
            "würden sich sonst als zwei zweispurige Straßen überlagern. "
            "Autobahnen bleiben unverändert (es gibt keine Einbahn-Vorlage dafür).")
        )
        self.oneway_box.stateChanged.connect(self._invalidate)
        layout.addWidget(self.oneway_box)

        self.dual_box = QCheckBox(tr("Richtungsfahrbahnen zusammenfassen (im Spiel ungetestet)"))
        self.dual_box.setChecked(False)
        self.dual_box.setToolTip(
            tr("Zwei parallele Einbahn-Wege gegenläufiger Richtung werden zu einem "
            "zweispurigen Weg in der Mitte. Autobahnen bleiben unverändert.")
        )
        self.dual_box.stateChanged.connect(self._invalidate)
        layout.addWidget(self.dual_box)

        self.dedupe_box = QCheckBox(tr("Doppelt gezeichnete Gleise entfernen (im Spiel ungetestet)"))
        self.dedupe_box.setChecked(False)
        self.dedupe_box.setToolTip(
            tr("Gleise, die fast deckungsgleich auf einem anderen Gleis liegen "
            "(z. B. Servicegleis auf der Hauptstrecke), entfallen.")
        )
        self.dedupe_box.stateChanged.connect(self._invalidate)
        layout.addWidget(self.dedupe_box)

        # --- Vereinfachung -----------------------------------------------
        form = QFormLayout()
        layout.addLayout(form)

        self.tolerance_spin = QDoubleSpinBox()
        self.tolerance_spin.setRange(0.0, 50.0)
        self.tolerance_spin.setDecimals(1)
        self.tolerance_spin.setSingleStep(0.5)
        self.tolerance_spin.setValue(NetworkOptions.simplify_tolerance_m)
        self.tolerance_spin.setSuffix(" m")
        self.tolerance_spin.setToolTip(
            tr("Formpunkte, die die Linie um weniger als diesen Wert verändern, "
            "entfallen. Kreuzungen und Wegenden bleiben immer. Weniger Punkte "
            "bedeuten ein kleineres Netz im Spiel.")
        )
        self.tolerance_spin.valueChanged.connect(self._invalidate)
        form.addRow(tr("Vereinfachen bis:"), self.tolerance_spin)

        self.min_segment_spin = QDoubleSpinBox()
        self.min_segment_spin.setRange(0.0, 100.0)
        self.min_segment_spin.setDecimals(1)
        self.min_segment_spin.setSingleStep(1.0)
        self.min_segment_spin.setValue(NetworkOptions.min_segment_m)
        self.min_segment_spin.setSuffix(" m")
        self.min_segment_spin.setToolTip(
            tr("Formpunkte, die näher als dieser Wert am Nachbarn liegen, "
            "entfallen. Sehr kurze Kanten sind in TPF2 oft gescheitert.")
        )
        self.min_segment_spin.valueChanged.connect(self._invalidate)
        form.addRow(tr("Kleinster Punktabstand:"), self.min_segment_spin)

        self.min_bridge_spin = QDoubleSpinBox()
        self.min_bridge_spin.setRange(0.0, 500.0)
        self.min_bridge_spin.setDecimals(0)
        self.min_bridge_spin.setSingleStep(5.0)
        self.min_bridge_spin.setValue(NetworkOptions.min_bridge_m)
        self.min_bridge_spin.setSuffix(" m")
        self.min_bridge_spin.setToolTip(
            tr("Brücken, die kürzer sind, werden als gewöhnliche Straße oder "
            "gewöhnliches Gleis gebaut. Im Spiel scheiterten alle Gleisbrücken "
            "zwischen 4 und 20 m Länge.")
        )
        self.min_bridge_spin.valueChanged.connect(self._invalidate)
        form.addRow(tr("Kürzeste Brücke:"), self.min_bridge_spin)

        self.edge_spin = QDoubleSpinBox()
        self.edge_spin.setRange(0.0, 500.0)
        self.edge_spin.setDecimals(0)
        self.edge_spin.setSingleStep(10.0)
        self.edge_spin.setValue(NetworkOptions.max_edge_m)
        self.edge_spin.setSuffix(" m")
        self.edge_spin.setToolTip(
            tr("Auf längeren Kanten werden Knoten eingefügt (auf der Linie). Zwischen zwei "
            "Knoten verläuft die Höhe im Spiel geradlinig; bei Kanten von mehreren hundert "
            "Metern schweben die Gleise über dem Hang oder stecken im Einschnitt. "
            "80 m passt zur Gleisterrasse der Heightmap. 0 = aus.")
        )
        self.edge_spin.valueChanged.connect(self._invalidate)
        form.addRow(tr("Größter Knotenabstand:"), self.edge_spin)

        self.road_gap_spin = QDoubleSpinBox()
        self.road_gap_spin.setRange(0.0, 20.0)
        self.road_gap_spin.setDecimals(0)
        self.road_gap_spin.setSingleStep(1.0)
        self.road_gap_spin.setValue(NetworkOptions.min_road_track_m)
        self.road_gap_spin.setSuffix(" m")
        self.road_gap_spin.setToolTip(
            tr("Mindestabstand zwischen Straße und Gleis (Mittellinie zu Mittellinie). Die Straße ist 14 m "
            "breit, das Gleis mit Masten rund 7 m. Standard 9 m: Die Ränder berühren sich nicht, die Straße "
            "bleibt nah an ihrer OSM-Lage, aber es bleibt kein freier Streifen dazwischen (dort geht im Spiel "
            "weder Gelände anheben noch Pflanzen setzen). 14 m lassen rund 3,5 m frei, verschieben die "
            "Straße aber bis zu 5 m von ihrer Lage. Übergänge und kreuzende Straßen bleiben. 0 = aus.")
        )
        self.road_gap_spin.valueChanged.connect(self._invalidate)
        form.addRow(tr("Mindestabstand Straße–Gleis:"), self.road_gap_spin)

        self.merge_spin = QDoubleSpinBox()
        self.merge_spin.setRange(0.0, 30.0)
        self.merge_spin.setDecimals(0)
        self.merge_spin.setSingleStep(2.0)
        self.merge_spin.setValue(NetworkOptions.merge_junctions_m)
        self.merge_spin.setSuffix(" m")
        self.merge_spin.setToolTip(
            tr("Einmündungen und Wegenden, die näher beieinander liegen, werden zu einem Knoten. "
            "Die Straßen im Spiel sind 14 bis 30 m breit, dichter liegende Einmündungen lassen "
            "sich dort nicht bauen. 0 = aus. Im Spiel noch nicht getestet.")
        )
        self.merge_spin.valueChanged.connect(self._invalidate)
        form.addRow(tr("Einmündungen zusammenlegen bis:"), self.merge_spin)

        self.clip_x_spin = QDoubleSpinBox()
        self.clip_x_spin.setRange(-60000.0, 60000.0)
        self.clip_x_spin.setDecimals(0)
        self.clip_x_spin.setSingleStep(500.0)
        self.clip_x_spin.setSuffix(" m")
        self.clip_x_spin.valueChanged.connect(self._invalidate)
        form.addRow(tr("Ausschnitt Mitte x (Ost):"), self.clip_x_spin)

        self.clip_y_spin = QDoubleSpinBox()
        self.clip_y_spin.setRange(-60000.0, 60000.0)
        self.clip_y_spin.setDecimals(0)
        self.clip_y_spin.setSingleStep(500.0)
        self.clip_y_spin.setSuffix(" m")
        self.clip_y_spin.valueChanged.connect(self._invalidate)
        form.addRow(tr("Ausschnitt Mitte y (Nord):"), self.clip_y_spin)

        self.clip_size_spin = QDoubleSpinBox()
        self.clip_size_spin.setRange(0.0, 120000.0)
        self.clip_size_spin.setDecimals(0)
        self.clip_size_spin.setSingleStep(1000.0)
        self.clip_size_spin.setSuffix(" m")
        self.clip_size_spin.setToolTip(
            tr("Nur Wege in diesem Quadrat (Mitte in Metern ab Kartenmitte). 0 = ganze Karte. "
            "Für große Karten: erst einen Ausschnitt von 6000 bis 8000 m testen.")
        )
        self.clip_size_spin.valueChanged.connect(self._invalidate)
        form.addRow(tr("Ausschnitt Kantenlänge (0 = alles):"), self.clip_size_spin)

        self.margin_spin = QDoubleSpinBox()
        self.margin_spin.setRange(0.0, 1000.0)
        self.margin_spin.setDecimals(0)
        self.margin_spin.setSingleStep(10.0)
        self.margin_spin.setValue(NetworkOptions.edge_margin_m)
        self.margin_spin.setSuffix(" m")
        self.margin_spin.setToolTip(
            tr("Wege werden so weit vor dem Kartenrand abgeschnitten.")
        )
        self.margin_spin.valueChanged.connect(self._invalidate)
        form.addRow(tr("Abstand zum Kartenrand:"), self.margin_spin)

        # --- Ergebnis ----------------------------------------------------
        self.status_label = QLabel(
            tr("Noch nicht berechnet. „Netz berechnen“ zeigt, wie viele Wege "
            "und Knoten entstehen.")
        )
        self.status_label.setWordWrap(True)
        self.status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.status_label)

        row = QHBoxLayout()
        layout.addLayout(row)

        self.compute_button = QPushButton(tr("Netz berechnen"))
        self.compute_button.clicked.connect(self._compute)
        row.addWidget(self.compute_button)

        self.write_button = QPushButton(tr("Mod schreiben..."))
        self.write_button.setEnabled(False)
        self.write_button.clicked.connect(self._write)
        row.addWidget(self.write_button)

        self.station_button = QPushButton(tr("Bahnhöfe speichern..."))
        self.station_button.setToolTip(
            tr("Liest Bahnhöfe, Haltepunkte, Bahnsteige, Bahnhofsgebäude und Haltepositionen aus den geladenen "
            "OSM-Daten und speichert sie als .json (alles) und .csv (eine Zeile je Bahnhof). Es wird "
            "nichts im Spiel gebaut.")
        )
        self.station_button.clicked.connect(self._save_stations)
        row.addWidget(self.station_button)

        close_button = QPushButton(tr("Schließen"))
        close_button.clicked.connect(self.reject)
        row.addWidget(close_button)

    # ---------------------------------------------------------

    def _options(self) -> NetworkOptions:

        highways = frozenset(
            key for key, box in self.highway_boxes.items() if box.isChecked()
        )

        railways = set()

        if self.rail_box.isChecked():
            railways.add("rail")

        if self.light_rail_box.isChecked():
            railways.add("light_rail")

        return NetworkOptions(
            include_streets=bool(highways),
            include_rail=bool(railways),
            include_tram=self.tram_box.isChecked(),
            highways=highways,
            railways=frozenset(railways),
            include_bridges=self.bridge_box.isChecked(),
            include_tunnels=self.tunnel_box.isChecked(),
            min_bridge_m=self.min_bridge_spin.value(),
            oneway_templates=self.oneway_box.isChecked(),
            merge_junctions_m=self.merge_spin.value(),
            max_edge_m=self.edge_spin.value(),
            min_road_track_m=self.road_gap_spin.value(),
            merge_dual_carriageways=self.dual_box.isChecked(),
            dedupe_tracks=self.dedupe_box.isChecked(),
            clip_center_m=(self.clip_x_spin.value(), self.clip_y_spin.value()),
            clip_size_m=self.clip_size_spin.value(),
            simplify_tolerance_m=self.tolerance_spin.value(),
            min_segment_m=self.min_segment_spin.value(),
            edge_margin_m=self.margin_spin.value(),
        )

    def _nur_hauptstrecken(self):
        """Wohn- und Nebenstrassen abwaehlen (Hauptstrecken-Test)."""

        for key in ("residential", "living_street", "unclassified", "service"):
            box = self.highway_boxes.get(key)

            if box is not None:
                box.setChecked(False)

    def _invalidate(self, *_args):
        """Einstellung geaendert: das berechnete Netz passt nicht mehr."""

        if self._network is None:
            return

        self._network = None
        self.write_button.setEnabled(False)
        self.status_label.setText(
            tr("Einstellungen geändert. Bitte „Netz berechnen“ erneut ausführen.")
        )

    def _compute(self):

        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            network = collect_network(
                self.osm, self.selection, self._options()
            )
        except Exception as error:  # Berechnung darf den Dialog nicht beenden
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(
                self,
                tr("Straßen und Gleise"),
                tr("Das Netz konnte nicht berechnet werden:\n{error}").format(error=error),
            )
            return

        QApplication.restoreOverrideCursor()

        self._network = network
        self.status_label.setText(summary_text(network))
        self.write_button.setEnabled(bool(network.ways))

        if not network.ways:
            self.status_label.setText(
                summary_text(network)
                + tr("\n\nKeine Wege gefunden. Sind Straßen und Gleise geladen "
                "(Werkzeuge → OSM laden) und die Haken oben gesetzt?")
            )

    def _save_stations(self):

        if self.osm is None:
            QMessageBox.information(
                self, tr("Bahnhöfe"), tr("Es sind keine OSM-Daten geladen."),
            )
            return

        try:
            data = collect_stations(self.osm, self.selection)
        except Exception as error:  # noqa: BLE001 - dem Nutzer melden, nicht abstuerzen
            QMessageBox.warning(self, tr("Bahnhöfe"), tr("Die Bahnhöfe konnten nicht gelesen werden:\n{error}").format(error=error))
            return

        if not data["stations"]:
            QMessageBox.information(
                self,
                tr("Bahnhöfe"),
                tr("In den geladenen OSM-Daten wurden keine Bahnhöfe oder Haltepunkte gefunden.\n\n"
                "Möglicherweise lädt die OSM-Abfrage des Studios Bahnhofsdaten nicht mit. Dann müsste "
                "die Abfrage um railway=station/halt/platform und building=train_station erweitert werden."),
            )
            return

        chosen, _filter = QFileDialog.getSaveFileName(
            self,
            tr("Bahnhöfe speichern"),
            str(Path.home() / "bahnhoefe.json"),
            tr("JSON (*.json)"),
        )

        if not chosen:
            return

        try:
            json_path, csv_path = write_stations(data, chosen)
        except OSError as error:
            QMessageBox.warning(self, tr("Bahnhöfe"), tr("Die Dateien konnten nicht geschrieben werden:\n{error}").format(error=error))
            return

        QMessageBox.information(
            self,
            tr("Bahnhöfe"),
            tr("{station_summary}\n\nGespeichert:\n{json_path}\n{csv_path}").format(station_summary=station_summary(data), json_path=json_path, csv_path=csv_path),
        )

    def _write(self):

        if self._network is None or not self._network.ways:
            return

        folder = find_tpf3_mods_folder()

        start = str(folder) if folder is not None and folder.is_dir() else str(Path.home())

        chosen = QFileDialog.getExistingDirectory(
            self,
            tr("Ordner „mods“ von Transport Fever 3 wählen"),
            start,
        )

        if not chosen:
            return

        try:
            root = write_mod(chosen, self._network, "Map Studio")
        except OSError as error:
            QMessageBox.warning(
                self,
                tr("Straßen und Gleise"),
                tr("Der Mod konnte nicht geschrieben werden:\n{error}").format(error=error),
            )
            return

        QMessageBox.information(
            self,
            tr("Straßen und Gleise"),
            tr("Mod geschrieben:\n{root}\n\nIm Spiel:\n1. Mod „Map Studio Import“ im Mod-Menü aktivieren und das Spiel neu starten.\n2. Karte mit der Heightmap laden, warten bis „Map is ready“ in der Konsole steht, Spielstand speichern, Pause ausschalten.\n3. In der Konsole eingeben:\n{START_COMMAND}\n4. Warten bis „Import fertig“ in der Konsole steht.").format(root=root, START_COMMAND=START_COMMAND),
        )
