"""
Bettet das Lua-Skript des Spiel-Mods in ein Python-Modul ein.

Quelle:  src/heightmap/mod_template/mapstudio.script.lua
Ziel:    src/heightmap/network_mod_script.py

Warum: Das Studio wird als .exe gebaut (PyInstaller). Eine eingebettete
Zeichenkette braucht keinen Eintrag in build.spec. Nach jeder Aenderung am
Lua-Skript einmal ausfuehren:   python tools/embed_mod_script.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "heightmap" / "mod_template" / "mapstudio.script.lua"
DST = ROOT / "src" / "heightmap" / "network_mod_script.py"

text = SRC.read_text(encoding="utf-8")

if '"""' in text or text.endswith("\\"):
    raise SystemExit("Das Skript enthaelt dreifache Anfuehrungszeichen.")

DST.write_text(
    '"""Automatisch erzeugt von tools/embed_mod_script.py. Nicht von Hand aendern."""\n\n'
    'IMPORT_SCRIPT_TEMPLATE = r"""' + text + '"""\n',
    encoding="utf-8",
)

print("geschrieben:", DST, len(text), "Zeichen")
