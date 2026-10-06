<p align="center">
  <img src="docs/images/banner.png" alt="TPF3 Map Studio" width="100%">
</p>
<p align="center"><sub>Titelbild: Illustration, nicht die echte Programmoberfläche.</sub></p>

# TPF3 Map Studio

Ein freies Werkzeug für Windows, das echte Kartendaten für den Bau realer Karten in **Transport Fever 3** vorbereitet: Kartenausschnitt wählen, OpenStreetMap-Daten und Höhendaten laden und daraus Heightmap, Biome-Maske, Städte, Industrien und eine Bahnhofsliste für den Import im Editor des Spiels erzeugen.

> Inoffizielles Werkzeug. Es steht in keiner Verbindung zu Urban Games oder dem Herausgeber von Transport Fever.

## Funktionen

- **Kartenausschnitt** per Rechteck-Tool festlegen (Mittelpunkt, Größe, Drehwinkel) und im Format des Spiels (z. B. Größenwahnsinnig 1:5) planen
- **OSM-Daten laden** mit konfigurierbarer Overpass-Abfrage (Checkboxen und Vorlagen statt Freitext)
- **Heightmap** aus dem DGM1 (Deutschland, 1 m) oder aus Copernicus (weltweit, 30 m), mit Schnellvorschau, Wasserhöhen-Vorschlag, Flüssen nach OSM, Gefälle-Ausgleich und Einebnen von Trassen und Siedlungen. Der Dialog nennt die Werte, die beim Import im Spiel einzutragen sind
- **Biome-Maske, Städte und Industrien** aus OSM, als Dateien für den Import im Editor
- **Bahnhöfe** als Marker mit Namen auf der Karte und als Liste (`bahnhoefe.json` und `bahnhoefe.csv`) mit Bahnsteigen, Haltepositionen und Status (aufgegeben, im Bau). Im Spiel wird dadurch nichts gebaut, die Liste dient als Nachschlagewerk
- **Hintergrundkarten:** OpenStreetMap, Satellit, Schattenrelief und Eisenbahnkarte (OpenRailwayMap)
- Koordinaten-Messwerkzeug, Vorab-Prüfung der geladenen Daten, Projekte speichern und Projekt-Dashboard

Funktionen für den OSM-TPF2-Importer von Vacuum-Tube (OSM-Export als `.osm`, Converter-Befehl, Mod-Checker, Import-Anleitung) sind in dieser Version ausgeblendet. Der Code bleibt im Projekt und lässt sich über den Schalter `VACUUMTUBE_IMPORTER` in `src/features.py` wieder einblenden.

## So arbeitest du

1. Mit dem Marker-Werkzeug die Kartenmitte setzen, dann **Werkzeuge → Rechteck-Tool**: Kartengröße und Drehwinkel wählen
2. **Werkzeuge → OSM laden**. Was geladen wird, stellst du unter **Werkzeuge → Overpass-Abfrage** ein
3. **Werkzeuge → Heightmap herunterladen**: Höhenquelle wählen, Einstellungen prüfen, Höhendaten laden und exportieren. Unten im Dialog stehen Mindesthöhe, Maximalhöhe, Wasserhöhe und Kartenformat für den Import
4. Im selben Dialog optional **Biome-Maske**, **Städte**, **Industrien** und **Bahnhöfe** aus OSM erzeugen
5. Im Editor von Transport Fever 3 die Dateien importieren und die Zahlen aus Schritt 3 eintragen

Die Anleitung im Heightmap-Dialog öffnest du mit F1, eine Übersicht aller Funktionen unter **Hilfe → Funktionsübersicht**.

## Download (empfohlen für die meisten Nutzer)

Keine Python-Installation nötig, einfach die fertige Version herunterladen:

1. Auf der [Releases-Seite](../../releases) die neueste Version öffnen
2. Die `.zip`-Datei herunterladen und **komplett** an einen beliebigen Ort entpacken (z. B. auf den Desktop). Nicht nur die `.exe` einzeln herauskopieren, das Programm braucht die Begleitdateien im selben Ordner
3. In dem entpackten Ordner `TPF3-Map-Studio.exe` doppelklicken

### Windows warnt beim ersten Start, das ist normal

Da diese `.exe` nicht kostenpflichtig digital signiert ist, zeigt Windows beim allerersten Start meist eine blaue Warnung **„Windows hat Ihren PC geschützt“**. So kommst du daran vorbei:

