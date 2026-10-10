<p align="center">
  <img src="docs/images/banner.png" alt="TPF3 Map Studio" width="100%">
</p>
<p align="center"><sub>Banner: illustration, not the real program window.</sub></p>

# TPF3 Map Studio

[Deutsch](README.md) | **English**

A free Windows tool that prepares real-world map data for building realistic maps in **Transport Fever 3**: pick a map area, load OpenStreetMap and elevation data, and generate a heightmap, biome mask, towns, industries and a station list for import into the game's map editor.

> Unofficial tool. It is not affiliated with Urban Games or the publisher of Transport Fever.
>
> **Note on language:** the program is available in German and English. On the first start it follows the Windows language; you can change it in the menu **Sprache / Language** (takes effect after a restart). Menu names below are given as they appear in the German program, with the English name in brackets; in the English interface use the bracketed name.

## Download and start

**[Download for Windows: latest version](https://github.com/sharpi13822/TPF3-Map-Studio/releases/latest)**

No Python installation needed. To start the program:

1. On the [release page](https://github.com/sharpi13822/TPF3-Map-Studio/releases/latest), under **Assets**, download `TPF3-Map-Studio-v…-win64.zip`
2. **Extract the whole ZIP file**, for example to the desktop. Do not run it from inside the ZIP and do not copy out only the `.exe`: the program needs the `_internal` folder next to it
3. In the extracted folder, double-click **`TPF3-Map-Studio.exe`**. It sits at the top, next to `START-HIER.txt`, `LICENSE` and the `_internal` folder

Then continue with [How to work with it](#how-to-work-with-it).

### Windows warns on first start, this is normal

This `.exe` is not digitally signed (signing is a paid service), so Windows usually shows a blue warning **"Windows protected your PC"** on the very first start. (The text is "Windows hat Ihren PC geschützt" on a German system.) To get past it:

1. Click **"More info"**
2. A **"Run anyway"** button appears, click it

This only appears on the first start. If your antivirus also flags the file or moves it to quarantine: that is a known **false positive** that happens often with programs built this way (PyInstaller), not a real threat. Restore the file from quarantine or add an exception for it.

### System requirements

- Windows 10 or 11 (64-bit)
- Internet connection (for the OSM and elevation data downloads)
- About 520 MB of free disk space for the extracted program
- For large maps with DGM1, several GB of free RAM, because the elevation data is processed in memory

## Contents

- [Download and start](#download-and-start)
- [Example: Bern in the game](#example-bern-in-the-game)
- [Features](#features)
- [How to work with it](#how-to-work-with-it)
- [Building it yourself: from Python to the .exe](#building-it-yourself-from-python-to-the-exe)
- [Data and attribution](#data-and-attribution)
- [Acknowledgements](#acknowledgements)
- [Questions, problems and contact](#questions-problems-and-contact)
- [Support](#support)
- [Licence](#licence)

## Example: Bern in the game

<p align="center">
  <img src="docs/images/beispiel-bern.jpg" alt="Bern in Transport Fever 3, built with the Studio" width="100%">
</p>
<p align="center"><sub>View in Transport Fever 3: terrain from swissALTI3D, waters, places and biomes from OpenStreetMap, created with the Studio. Sources: © swisstopo (Bundesamt für Landestopografie swisstopo), © OpenStreetMap contributors.</sub></p>

## Features

- **Map area**: set it with the rectangle tool (centre, size, rotation) and plan it in the game's format (for example "Größenwahnsinnig 1:5", the game's largest scale)
- **Load OSM data** with a configurable Overpass query (checkboxes and templates instead of free text)
- **Heightmap** from DGM1 (Germany, 1 m), swissALTI3D (Switzerland and Liechtenstein, 2 m), Copernicus (worldwide, 30 m, includes tree canopy) or your own GeoTIFF tiles. With a quick preview (always Copernicus), water level suggestion, rivers from OSM, slope compensation, levelling of railway routes and settlements, smoothing and squashing, and a height window for the limits of the map editor (−20 to 3177 m: cap peaks, cut off lows or squash, with preview). The dialog lists the values to enter during the import in the game. The heightmap is saved as a 16-bit PNG
- **Biome mask, towns and industries** from OSM, as files for the import in the editor
- **Stations** as named markers on the map and as a list (`bahnhoefe.json` and `bahnhoefe.csv`) with platforms, stopping positions and status (abandoned, under construction). Nothing is built in the game from this, the list is a reference
- **Map**: OpenStreetMap, optionally with hillshade, plus switchable railway map (OpenRailwayMap) and a measuring grid. Layers can be shown, hidden, locked, and changed in opacity and order
- Draw your own roads, rivers and buildings, JSON export and import of the objects
- Coordinate measuring tool, pre-check of the loaded data, saving projects and a project dashboard

### Elevation sources at a glance

| Source | Area | Resolution | Provider | Note |
| --- | --- | --- | --- | --- |
| Copernicus DEM (GLO-30) | worldwide | 30 m | Copernicus (AWS Open Data) | includes tree canopy, default of the quick preview |
| DGM1 Germany | Germany | 1 m | hoehendaten.de (state surveys) | about 20 tiles per minute, large maps take half an hour |
| swissALTI3D | Switzerland and Liechtenstein | 2 m | data.geo.admin.ch (swisstopo) | only selectable for maps there, attribution is mandatory |
| Own tiles | Germany | depends on file | downloaded yourself from a state portal | GeoTIFF on the 1 km grid (UTM) |

Where data from one source is missing, the Studio fills the gaps from Copernicus. You choose the elevation source in the heightmap dialog.

The functions for Vacuum-Tube's OSM-TPF2-Importer (OSM export as `.osm`, mod checker, import guide, check of short connection segments) are hidden in this version. The code stays in the project and can be shown again with the `VACUUMTUBE_IMPORTER` switch in `src/features.py`.

A full description of all functions is in the Studio under **Hilfe → Funktionsübersicht** (Help → Feature overview).

## How to work with it

1. Set the map centre with the marker tool, then **Werkzeuge → Rechteck-Tool** (Tools → Rectangle tool): choose map size and rotation
2. **Werkzeuge → OSM laden** (Tools → Load OSM). What gets loaded is set under **Werkzeuge → Overpass-Abfrage** (Tools → Overpass query)
3. **Werkzeuge → Heightmap herunterladen** (Tools → Download heightmap): choose the elevation source, check the settings, load the elevation data and export. At the bottom of the dialog you find minimum height, maximum height, water level and map format for the import
4. In the same dialog, optionally create **biome mask**, **towns**, **industries** and **stations** from OSM
5. In the Transport Fever 3 editor, import the files and enter the numbers from step 3

Open the guide in the heightmap dialog with F1.

## Building it yourself: from Python to the .exe

This guide leads step by step from a Windows computer without Python to the finished `.exe`. Enter all commands in **PowerShell** (Start menu, type "PowerShell", Enter).

You need: Windows 10 or 11 (64-bit), an internet connection and a few GB of free disk space (Python, the packages and the build need room).

### 1. Install Python

1. Go to <https://www.python.org/downloads/release/python-3119/>, scroll down and download the **Windows installer (64-bit)** of **Python 3.11.9**. The Studio is tested with this version. Other 3.11 versions should also work. Python 3.12 and newer are untested with the pinned PySide6 version 6.7.2.
2. Start the installer and, **in the first window at the bottom, tick "Add python.exe to PATH"**. This is the most common stumbling block. Then click **"Install Now"**.
3. Open a **new** PowerShell and check:
   ```
   python --version
   ```
   It shows `Python 3.11.9`. If the Microsoft Store opens instead, turn off the entries for `python.exe` under *Settings → Apps → Advanced app settings → App execution aliases* and try again.

### 2. Download the Studio

Without Git: on the project's GitHub page click the green **Code** button, choose **Download ZIP** and extract it to a folder with a short path without spaces or special characters, for example `C:\TPF3-Map-Studio`.

With Git (<https://git-scm.com/download/win>); updating later with `git pull` is then easier:
```
git clone https://github.com/sharpi13822/TPF3-Map-Studio.git
```

### 3. Change into the project folder

```
cd C:\TPF3-Map-Studio
```
Adjust the path to your folder. In Windows Explorer you can also open the folder, type `powershell` in the address bar and press Enter.

### 4. Create and activate a virtual environment

The virtual environment keeps the Studio's packages separate from the rest of your system.
```
python -m venv .venv
.venv\Scripts\Activate.ps1
```
Afterwards `(.venv)` appears at the start of the line. If PowerShell says scripts may not be run, enter the following once, confirm with **Y** (**J** on a German system) and repeat the second command:
```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 5. Install the packages

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
This downloads PySide6 (with Qt WebEngine), among others, and takes a few minutes.

### 6. Start the Studio (test)

```
python -m src.main
```
The window with the map opens. If it runs, everything is installed correctly.

### 7. Build the .exe

```
pip install pyinstaller
pyinstaller build.spec
```
If PyInstaller asks at the end **"The output directory … will be REMOVED! Continue? (y/N)"**, answer `y`. This happens when an old build folder exists. The build takes a few minutes.

The result is in:
```
dist\TPF3-Map-Studio\TPF3-Map-Studio.exe
```
To pass it on, pack the **whole folder** `dist\TPF3-Map-Studio` into a ZIP file. The `.exe` alone does not run, it needs the `_internal` folder next to it.

### 8. Everything in one step (optional)

The script `tools\make_release.ps1` builds the `.exe`, checks that the icons are in the package, puts `START-HIER.txt`, `LICENSE` and `THIRD_PARTY_NOTICES.md` next to the `.exe` and packs the whole folder into a ZIP file together with a checksum. With an existing `.venv` in the project folder:
```
powershell -ExecutionPolicy Bypass -File tools\make_release.ps1 -Version 0.3.0
```
The ZIP is then called `TPF3-Map-Studio-v0.3.0-win64.zip`. It does not belong in the Git repository but is attached to a release on GitHub (see below).

### 9. Check

- Double-click `TPF3-Map-Studio.exe`. Windows warns on the first start (see above).
- This command shows whether the icons made it into the package. It should print two hits:
  ```
  Get-ChildItem dist\TPF3-Map-Studio -Recurse -Filter "strassen_hell.png" | Select-Object FullName
  ```

### 10. Publish as a release on GitHub (for maintainers)

1. On GitHub: **Releases → Draft a new release**
2. Create a new tag, for example `v0.3.0` (on `master`)
3. Attach the ZIP file under **Assets**, put the checksum from `…sha256.txt` into the description and publish

The "Download for Windows" link above then automatically points to the latest version.

### If something does not work

| Problem | Solution |
| --- | --- |
| `python` is not recognised | Reinstall Python and tick "Add python.exe to PATH". Then open a **new** PowerShell |
| "Running scripts is disabled" | Enter `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, see step 4 |
| `pip install` reports "No matching distribution found for PySide6" | Check the version with `python --version`. Use Python 3.11.9 (64-bit) |
| The `.exe` starts but the window stays empty or closes | In `build.spec` change the line `console=False` to `console=True` and rebuild. A black window then shows the error message. Please report it in an [issue](https://github.com/sharpi13822/TPF3-Map-Studio/issues) |
| Antivirus raises an alarm | Known false positive with PyInstaller programs, see above |
| Packages are missing after an update | With the `.venv` activated, run `pip install -r requirements.txt` again |

The tests are in the `tests` folder, for example `python -m unittest tests.test_readme`.

## Data and attribution

The Studio uses public data sources. If you publish a map made with it, please credit the sources:

- **Map data:** © OpenStreetMap contributors, Open Database License (ODbL)
- **Elevation data Germany (DGM1):** depending on the federal state, Data licence Germany, attribution, version 2.0 (dl-de/by-2-0). The heightmap dialog shows the exact attribution
- **Elevation data Switzerland and Liechtenstein (swissALTI3D):** © swisstopo (Bundesamt für Landestopografie swisstopo), Open Government Data, attribution is mandatory
- **Elevation data worldwide:** Copernicus DEM (GLO-30)

All sources, licences and notices are in [THIRD_PARTY_NOTICES.en.md](THIRD_PARTY_NOTICES.en.md).

## Acknowledgements

- [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors for the map data
- [Leaflet](https://leafletjs.com/) for the map display
- [Copernicus](https://copernicus-dem-30m.s3.amazonaws.com/) for the worldwide elevation data
- The state survey offices for DGM1 and [hoehendaten.de](https://hoehendaten.de/) for access to it
- [swisstopo](https://www.swisstopo.admin.ch/) for swissALTI3D
- [Vacuum-Tube](https://github.com/Vacuum-Tube/OSM-TPF2-Importer) for the OSM-TPF2-Importer. The Studio grew out of the wish to prepare data for it. The importer is an independent project under its own licence

## Questions, problems and contact

- **Bugs or wishes:** please open an [issue](https://github.com/sharpi13822/TPF3-Map-Studio/issues)
- **Questions, ideas and discussion:** in the [Discussions](https://github.com/sharpi13822/TPF3-Map-Studio/discussions)

For a bug report these details help: version of the Studio, Windows version, what you did, the exact error message (if any) and whether the error happens every time. Screenshots are welcome. Please do not attach map files with private data. You are welcome to write in English or German.

## Support

The Studio is free and made in spare time. If it helps you and you would like to support further development, I would be happy about a donation. It is voluntary and changes nothing about how you can use the program.

<a href="https://paypal.me/PEttelt"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="Donate with PayPal"></a>

## Licence

MIT, see [LICENSE](LICENSE). Notes on the data, services and libraries used are in [THIRD_PARTY_NOTICES.en.md](THIRD_PARTY_NOTICES.en.md).
