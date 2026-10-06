"""
Haengt den Knopf "Strassen und Gleise..." in den Heightmap-Dialog ein.

Aufruf im Projektordner:   python tools/patch_heightmap_dialog.py

Es werden genau drei Stellen in src/gui/heightmap_dialog.py ergaenzt:
  1. der Import von NetworkDialog,
  2. der Knopf in der Knopfleiste (nach "Industrien aus OSM..."),
  3. die Methode _open_network_dialog (vor _open_industries_dialog).
Nichts wird entfernt. Laeuft das Skript ein zweites Mal, meldet es
"schon eingebaut" und aendert nichts. Rueckgaengig: git checkout src/gui/heightmap_dialog.py
"""

from pathlib import Path

ZIEL = Path(__file__).resolve().parent.parent / "src" / "gui" / "heightmap_dialog.py"

IMPORT_ANKER = "from src.gui.towns_dialog import TownsDialog\n"
IMPORT_NEU = IMPORT_ANKER + "from src.gui.network_dialog import NetworkDialog\n"

KNOPF_ANKER = "        button_row.addWidget(self.industries_button)\n"
KNOPF_NEU = KNOPF_ANKER + '''
        # Strassen und Gleise fuer den Spiel-Mod (eigener Dialog, schreibt
        # den Mod in den Ordner mods).
        self.network_button = QPushButton("Straßen und Gleise...")
        self.network_button.setToolTip(
            "Erzeugt aus den geladenen OSM-Wegen einen Mod, der im Spiel "
            "Straßen, Gleise, Brücken und Tunnel baut. Braucht geladene "
            "OSM-Daten."
        )
        self.network_button.clicked.connect(self._open_network_dialog)
        button_row.addWidget(self.network_button)
'''

METHODE_ANKER = "    def _open_industries_dialog(self):\n"
METHODE_NEU = '''    def _open_network_dialog(self):

        has_osm_data = (
            self.osm is not None
            and (self.osm.node_count > 0 or self.osm.way_count > 0)
        )

        if not has_osm_data:
            QMessageBox.information(
                self,
                "Straßen und Gleise",
                "Keine OSM-Daten geladen. Zuerst Werkzeuge → OSM laden "
                "ausführen und die Ebenen Straßen und Eisenbahn laden.",
            )
            return

        NetworkDialog(self, self.selection, self.osm).exec()

''' + METHODE_ANKER


def main():

    text = ZIEL.read_bytes().decode("utf-8")
    bom = text.startswith("\ufeff")
    text = text.lstrip("\ufeff")

    # Zeilenende des Projekts merken (Windows: \r\n)
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")

    if "NetworkDialog" in text:
        print("schon eingebaut, nichts geaendert")
        return

    for name, anker in (
        ("Import", IMPORT_ANKER),
        ("Knopfleiste", KNOPF_ANKER),
        ("Methode", METHODE_ANKER),
    ):
        if text.count(anker) != 1:
            raise SystemExit(
                f"Abbruch: Anker '{name}' kommt {text.count(anker)}x vor "
                "(erwartet 1x). Datei wurde nicht veraendert."
            )

    text = text.replace(IMPORT_ANKER, IMPORT_NEU, 1)
    text = text.replace(KNOPF_ANKER, KNOPF_NEU, 1)
    text = text.replace(METHODE_ANKER, METHODE_NEU, 1)

    if crlf:
        text = text.replace("\n", "\r\n")

    out = ("\ufeff" if bom else "") + text
    ZIEL.write_bytes(out.encode("utf-8"))

    print("eingebaut:", ZIEL)


if __name__ == "__main__":
    main()