1. Auf **„Weitere Informationen“** klicken
2. Danach erscheint ein Button **„Trotzdem ausführen“**, darauf klicken

Das erscheint nur beim ersten Start. Falls dein Virenscanner die Datei zusätzlich meldet oder in Quarantäne verschiebt: Das ist ein bekannter **Fehlalarm**, der bei so gebauten (PyInstaller-)Programmen öfter vorkommt, keine tatsächliche Bedrohung. Die Datei ggf. aus der Quarantäne wiederherstellen bzw. eine Ausnahme dafür einrichten.

### Systemvoraussetzungen

- Windows 10 oder 11 (64-Bit)
- Internetverbindung (für den OSM- und Höhendaten-Download)
- Ca. 500 MB freier Speicherplatz für das entpackte Programm
- Für große Karten mit dem DGM1 mehrere GB freier Arbeitsspeicher, die Höhendaten werden dabei im Speicher verarbeitet

## Aus dem Quellcode starten (für Entwickler)

Falls du stattdessen den Quellcode selbst ausführen oder weiterentwickeln möchtest:

```
git clone https://github.com/sharpi13822/TPF3-Map-Studio.git
cd TPF3-Map-Studio
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.main
```

Vorausgesetzt wird Python 3.11 oder neuer. Die Tests laufen mit `python -m unittest` (siehe Ordner `tests`).

## Eigene .exe bauen

Aus dem Quellcode lässt sich mit [PyInstaller](https://pyinstaller.org/) selbst eine `.exe` erzeugen:

```
pip install pyinstaller
pyinstaller build.spec
```

Das Ergebnis liegt danach in `dist/TPF3-Map-Studio/`.

## Daten und Quellenangaben

Das Studio nutzt öffentliche Datenquellen. Wer eine damit erzeugte Karte veröffentlicht, sollte die Quellen nennen:

- **Kartendaten:** © OpenStreetMap-Mitwirkende, Open Database License (ODbL)
- **Höhendaten Deutschland (DGM1):** je nach Bundesland Datenlizenz Deutschland, Namensnennung, Version 2.0 (dl-de/by-2-0). Die genaue Quellenangabe zeigt der Heightmap-Dialog an
- **Höhendaten weltweit:** Copernicus DEM (GLO-30)

Alle Quellen, Lizenzen und Hinweise stehen in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Danksagung

- [OpenStreetMap](https://www.openstreetmap.org/copyright)-Mitwirkende für die Kartendaten
- [Leaflet](https://leafletjs.com/) für die Kartendarstellung
- [Copernicus](https://copernicus-dem-30m.s3.amazonaws.com/) für die weltweiten Höhendaten
- Die Landesvermessungsämter für das DGM1 und [hoehendaten.de](https://hoehendaten.de/) für den Zugang dazu
- [Vacuum-Tube](https://github.com/Vacuum-Tube/OSM-TPF2-Importer) für den OSM-TPF2-Importer. Das Studio ging aus dem Wunsch hervor, Daten für ihn aufzubereiten. Der Importer ist ein eigenständiges Projekt unter eigener Lizenz

## Fragen, Probleme und Kontakt

- **Fehler oder Wünsche:** bitte ein [Issue](https://github.com/sharpi13822/TPF3-Map-Studio/issues) eröffnen
- **Fragen, Ideen und Austausch:** in den [Discussions](https://github.com/sharpi13822/TPF3-Map-Studio/discussions)

Bei einem Fehler helfen diese Angaben: Version des Studios, Windows-Version, was du getan hast, die genaue Fehlermeldung (wenn vorhanden) und ob der Fehler jedes Mal auftritt. Screenshots sind willkommen. Bitte keine Kartendateien mit privaten Daten anhängen.

## Unterstützung

Das Studio ist kostenlos und entsteht in der Freizeit. Wenn es dir hilft und du die Weiterentwicklung unterstützen möchtest, freue ich mich über eine Spende. Sie ist freiwillig und verändert nichts an der Nutzung.

<a href="https://paypal.me/PEttelt"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="Mit PayPal spenden"></a>

## Lizenz

MIT, siehe [LICENSE](LICENSE). Hinweise zu den verwendeten Daten, Diensten und Bibliotheken stehen in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
