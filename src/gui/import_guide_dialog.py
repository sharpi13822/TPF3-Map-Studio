import json
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QCheckBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QWidget,
    QDialogButtonBox,
    QApplication,
)
from src.i18n import tr


SETTINGS_PATH = Path.home() / ".tpf2_map_studio" / "import_guide_settings.json"

# (Feldname, Beschriftung, Standardwert) - siehe
# res/scripts/osm_importer/README.md des OSM-TPF2-Importer-Projekts,
# Abschnitt "Options for Step 3".
OPTION_FIELDS = (
    ("build_streets", tr("Straßen bauen (inkl. Fußwege/Bäche)"), True),
    ("build_tracks", tr("Gleise bauen"), True),
    ("build_subwaytracks", tr("U-Bahn-/Stadtbahn-Gleise (subway/light_rail)"), True),
    ("build_tramtracks", tr("Straßenbahn als eigene Gleise (statt auf Straßen)"), False),
    ("build_bridges", tr("Brücken bauen"), True),
    ("build_tunnels", tr("Tunnel bauen (Ergebnis oft unbefriedigend)"), False),
    ("build_signals", tr("Signale bauen (nur deutsche Signale)"), True),
    ("build_autobahn", tr("Autobahnen bauen"), True),
    ("build_streets_street_types", tr("Normale Straßentypen bauen"), True),
    ("build_streets_footway_types", tr("Fuß-/Radwege bauen"), True),
    ("build_streets_water", tr("Wasserstraßen für Bäche/kleine Flüsse"), True),
    ("build_streets_airport", tr("Flughafen-Straßen (braucht Airport-Roads-Mod)"), True),
    ("skip_nodes_outofbounds", tr("Knoten außerhalb der Kartengrenzen überspringen"), True),
    ("crash_type_not_found", tr("Bei fehlendem Mod-Typ abbrechen (empfohlen zum Testen)"), True),
)

STEP_0_COMMAND = 'require "osm_importer.main"'

STEP_1_COMMAND = (
    "m.towns.createTownLabels(osmdata.towns)\n"
    'm.scriptevent.ScriptEvent("setAllTownsDevActive-false")\n'
    'm.scriptevent.ScriptEvent("bulldoze.delEdges")  -- entfernt ALLE gebauten Straßen!\n'
    "bulldoze.delAssets() -- entfernt Bäume (Reste von Städten)"
)

STEP_2_COMMAND = "m.areas.buildAreas(osmdata.areas, osmdata.nodes)"

STEP_3_CALL = "m.simpleproposalseq.SimpleProposalSeq(osmdata, options)"

STEP_4_COMMAND = "m.models.buildObjects(osmdata.objects)"


