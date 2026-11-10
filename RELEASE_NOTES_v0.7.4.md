# TPF3 Map Studio v0.7.4

Mehrere Höhenquellen in einer Karte kombinieren, z. B. an Landesgrenzen. / Combine several height sources in one map, e.g. along national borders.

## Deutsch

Neu
- Höhenquellen kombinieren: Im Heightmap-Dialog lassen sich über „Quellen kombinieren...“ bis zu drei Höhenquellen in einer Karte nutzen, zum Beispiel DGM1 Rheinland-Pfalz und Luxemburg MNT 2024 an der Mosel. Die gewählte Quelle hat Vorrang, die Reihenfolge der weiteren Quellen legst du mit Pfeilen fest; Copernicus steht immer an letzter Stelle und füllt nur Lücken. Angeboten werden nur Quellen, die das Rechteck berühren. An der Grenze gleicht das Studio einen festen Höhenversatz zwischen den Quellen aus und blendet auf einstellbarer Breite weich über (Standard 150 m, 0 m = harte Kante). Nach dem Laden zeigt der Dialog, wie viel Fläche aus welcher Quelle stammt. Die Auswahl wird im Projekt und im Kartenrezept gespeichert, die Beschreibung zum Teilen nennt alle Quellen mit Quellenangabe und Lizenz. Danke an Psc0905 für die Anregung.

Behoben
- DGM1 an Landesgrenzen: Reichte das Rechteck über die deutsche Grenze, brach der Download mit „HTTP 400“ ab. Kacheln jenseits der Grenze werden jetzt übersprungen, dort übernimmt die nächste Quelle.
- Beschreibung zum Teilen: Bei der Höhenquelle BEV Österreich stand „Copernicus“, und die vorgeschriebene BEV-Quellenangabe (CC BY 4.0) fehlte.
- Projekte mit der Höhenquelle BEV Österreich oder Luxemburg MNT 2024 öffneten mit Copernicus statt mit der gespeicherten Quelle.

Installation: `TPF3-Map-Studio-v0.7.4-win64.zip` herunterladen, die ganze ZIP entpacken, `TPF3-Map-Studio.exe` starten. Windows warnt beim ersten Start eventuell („Weitere Informationen“ -> „Trotzdem ausführen“), bei PyInstaller-Programmen sind Virenscanner-Fehlalarme bekannt.

SHA-256: `6e55c197633cacadf7f0ad01604d97630a8843bb76f3a330f16b77dc9f1ce53b`

Hinweis: inoffizielles Werkzeug, keine Verbindung zu Urban Games.

„Kaffeekasse – Freiwillig & von Herzen! ❤️“ https://paypal.me/PEttelt?locale.x=de_DE&country.x=DE

## English

New
- Combine height sources: in the heightmap dialog, “Combine sources...” lets you use up to three height sources in one map, for example DGM1 Rhineland-Palatinate and Luxembourg MNT 2024 along the Moselle. The selected source has priority and you set the order of the further sources with arrows; Copernicus always comes last and only fills gaps. Only sources that touch the rectangle are offered. At the border the studio corrects a constant height offset between the sources and blends smoothly across an adjustable width (default 150 m, 0 m = hard edge). After loading, the dialog shows how much of the area comes from which source. The selection is saved in the project and in the map recipe, and the share description lists every source with attribution and licence. Thanks to Psc0905 for the suggestion.

Fixed
- DGM1 at national borders: if the rectangle reached across the German border, the download stopped with “HTTP 400”. Tiles beyond the border are now skipped and the next source takes over there.
- Share description: with the height source BEV Austria it said “Copernicus”, and the required BEV attribution (CC BY 4.0) was missing.
- Projects using BEV Austria or Luxembourg MNT 2024 as height source opened with Copernicus instead of the saved source.

Install: download `TPF3-Map-Studio-v0.7.4-win64.zip`, extract the whole ZIP, run `TPF3-Map-Studio.exe`. Windows may warn on first start ("More info" -> "Run anyway"); antivirus false positives are known for PyInstaller programs.

SHA-256: `6e55c197633cacadf7f0ad01604d97630a8843bb76f3a330f16b77dc9f1ce53b`

Note: unofficial tool, not affiliated with Urban Games.

“Coffee fund – Voluntary & from the heart! ❤️” https://paypal.me/PEttelt?locale.x=de_DE&country.x=DE
