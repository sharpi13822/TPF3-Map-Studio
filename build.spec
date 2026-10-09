# PyInstaller-Buildkonfiguration fuer TPF3-Map-Studio.
#
# Verwendung (im Projekt-Hauptordner, mit aktivierter venv):
#   pip install pyinstaller
#   tools\make_release.ps1 -Version <x.y.z>   (baut und packt das Release)
#   oder nur bauen: pyinstaller build.spec
#
# Ergebnis liegt danach in dist/TPF3-Map-Studio/
#
# Das Paket wird klein gehalten: tools/build_filter.py entfernt Dateien, die das
# Studio nicht braucht (andere Sprachen, Entwicklerwerkzeuge, QML-Module).

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

block_cipher = None

# -----------------------------------------------------------------
# Datendateien, die zur Laufzeit vom lokalen HTTP-Server bzw. von
# icons.py gelesen werden (siehe src/core/server.py, src/gui/icons.py) -
# muessen an DERSELBEN relativen Stelle wie im Quellbaum landen, da der
# Code sie ueber Path(__file__)-relative Pfade findet.
# -----------------------------------------------------------------

datas = [
    ("src/map/web", "src/map/web"),
    ("src/icons", "src/icons"),
    # Symbole und Bedienelemente des Studio-Designs (src/gui/icon_set.py, src/gui/theme.py)
    ("src/gui/icons", "src/gui/icons"),
]

# PySide6s eigene QtWebEngine-Ressourcen (icudtl.dat, resources.pak,
# Lokalisierungsdateien, QtWebEngineProcess.exe) - collect_data_files
# holt automatisch alles, was das installierte PySide6-Paket dafuer
# mitbringt. Falls die exe beim ersten Start mit einer QtWebEngine-
# bezogenen Fehlermeldung abstuerzt, ist das der wahrscheinlichste Ort,
# an dem noch etwas fehlt (siehe Hinweise unten).
datas += collect_data_files("PySide6", subdir="Qt/resources")
datas += collect_data_files("PySide6", subdir="Qt/translations")

# SSL-Zertifikate fuer HTTPS-Anfragen (requests -> Overpass-API,
# Copernicus-Hoehendaten) - werden von PyInstaller nicht immer
# automatisch mitgebuendelt, was zu SSL-Fehlern in der exe fuehrt,
# obwohl der Quellcode einwandfrei funktioniert.
datas += collect_data_files("certifi")

# scipy ist dafuer bekannt, dass PyInstallers automatische Erkennung es
# oft komplett uebersieht (verschachtelte, teils dynamisch geladene
# Untermodule mit eigenen C-Erweiterungen) - deshalb hier explizit ALLE
# scipy-Untermodule und binaeren Erweiterungen mitgeben, statt uns auf
# die automatische Analyse zu verlassen.
scipy_submodules = collect_submodules("scipy")
scipy_binaries = collect_dynamic_libs("scipy")

a = Analysis(
    ["src/main.py"],
    pathex=["."],
    binaries=scipy_binaries,
    datas=datas,
    hiddenimports=[
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebEngineCore",
        "PySide6.QtNetwork",
        "certifi",
        # Wird in src/i18n.py erst bei Bedarf importiert (englischer Katalog).
        "src.i18n_en",
        "src.i18n_web_en",
        "requests",
        "urllib3",
        "scipy",
    ] + scipy_submodules,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

# Nicht benoetigte Dateien aus dem Paket nehmen (siehe tools/build_filter.py)
import sys
sys.path.insert(0, SPECPATH)
from tools.build_filter import soll_behalten

a.datas = [d for d in a.datas if soll_behalten(d[0])]
a.binaries = [b for b in a.binaries if soll_behalten(b[0])]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TPF3-Map-Studio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX-Kompression mit QtWebEngine hat oefter Probleme verursacht
    icon="src/icons/app.ico",
    console=False,  # kein Konsolenfenster
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="TPF3-Map-Studio",
)