class ImportGuideDialog(QDialog):
    """
    Referenz-Dialog mit dem kompletten, offiziellen Import-Ablauf des
    OSM-TPF2-Importers (5 Schritte 0-4), inkl. kopierbarer Befehle und
    einer per Checkbox konfigurierbaren Optionen-Tabelle fuer Schritt 3.

    Quelle: res/scripts/osm_importer/README.md des OSM-TPF2-Importer-
    Projekts (Vacuum-Tube). Fast nichts hiervon ist kartengroessen-
    abhaengig - das einzige, was sich pro Projekt aendert, ist der
    Converter-Befehl (siehe eigener Dialog "Converter-Befehl anzeigen...").
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle(tr("Import-Anleitung (OSM-TPF2-Importer)"))
        self.setMinimumSize(760, 640)

        outer_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer_layout.addWidget(scroll)

        content = QWidget()
        layout = QVBoxLayout(content)
        scroll.setWidget(content)

        intro = QLabel(
            tr("Alle Schritte müssen in dieser Reihenfolge ausgeführt werden. "
            "Die Karte muss vorher komplett leer sein (keine Straßen/Gleise/"
            "Vegetation, nur Terrain). Am besten zuerst mit einem kleinen "
            "Testausschnitt üben.")
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        # -------------------------------------------------
        # Schritt 0
        # -------------------------------------------------

        layout.addWidget(self._make_step_group(
            tr("Schritt 0: Initialisierung"),
            tr("Spiel pausieren. In UG Console UND Script Thread eingeben "
            "(Workaround für Script Thread ohne CommonAPI2: "
            'm.scriptevent.ScriptEvent("require-osm_importer.main")):'),
            STEP_0_COMMAND,
        ))

        # -------------------------------------------------
        # Schritt 1
        # -------------------------------------------------

        layout.addWidget(self._make_step_group(
            tr("Schritt 1: Stadtnamen"),
            tr("In der UG Console, Zeile für Zeile. Bekannter Absturz "
            "('proposalData.errorState.Empty()'): tritt auf, wenn eine "
            "Stadt zu nah an Wasser liegt - betroffene Stadt dann aus "
            "osmdata.lua entfernen."),
            STEP_1_COMMAND,
        ))

        # -------------------------------------------------
        # Schritt 2
        # -------------------------------------------------

        layout.addWidget(self._make_step_group(
            tr("Schritt 2: Flächen (Wälder/Oberflächen)"),
            tr("Im Script Thread (Workaround ohne CommonAPI2, in UG Console: "
            'm.scriptevent.ScriptEvent("areas.buildAreas")). Braucht '
            "Forester-Mod (Version 1.4 Interface!) und Paver-Mod. Kann "
            "eine Weile dauern."),
            STEP_2_COMMAND,
        ))

        # -------------------------------------------------
        # Schritt 3 - Optionen-Tabelle
        # -------------------------------------------------

        step3_group = QGroupBox(tr("Schritt 3: Straßen/Gleise (der lange Schritt)"))
        step3_layout = QVBoxLayout(step3_group)

        step3_note = QLabel(
            tr("In der UG Console zuerst die Optionen-Tabelle einfügen, DANACH "
            "den Aufruf. Dauer grob schätzbar: Anzahl Edges / 5 Sekunden "
            "(siehe Converter-Log), bei großen Karten mehrere Stunden. "
            "Bekannter Fallstrick ('Already called, reload osm_importer "
            "before use again'): Workaround ist, beides in einer Zeile "
            "auszuführen: asdf=1; ") + STEP_3_CALL
        )
        step3_note.setWordWrap(True)
        step3_layout.addWidget(step3_note)

        self.option_checkboxes: dict[str, QCheckBox] = {}

        for key, label, default in OPTION_FIELDS:

            checkbox = QCheckBox(label)
            checkbox.setChecked(default)
            checkbox.toggled.connect(self._update_options_output)

            self.option_checkboxes[key] = checkbox

            step3_layout.addWidget(checkbox)

        self.options_output = QPlainTextEdit()
        self.options_output.setReadOnly(True)
        self.options_output.setMinimumHeight(280)
        self.options_output.setStyleSheet("font-family: Consolas, monospace;")
        step3_layout.addWidget(self.options_output)

        step3_copy_button = QPushButton(tr("Optionen-Tabelle + Aufruf kopieren"))
        step3_copy_button.clicked.connect(
            lambda: self._copy(self.options_output.toPlainText())
        )
        step3_layout.addWidget(step3_copy_button)

        layout.addWidget(step3_group)

        # -------------------------------------------------
        # Schritt 4
        # -------------------------------------------------

        layout.addWidget(self._make_step_group(
            tr("Schritt 4: Objekte"),
            tr("In der UG Console. Muss NACH Schritt 3 kommen, da er Höhen "
            "verändert. Baut Einzelbäume, Brunnen, Poller, Litfaßsäulen."),
            STEP_4_COMMAND,
        ))

        # -------------------------------------------------
        # Allgemeine Hinweise
        # -------------------------------------------------

        hints_group = QGroupBox(tr("Allgemeine Hinweise"))
        hints_layout = QVBoxLayout(hints_group)

        hints_label = QLabel(
            tr("• Alle 4 Schritte sollten in derselben Sitzung direkt "
            "hintereinander laufen, nicht über mehrere Tage verteilt.\n"
            "• Bei Änderungen an osmdata.lua oder den Skripten: m.reload() "
            "nötig (Spielstand neu laden reicht nicht).\n"
            "• Schritt 3 lässt sich nicht zweimal ohne Reload ausführen.\n"
            "• Nach Schritt 3: im Log nach 'WARNING' und 'ERROR' suchen "
            "(stdout.txt), auch wenn der Prozess nicht abgebrochen ist.\n"
            "• Alle Schritte auf einer bereits bebauten Fläche können zu "
            "Problemen führen - die Karte muss vorher leer sein.")
        )
        hints_label.setWordWrap(True)
        hints_layout.addWidget(hints_label)

        layout.addWidget(hints_group)

        # -------------------------------------------------
        # Schließen
        # -------------------------------------------------

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        outer_layout.addWidget(buttons)

        self._load_settings()
        self._update_options_output()

    # ---------------------------------------------------------
    # Hilfsfunktionen
    # ---------------------------------------------------------

    def _make_step_group(self, title: str, note: str, command: str) -> QGroupBox:

        group = QGroupBox(title)
        group_layout = QVBoxLayout(group)

        note_label = QLabel(note)
        note_label.setWordWrap(True)
        group_layout.addWidget(note_label)

        output = QPlainTextEdit()
        output.setReadOnly(True)
        output.setPlainText(command)
        output.setMaximumHeight(80 if "\n" in command else 40)
        output.setStyleSheet("font-family: Consolas, monospace;")
        group_layout.addWidget(output)

        copy_button = QPushButton(tr("Kopieren"))
        copy_button.clicked.connect(lambda: self._copy(command))
        group_layout.addWidget(copy_button)

        return group

    def _copy(self, text: str):
        QApplication.clipboard().setText(text)

    def _update_options_output(self):

        self._save_settings()

        lines = ["options = {"]

        for key, _, _ in OPTION_FIELDS:

            value = self.option_checkboxes[key].isChecked()

            lines.append(f"\t{key} = {'true' if value else 'false'},")

        lines.append("\tlog_level = 1,")
        lines.append("}")
        lines.append("")
        lines.append(STEP_3_CALL)

        self.options_output.setPlainText("\n".join(lines))

    def _load_settings(self):

        if not SETTINGS_PATH.is_file():
            return

        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        for key, checkbox in self.option_checkboxes.items():

            if key in data:
                checkbox.setChecked(data[key])

    def _save_settings(self):

        try:
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

            data = {
                key: checkbox.isChecked()
                for key, checkbox in self.option_checkboxes.items()
            }

            SETTINGS_PATH.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError:
            pass
