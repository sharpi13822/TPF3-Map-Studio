# TPF3 Map Studio

Ein Werkzeug, um echte OpenStreetMap-Daten für den Bau realer Kartenausschnitte in Transport Fever 2 vorzubereiten – Kartenausschnitt wählen, OSM-Daten herunterladen, Höhendaten exportieren, und alles für den Import mit dem [OSM-TPF2-Importer](https://github.com/Vacuum-Tube/OSM-TPF2-Importer) aufbereiten.

## Download (empfohlen für die meisten Nutzer)

Keine Python-Installation nötig – einfach die fertige Version herunterladen:

1. Auf der [Releases-Seite](../../releases) die neueste Version öffnen
2. Die `.zip`-Datei herunterladen und **komplett** an einen beliebigen Ort entpacken (z. B. auf den Desktop) – nicht nur die `.exe` einzeln herauskopieren, das Programm braucht die Begleitdateien im selben Ordner
3. In dem entpackten Ordner `TPF3-Map-Studio.exe` doppelklicken

### Windows warnt beim ersten Start – das ist normal

Da diese `.exe` nicht kostenpflichtig digital signiert ist, zeigt Windows beim allerersten Start meist eine blaue Warnung **"Windows hat Ihren PC geschützt"**. So kommst du daran vorbei:

1. Auf **"Weitere Informationen"** klicken
2. Danach erscheint ein Button **"Trotzdem ausführen"** – darauf klicken

Das erscheint nur beim ersten Start. Falls dein Virenscanner die Datei zusätzlich meldet oder in Quarantäne verschiebt: Das ist ein bekannter **Fehlalarm**, der bei so gebauten (PyInstaller-)Programmen öfter vorkommt, keine tatsächliche Bedrohung. Die Datei ggf. aus der Quarantäne wiederherstellen bzw. eine Ausnahme dafür einrichten.

### Systemvoraussetzungen

- Windows 10 oder 11 (64-Bit)
- Internetverbindung (für den OSM-/Höhendaten-Download)
- Ca. 500 MB freier Speicherplatz für das entpackte Programm

## Aus dem Quellcode starten (für Entwickler)

Falls du stattdessen den Quellcode selbst ausführen oder weiterentwickeln möchtest:

```
git clone https://github.com/sharpi13822/TPF3-Map-Studio.git
cd TPF3-Map-Studio
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main.py
```

Vorausgesetzt wird Python 3.11 oder neuer.

## Eigene .exe bauen

Aus dem Quellcode lässt sich mit [PyInstaller](https://pyinstaller.org/) selbst eine `.exe` erzeugen:

```
pip install pyinstaller
pyinstaller build.spec
```

Das Ergebnis liegt danach in `dist/TPF3-Map-Studio/`.

## Funktionen

- Kartenausschnitt per Rechteck-Tool festlegen (Mittelpunkt, Größe, Drehwinkel)
- OSM-Daten laden, mit konfigurierbarer Overpass-Abfrage (Checkboxen statt Freitext)
- Koordinaten-Messwerkzeug direkt auf der Karte
- Höhendaten-Download (Copernicus DEM) mit Schnellvorschau und automatischem Wasserhöhen-Vorschlag
- Export als Standard-OSM-XML-Datei für externe Konverter-Werkzeuge
- Mod-Checker gegen die Anforderungen des OSM-TPF2-Importers
- Vorab-Prüfung der geladenen Daten vor dem großen Import-Lauf
- Projekt-Speicherung und -Dashboard über mehrere Kartenprojekte hinweg
- Eingebaute Anleitung für den kompletten Import-Ablauf im Spiel

## Danksagung

- [OpenStreetMap](https://www.openstreetmap.org/copyright)-Mitwirkende für die Kartendaten
- [Leaflet](https://leafletjs.com/) für die Kartendarstellung
- [Copernicus](https://copernicus-dem-30m.s3.amazonaws.com/) für die Höhendaten
- [Vacuum-Tube](https://github.com/Vacuum-Tube/OSM-TPF2-Importer) für den OSM-TPF2-Importer, für den dieses Studio die Daten aufbereitet

## Lizenz

MIT – siehe [LICENSE](LICENSE)
