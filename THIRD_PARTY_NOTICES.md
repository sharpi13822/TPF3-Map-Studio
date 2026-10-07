# Hinweise zu Drittanbietern

Das Studio selbst steht unter der MIT-Lizenz (siehe [LICENSE](LICENSE)). Es nutzt öffentliche Datenquellen, Kartendienste und Bibliotheken, die eigenen Lizenzen und Nutzungsbedingungen unterliegen. Diese Datei fasst sie zusammen. Sie ist keine Rechtsberatung. Maßgeblich sind jeweils die Originaltexte der Anbieter.

## Daten

### OpenStreetMap

- Kartendaten: © OpenStreetMap-Mitwirkende
- Lizenz: Open Database License (ODbL) 1.0, <https://www.openstreetmap.org/copyright>
- Die Daten werden über die Overpass API geladen. Die öffentlichen Overpass-Server haben Nutzungsgrenzen, bitte nicht übermäßig viele große Abfragen in kurzer Zeit stellen.
- Wer eine aus OSM-Daten erzeugte Karte veröffentlicht, nennt „© OpenStreetMap-Mitwirkende“ und beachtet die ODbL.

### Digitales Geländemodell DGM1 (Deutschland)

- Lizenz: Datenlizenz Deutschland, Namensnennung, Version 2.0 (dl-de/by-2-0), <https://www.govdata.de/dl-de/by-2-0>
- Datengeber sind die Vermessungsverwaltungen der Bundesländer. Welche Quellenangabe gilt, hängt vom Gebiet der verwendeten Kacheln ab. Das Studio zeigt sie im Heightmap-Dialog an, zum Beispiel „© GeoBasis-DE / LVermGeoRP (2025), dl-de/by-2-0“ für Rheinland-Pfalz.
- Der Zugang erfolgt über <https://hoehendaten.de>. Die Höhendaten werden nicht mit dem Studio ausgeliefert, sondern beim Download bezogen.
- Wer eine daraus erzeugte Karte veröffentlicht, nennt die angezeigte Quelle.

### swissALTI3D (Schweiz und Liechtenstein)

- Geländemodell von swisstopo, im Studio mit 2 m Auflösung genutzt. Die Kacheln werden beim Laden von <https://data.geo.admin.ch> bezogen und nicht mit dem Studio ausgeliefert.
- Nutzungsbedingungen: Open Government Data (OGD) von swisstopo, <https://www.swisstopo.admin.ch/en/terms-of-use-free-geodata-and-geoservices>. Die Daten dürfen genutzt, verbreitet, bearbeitet und auch kommerziell verwendet werden. **Die Quellenangabe ist Pflicht**, zum Beispiel „©swisstopo“ oder „Bundesamt für Landestopografie swisstopo“.
- Wer eine daraus erzeugte Karte veröffentlicht, nennt die Quelle. Das Studio zeigt sie im Heightmap-Dialog an: „© swisstopo (Bundesamt für Landestopografie swisstopo), swissALTI3D“.
- Bei übermäßiger Nutzung kann swisstopo den Zugriff einschränken. Das Studio lädt nur die nötigen Kacheln, mit kurzer Pause dazwischen, und legt sie im Zwischenspeicher ab.

### Copernicus DEM (GLO-30)

- Weltweites Höhenmodell mit etwa 30 m Auflösung, bezogen über <https://copernicus-dem-30m.s3.amazonaws.com/>
- Hinweis des Datengebers: „Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.“
- Es gelten die Lizenzbedingungen von Copernicus, bitte vor der Weitergabe abgeleiteter Daten prüfen.

## Kartendienste in der Oberfläche

Die Hintergrundkarten werden beim Anzeigen aus dem Internet geladen und nicht mit dem Studio ausgeliefert. Ihre Quellenangaben erscheinen unten rechts in der Karte.

| Dienst | Verwendung | Hinweis |
| --- | --- | --- |
| OpenStreetMap-Kacheln (`tile.openstreetmap.org`) | Straßenkarte | © OpenStreetMap-Mitwirkende. Es gilt die [Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/) der OpenStreetMap Foundation. Für intensive Nutzung ist ein eigener Kachelserver vorgesehen. |
| OpenRailwayMap | Eisenbahnkarte als Überlagerung | Daten © OpenStreetMap-Mitwirkende, Stil CC-BY-SA 2.0 OpenRailwayMap, <https://www.openrailwaymap.org/>. Es gelten die Nutzungsbedingungen von OpenRailwayMap. |
| Schattenrelief | Zuschaltbares Relief über der Karte | Wird im Browser aus den „Terrain Tiles“ (Terrarium-Format, `elevation-tiles-prod` auf Amazon S3, Projekt Tilezen/Joerd) berechnet. Die Daten stammen aus mehreren Quellen, die Namensnennung steht unter <https://github.com/tilezen/joerd/blob/master/docs/attribution.md> und in der Karte unten rechts. |

## Bibliotheken

Die Versionen stehen in `requirements.txt`. Jedes Paket bringt seine eigenen Lizenzdateien mit.

| Bibliothek | Lizenz | Verwendung |
| --- | --- | --- |
| [Leaflet](https://leafletjs.com/) | BSD 2-Clause | Kartendarstellung |
| [PySide6 / Qt for Python](https://doc.qt.io/qtforpython/) (mit Shiboken) | LGPL-3.0 (Qt for Python ist auch unter GPL-3.0 und kommerziell erhältlich) | Oberfläche |
| [requests](https://requests.readthedocs.io/) | Apache-2.0 | Downloads von OSM- und Höhendaten |
| [NumPy](https://numpy.org/) | BSD 3-Clause | Berechnung der Höhendaten |
| [SciPy](https://scipy.org/) | BSD 3-Clause | Berechnung der Höhendaten, Glättung |
| [Pillow](https://python-pillow.org/) | MIT-CMU (HPND) | Bildverarbeitung |
| [PyInstaller](https://pyinstaller.org/) | GPL-2.0 mit Ausnahme, die gebaute Programme nicht an die GPL bindet | nur zum Bauen der `.exe` |

`requests` bringt weitere Pakete mit, darunter urllib3 (MIT), certifi (MPL-2.0), charset-normalizer (MIT) und idna (BSD 3-Clause). Auch NumPy und SciPy enthalten mitgelieferte Bibliotheken unter eigenen Lizenzen, die in den Paketen liegen.

Die Kartenansicht läuft in Qt WebEngine, das auf Chromium aufbaut. Die Lizenzhinweise dazu stehen unter <https://doc.qt.io/qt-6/qtwebengine-licensing.html>.

Die fertige `.exe` enthält Qt in Form von Bibliotheken. Die LGPL erlaubt das, sie verlangt aber, dass Qt austauschbar bleibt. Der Ordner mit der `.exe` enthält die Qt-Dateien als einzelne Bibliotheken. Wer Qt ersetzen möchte, kann das Studio außerdem jederzeit aus dem Quellcode starten.

## Verwandte Projekte

- [OSM-TPF2-Importer](https://github.com/Vacuum-Tube/OSM-TPF2-Importer) von Vacuum-Tube: eigenständiges Projekt für Transport Fever 2 unter eigener Lizenz. Das Studio enthält seine Importer-Funktionen nicht mehr sichtbar, bereitet aber Daten im passenden Format auf.

## Marken

„Transport Fever“ und „TPF“ sind Marken ihrer jeweiligen Inhaber. Dieses Projekt ist inoffiziell und steht in keiner Verbindung zu Urban Games oder dem Herausgeber.
