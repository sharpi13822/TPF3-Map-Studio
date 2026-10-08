# Third-party notices

[Deutsch](THIRD_PARTY_NOTICES.md) | **English**

The Studio itself is licensed under the MIT licence (see [LICENSE](LICENSE)). It uses public data sources, map services and libraries that are subject to their own licences and terms of use. This file summarises them. It is not legal advice. The providers' original texts are authoritative.

## Data

### OpenStreetMap

- Map data: © OpenStreetMap contributors
- Licence: Open Database License (ODbL) 1.0, <https://www.openstreetmap.org/copyright>
- The data is loaded through the Overpass API. The public Overpass servers have usage limits, so please do not send an excessive number of large queries in a short time.
- If you publish a map made from OSM data, credit "© OpenStreetMap contributors" and observe the ODbL.

### Digital terrain model DGM1 (Germany)

- Licence: Data licence Germany, attribution, version 2.0 (dl-de/by-2-0), <https://www.govdata.de/dl-de/by-2-0>
- The data providers are the survey administrations of the federal states. Which attribution applies depends on the area of the tiles used. The Studio shows it in the heightmap dialog, for example "© GeoBasis-DE / LVermGeoRP (2025), dl-de/by-2-0" for Rhineland-Palatinate.
- Access is through <https://hoehendaten.de>. The elevation data is not shipped with the Studio but obtained at download time.
- If you publish a map made from it, credit the source shown.

### swissALTI3D (Switzerland and Liechtenstein)

- Terrain model by swisstopo, used in the Studio at 2 m resolution. The tiles are obtained from <https://data.geo.admin.ch> when loading and are not shipped with the Studio.
- Terms of use: Open Government Data (OGD) by swisstopo, <https://www.swisstopo.admin.ch/en/terms-of-use-free-geodata-and-geoservices>. The data may be used, distributed, modified and also used commercially. **Attribution is mandatory**, for example "©swisstopo" or "Bundesamt für Landestopografie swisstopo".
- If you publish a map made from it, credit the source. The Studio shows it in the heightmap dialog: "© swisstopo (Bundesamt für Landestopografie swisstopo), swissALTI3D".
- In case of excessive use swisstopo may restrict access. The Studio loads only the tiles it needs, with a short pause in between, and keeps them in a cache.

### Copernicus DEM (GLO-30)

- Worldwide elevation model with about 30 m resolution, obtained through <https://copernicus-dem-30m.s3.amazonaws.com/>
- Notice from the data provider: "Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved."
- The Copernicus licence terms apply. Please check them before passing on derived data.

## Map services in the interface

The background maps are loaded from the internet when displayed and are not shipped with the Studio. Their attributions appear at the bottom right of the map.

| Service | Use | Note |
| --- | --- | --- |
| OpenStreetMap tiles (`tile.openstreetmap.org`) | Road map | © OpenStreetMap contributors. The [Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/) of the OpenStreetMap Foundation applies. For intensive use, a tile server of your own is intended. |
| OpenRailwayMap | Railway map as an overlay | Data © OpenStreetMap contributors, style CC-BY-SA 2.0 OpenRailwayMap, <https://www.openrailwaymap.org/>. The terms of use of OpenRailwayMap apply. |
| Hillshade | Switchable relief over the map | Computed in the browser from the "Terrain Tiles" (Terrarium format, `elevation-tiles-prod` on Amazon S3, project Tilezen/Joerd). The data comes from several sources, the attribution is at <https://github.com/tilezen/joerd/blob/master/docs/attribution.md> and at the bottom right of the map. |

## Libraries

The versions are listed in `requirements.txt`. Each package brings its own licence files.

| Library | Licence | Use |
| --- | --- | --- |
| [Leaflet](https://leafletjs.com/) | BSD 2-Clause | Map display |
| [PySide6 / Qt for Python](https://doc.qt.io/qtforpython/) (with Shiboken) | LGPL-3.0 (Qt for Python is also available under GPL-3.0 and commercially) | User interface |
| [requests](https://requests.readthedocs.io/) | Apache-2.0 | Downloads of OSM and elevation data |
| [NumPy](https://numpy.org/) | BSD 3-Clause | Elevation data calculations |
| [SciPy](https://scipy.org/) | BSD 3-Clause | Elevation data calculations, smoothing |
| [Pillow](https://python-pillow.org/) | MIT-CMU (HPND) | Image processing |
| [PyInstaller](https://pyinstaller.org/) | GPL-2.0 with an exception that does not bind built programs to the GPL | only for building the `.exe` |

`requests` brings further packages, including urllib3 (MIT), certifi (MPL-2.0), charset-normalizer (MIT) and idna (BSD 3-Clause). NumPy and SciPy also contain bundled libraries under their own licences, which are in the packages.

The map view runs in Qt WebEngine, which is based on Chromium. The licence notes for it are at <https://doc.qt.io/qt-6/qtwebengine-licensing.html>.

The finished `.exe` contains Qt in the form of libraries. The LGPL allows this but requires that Qt remains replaceable. The folder with the `.exe` contains the Qt files as individual libraries. Anyone who wants to replace Qt can also run the Studio from the source code at any time.

## Related projects

- [OSM-TPF2-Importer](https://github.com/Vacuum-Tube/OSM-TPF2-Importer) by Vacuum-Tube: an independent project for Transport Fever 2 under its own licence. The Studio no longer shows its importer functions but prepares data in a matching format.

## Trademarks

"Transport Fever" and "TPF" are trademarks of their respective owners. This project is unofficial and not affiliated with Urban Games or the publisher.
