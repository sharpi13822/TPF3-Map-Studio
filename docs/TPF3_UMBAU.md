# TPF3-Map-Studio: Umbau auf Transport Fever 3

Stand: 29.09.2026. Quelle der Fakten: offizielles Wiki https://wiki.transportfever3.com
(Seiten `gamemanual:mapsizes`, `gamemanual:gamemodes:mapeditor`, `gamemanual:installation:gamefilelocations`).
Alles unter "Verifiziert" steht so im Wiki. Alles unter "Offen" ist NICHT geprüft und darf nicht geraten werden.

## Verifiziert

### Heightmap
- 16-Bit-Graustufen-PNG. 1 Pixel = 4 x 4 m im Spiel. Kantenlänge in Metern = (Pixel - 1) * 4.
- Import im Karteneditor (Heightmap-Import) hat drei Felder:
  - `Minimum Height` = Höhe der komplett schwarzen Pixel
  - `Maximum Height` = Höhe der komplett weißen Pixel
  - `Water Level` = Höhe der Wasserebene. Das Wiki empfiehlt ausdrücklich 0 (beste Ergebnisse bei Biomen und Materialien).
- Es gibt nur EINEN flachen Wasserspiegel für die ganze Karte.
- Daraus folgt die universelle Formel (bei Wasserspiegel 0, Höhen relativ zum Fluss):
  - `Min = -Puffer_unten_m`
  - `Max = (H_Berg - H_Fluss) + Zuschlag_oben_m`
  - `Wasserspiegel = 0`
  - Puffer/Zuschlag stehen in `tpf3_universelle_import_tabelle.csv`.

### Kartengrößen (Breite x Höhe)
Angezeigte Werte im Spiel sind gerundet (bis 250 m Abweichung), exakt ist (Pixel-1)*4 m.
`*` = nur mit `experimentalMapFeatures = true` in der `settings.lua` (Userdata-Ordner) sichtbar.

| Größe \ Verhältnis | 1:1 | 1:2 | 1:3 | 1:4 | 1:5 |
|---|---|---|---|---|---|
| Tiny* | 1025x1025 px | 641x1281 | 513x1537 | 513x1537 | 385x1921 |
| Small | 2049x2049 | 1409x2817 | 1153x3457 | 1025x4097 | 897x4481 |
| Medium | 2817x2817 | 2049x4097 | 1665x4993 | 1537x6145 | 1281x6401 |
| Large | 3585x3585 | 2561x5121 | 2049x6145 | 1793x7169 | 1537x8065 |
| Very Large | 4097x4097 | 2817x5633 | 2305x6913 | 2049x8193 | 1793x8961 |
| Huge* | 5121x5121 | 3585x7169 | 2945x8833 | 2561x10241 | 2177x10881 |
| Megalomaniac* | 6145x6145 | 4225x8449 | 3457x10369 | 3073x12289 | 2689x13441 |
| Gigantomaniac* | 7169x7169 | 5121x10241 | 4097x12289 | 3585x14337 | 3201x16001 |

Kilometer-Werte: Größen in der CSV `tpf3_universelle_import_tabelle.csv` (Flächenspalten) bzw. (Pixel-1)*4.
Beispiel: Megalomaniac 1:5 = 10,752 x 53,760 km (= altes "Größenwahnsinnig 1:5").
Deutsche Namen im Spiel (Screenshot): Winzig, Klein, Mittel, Gross, Sehr gross, Riesig, Grössenwahnsinnig,
Gigantomanisch (Schreibweise mit "ss" statt "ß"). Kartenformat: 1:1 bis 1:5.
Im Dropdown waren alle acht Größen sichtbar; ob `experimentalMapFeatures` dafür an sein muss, ist ungeprüft.
Gigantomaniac scheint neu gegenüber TPF2.

### Aus dem Spiel bestätigt (Screenshots vom 30.09.2026)
- Heightmap-Import-Dialog: Felder `Mindesthöhe` (Standard -100), `Maximalhöhe` (Standard 500), `Wasserhöhe` (Standard 0),
  `Assets behalten` (Ja/Nein, Standard Nein). Negative Mindesthöhe ist also vorgesehen: `Min = -Puffer` passt.
- Der Dialog zeigt rechts eine Vorschau mit Kartengröße in km sowie die Zahl der Städte und Industrien (aus `towns_industries`).
- Biome-Tab hat drei getrennte Bilder: `Biome` (5 Biome, "Biom 0" bis "Biom 4"), `Berge`, `Flüsse`. Jeweils Ordner-Button und
  Löschen-Button, unten `Anwenden`. Es gibt also eine eigene Flüsse-Maske. Wie sich Flüsse daraus im Spiel verhalten
  (Gefälle? fester Pegel?), ist NICHT geprüft und wird zuerst getestet.
- Steam-Userdata ist nicht immer unter `C:\Program Files`: hier `D:\Steam\userdata\<Nummer>\3493540\local`.
  Das Studio muss den Pfad suchen (alle Laufwerke, Steam-Bibliotheken) oder einmal abfragen.
- Ordner vorhanden: biomes, heightmaps, towns_industries, save_maps, mods, staging_area, shader_cache, crash_dump ...
  Dateien: settings.lua (7 KB), settings_keys_v3.lua, profile.lua, console-history.lua, autosave.tree.lua.bak.

### Biome-Masken: im Spiel getestet (30.09.2026)
Testbilder 641 x 3201 (1:5) im Ordner `biomes`, im Biome-Tab je Slot gewaehlt. Ergebnis der Vorschau:
- `Biome`: 8-Bit-Graustufen. Fuenf gleich breite Intervalle. Grauwert 26 -> Biom 0, 77 -> Biom 1, 128 -> Biom 2,
  179 -> Biom 3, 230 -> Biom 4 (Mitten der Intervalle verwenden).
- `Berge`: weiss = Bergflaeche (schwarz = keine). Ellipse wurde als Bergflaeche dargestellt.
- `Fluesse`: weisse Linie wird als Fluss dargestellt.
- Masken werden auf die Kartengroesse gestreckt (wie die Heightmap): Seitenverhaeltnis muss zur Karte passen.
- Die Anzeige der Kartengroesse rundet offenbar: "12,5 x 62,5 km" (Gigantomanisch 1:5, Wiki 12,8 x 64) und
  "10,5 x 52,5 km" (Groessenwahnsinnig 1:5, Wiki 10,752 x 53,76). Die kurze Seite wird auf 0,5 km abgerundet, die lange
  ist das Fuenffache. Die Wiki-Tabelle bleibt damit die Referenz (noch nicht mit echten Pixelmassen gegengeprueft).
- Heightmap-Standardwerte (-100 / 500 / 0) aendern sich nicht mit der Kartengroesse.

### Schnee- und Felsgrenze: im Spiel getestet (01.10.2026)
Test mit `hoehen_schneegrenze_test.png` (12 flache Terrassen, je 50 m breit):
- Test A (0/600/0): Terrassen bei 25, 75, ... 575 m. Stufe 7 (325 m) gruen, Stufe 8 (375 m) grau (Fels), Stufe 9 (425 m) weiss (Schnee).
- Test B (0/1200/0): Terrassen bei 50, 150, ... Stufe 3 (250 m) gruen, Stufe 4 (350 m) grau, Stufe 5 (450 m) weiss.
- Ergebnis: Das Spiel faerbt nach der Hoehe UEBER DEM WASSERSPIEGEL, nicht nach dem Anteil der Hoehenspanne und nicht nach der absoluten Hoehe ueber NN. Fels beginnt zwischen ca. 325 und 350 m, Schnee zwischen ca. 375 und 425 m. Uebergaenge sind weich, die Werte sind Richtwerte.
- Die Berge-Maske (komplett schwarz) und die Flueesse-Maske aendern daran nichts.
- Rhein-Test (Koblenz-Bingen, Wasser 68 m): unbearbeitet ca. 574 m ueber Wasser -> grosse weisse Flaechen auf den Hochflaechen. Gestaucht auf 50 % (hoechste Stelle 287 m ueber Wasser): einzelne kleine weisse Flecken. Gestaucht auf 45 % (258 m): keine weissen Flaechen mehr, Hochflaechen gruen.
- Graue Streifen an steilen Haengen am Rhein bleiben (vermutlich Fels wegen der Neigung, nicht getestet). Graue Flaechen mit Gitter waren nur noch nicht fertig geladene Kartenteile.
- Umsetzung im Studio: `compress_heights` (src/heightmap/terrain_smoothing.py) staucht mit Knie: Die hoechste Stelle landet auf dem eingestellten Anteil (Standard-Empfehlung 45 %), der untere Teil (60 % der neuen Gipfelhoehe ueber Wasser) bleibt unveraendert, darueber wird logarithmisch gestaucht. Der Heightmap-Dialog warnt, wenn die hoechste Stelle mehr als 270 m ueber dem Wasser liegt (`WARN_HEIGHT_ABOVE_WATER_M`).
- Noch nicht geprueft: ob die Grenzen vom Klima/Biom der Karte abhaengen (getestet nur mit Standardbiom), und die Biome-Maske `biome_einheitlich_2.png` im Rhein-Test.

### Industrien (aus einem Spiel-Export, `industrien_test1.lua`, 01.10.2026, Karte 11 x 11 km)
Format je Industrie: `angle` (Bogenmaß), `fileName = "::/industries/<tag>/<tag>.con"`, `onWater`, `position = { x, y }` (Meter ab Kartenmitte, x Ost, y Nord), `tag`. Auf dieser Karte (18 Industrien) vorgekommen: `farm`, `fishing_grounds` (onWater = true), `oil_refinery`, `oil_platform` (onWater = true), `bricks_works`, `clay_pit`, `livestock_farm`, `saw_mill`, `forest`. Ein zweiter Export (`industrien_test2.lua`, andere Verteilung, ebenfalls 18 Industrien) enthielt keine weiteren Arten; ein dritter war identisch mit dem zweiten. KORREKTUR: Die neun sind NICHT die vollständige Liste. Laut Wiki (gamemanual:simulation:industriescargos) gibt es 32 Industrien; bei Kartenbeginn sind nur die Rohstoff-Industrien und wenige weitere vorhanden, die übrigen entstehen im Spiel, wenn die Nachfrage steigt. Die Städte beider Exporte sind identisch.
Wiki-Industrien (englische Namen) und im gemäßigten Klima (Temperate) verfügbar: Brewery, Brick Works, Chemical Plant, Clay Pit, Coal Mine, Cotton Farm, Crop Farm, Fishing Grounds, Canning Factory, Furniture Factory, Glass Works, Iron Ore Mine, Livestock Farm, Logging Camp, Machine Factory, Oil Platform, Oil Refinery, Oil Well, Quarry, Sand Excavator, Sand Pit, Saw Mill, Steel Mill, Textile Factory, Tool Factory, Vehicle Factory, Weaving Mill. Nicht im gemäßigten Klima: Cement Plant (tropical, subarctic), Paper Mill und Printing Press (subarctic), Rubber Farm (tropical), Tire Factory (tropical). Die Dateinamen der bestätigten neun (farm = Crop Farm, forest = Logging Camp, food_factory = vermutlich Canning Factory) stimmen mit den Icon-Namen im Wiki überein; die übrigen Namen wurden daraus abgeleitet und sind im Spiel BESTÄTIGT (Test `tpf3_test_industrienamen.lua`, 01.10.2026: alle 17 abgeleiteten Industrien erscheinen mit Namen): quarry, coal_mine, iron_ore_mine, sand_pit, oil_well, cotton_farm, steel_mill, machine_factory, tool_factory, vehicle_factory, glass_works, brewery, food_factory, furniture_factory, chemical_plant, textile_factory, weaving_mill.
Städte im selben Export: `landUse2CargoNeedsCategories` mit echten Waren, `com` = vegetables / fish / meat, `ind` = planks / bricks / fuel (je Stadt eine Kombination: vegetables+planks, fish+bricks, meat+fuel). `sizeFactors` im Spiel erzeugt z. B. { 1.03, 1.3, 0.9 } bis { 2.73, 3.53, 2.76 } (Bremen).
Im Studio (`src/heightmap/industries_export.py`, `src/gui/industries_dialog.py`, Knopf "Industrien aus OSM..." im Heightmap-Dialog): landuse=farmyard -> farm, building=cowshed/stable/sty -> livestock_farm, Steinbrüche/Minen nach `resource` (clay -> clay_pit, sand/gravel -> sand_pit, coal -> coal_mine, iron_ore -> iron_ore_mine, sonst quarry), industrial/craft/man_made=works+product für Sägewerk, Ziegelei, Raffinerie, Stahlwerk, Maschinen-, Werkzeug-, Fahrzeugfabrik, Glashütte, Brauerei, Konserven/Lebensmittel, Möbel, Chemie, Textil; man_made=petroleum_well -> oil_well, man_made=offshore_platform -> oil_platform, große landuse=forest-Flächen -> forest (Standard aus). Die OSM-Tags der Fabriken sind uneinheitlich; es trifft nur, was so eingetragen ist. Erster Test im Spiel (01.10.2026, Mittelrhein): Steinbrüche und Höfe sahen auf bewaldeten Hängen und am Rheinufer schlecht aus (das Spiel schneidet große Gruben in den Hang, Steinbruch senkrecht ins Wasser). Darum: Gruben/Minen (Lehm, Stein, Sand, Kohle, Eisenerz) standardmäßig aus; neue Prüfung im Dialog: höchster Höhenunterschied im Umkreis von 150 m (Standard 15 m) und Mindestabstand zu Gewässern (Standard 150 m), gerechnet auf dem exportierten Höhenraster und der Wassermaske. Ungetestet im Spiel. Schwerpunkt der Fläche, Mindestabstand und Höchstzahl je Art einstellbar, Haken je Objekt, Winkel immer 0, Datei enthält nur Industrien (beim Import "Städte behalten: Ja"). Zweiter Test im Spiel (Mittelrhein): Höfe auf flachen Hochflächen sehen gut aus; eine Viehzucht am Kartenrand ließ Felder und Hecken über den Rand ragen, darum Abstand zum Kartenrand (Standard 500 m). Der Overpass-Baukasten hat dafür den Haken "Industrie-Objekte" (standardmäßig an). Die Städte-Datei benutzt jetzt die echten Waren (vorher "fish"/"machines").

### Die fuenf Biome und die Biome-Maske aus OSM (im Spiel getestet, 01.10.2026)
Einheitliche Biome-Masken (Grauwert 26/77/128/179/230) auf einer Testkarte, so sieht jedes Biom aus:
- Biom 0 (26): helle, gruene Wiese ohne Baeume.
- Biom 1 (77): Wiese mit Baumgruppen und einzelnen Baeumen.
- Biom 2 (128): dunkle, bewachsene Wiese ohne Baeume.
- Biom 3 (179): trockene Steppe, gelbbraun mit einzelnen Grasflecken.
- Biom 4 (230): gruen-braun gemischt (Savanne). KEIN Schnee; die Legende (Biom 4 weiss) taeuschte. Schnee kommt nur von der Hoehe.
- Nur Biom 1 hat Baeume. Dichter Wald ist mit den Biomen nicht zu erreichen; fuer die Baumdichte gibt es im Biome-Tab keine Einstellung.

Biome-Maske aus OSM (`src/heightmap/biome_mask.py`, `src/gui/biome_dialog.py`, Knopf "Biome-Maske aus OSM..." im Heightmap-Dialog):
- Rastert die geladenen OSM-Flaechen (einfache Flaechen und Multipolygone mit Loechern) in ein 8-Bit-Bild, Norden oben, gleiche Ausrichtung wie die Heightmap. Aufloesung waehlbar (16/8/4 m pro Pixel), das Spiel streckt die Maske auf die Kartengroesse.
- Zuordnung (Vorschlag, im Dialog je Kategorie aenderbar): Wiese/Weide/Park -> 0, Wald -> 1, Moor/Sumpf/Heide -> 2, Acker/Weinberg/Obstbau -> 3, Fels/Sand/Abbau -> 3, Siedlung/Industrie/Gewerbe -> 4, alles andere und Wasser -> 0. Spaetere Kategorien ueberdecken fruehere (Reihenfolge in `CATEGORIES`).
- Test am Mittelrhein (Koblenz-Bingen, 1:5): Lage und Ausrichtung stimmen. Die Rheinschleife passt zwischen Studio und Spiel, zwei grosse Ackerflaechen liegen an denselben Stellen (ockerfarben im Spiel). Keine Spiegelung, kein Versatz erkennbar.
- Siedlung -> Biom 4 im Spiel angesehen (Bingen, 01.10.2026, Maske mit den neuen Overpass-Flächen: Biom 0 23 %, Biom 1 52 %, Biom 2 2 %, Biom 3 14 %, Biom 4 9 %): weicher Übergang, gefällt, bleibt Standard. Fels/Sand -> Biom 3 und Heide/Moor -> Biom 2 nicht gesondert beurteilt.
- Overpass-Baukasten (`src/osm/overpass_query_builder.py`, `src/gui/overpass_dialog.py`): "Orte (Städte, Dörfer)" ist jetzt standardmäßig an (Export "Städte aus OSM" braucht die Ortsknoten). Neuer Haken "Siedlung, Heide, Moor, Fels (für Biome)" (landuse residential/industrial/commercial/retail/quarry/brownfield/..., natural heath/scrub/wetland/grassland/bare_rock/scree/sand/..., auch als Multipolygone), ebenfalls standardmäßig an; ohne ihn bleiben diese Biome-Kategorien leer. Im Studio getestet (Biom 4 kommt mit 9 % in der Maske an); macht den OSM-Download größer.

### Ordner (Userdata)
- Steam/Windows: `C:\Program Files (x86)\Steam\userdata\<user-number>\3493540\local`
- GOG/Epic/Windows: `C:\Users\<username>\AppData\Roaming\Transport Fever 3`
- Darin: `heightmaps`, `biomes`, `towns_industries`, `save_maps`, `mods`, `staging_area`, `settings.lua`, `crash_dump`.

### Städte und Industrien (`towns_industries`, Lua)
```
function data()
return {
  industries = {
    { angle = -0.218669, fileName = "::/industries/farm/farm.con",
      onWater = false, position = { x = -1240, y = 3072 }, tag = "farm" },
  },
  towns = {
    { landUse2CargoNeedsCategories = { com = { { "fish", 1 } }, ind = { { "machines", 0.5 } } },
      name = "Gausdal", position = { x = -3239.97, y = -6574.89 },
      sizeFactors = { 1.11, 1.19, 1.03 } },
  }
}
end
```
Koordinaten x/y in Metern. Ursprung = KARTENMITTE, x nach Osten, y nach Norden (im Spiel getestet 01.10.2026 mit `tpf3_test_ursprung.lua`: T0 (0/0) in der Mitte, T2 (y +5000) oben, T3 (y -5000) unten, T1 (x +1000) rechts von T0). Das Spiel nimmt die Datei mit den Feldern aus dem Beispiel an und zählt die Städte. Einwohner (getestet 01.10.2026, flache Testkarte, nur eine Zahl verändert): Die MITTLERE Zahl von `sizeFactors` skaliert die Anfangs-Einwohner. Faktor 1 -> 97-99, 3 -> 298, 5 -> 500, 10 -> 999, 30 -> 2892, 100 -> nur 4476 (Obergrenze, nicht 10000). Die erste und dritte Zahl (je 3 getestet) ändern die Einwohner nicht. Im Studio: Faktor = Maßstab (Standard 0,03) × Wurzel(OSM-Einwohner), begrenzt auf 0,2 bis 30 (alles einstellbar): Koblenz ca. 10 (~1000 Einwohner), Bingen ca. 4,8, Dörfer mit 300 Einwohnern ca. 0,5, mit 100 ca. 0,3. Im Spiel getestet (01.10.2026, Rhein-Karte): Koblenz 979, Bingen 478, Waldalgesheim 189 Einwohner, wie berechnet. Der Städte-Dialog hat Haken je Ort, exportiert wird nur die Auswahl. Faktoren unter 1 gehen (getestet 01.10.2026, `tpf3_test_klein.lua`): 0,2 -> 19, 0,5 -> 50, 0,8 -> 79, 1 -> 98 Einwohner, also etwa 98 je Faktor. Kleinster Faktor im Studio: 0,2 (darunter ungetestet). Offen: was die erste und dritte Zahl von `sizeFactors` und `landUse2CargoNeedsCategories` bewirken (im Studio Standardwerte 1.0 und Beispiel-Frachtbedürfnisse).

### Biome
- Export aus einer generierten Karte mit `Biomes Data` liefert Masken-Bilder; Import aus dem Ordner `biomes`.
- Maske `Biomes`: Graustufen, 0 bis 100 % in gleich große Intervalle je Anzahl Biome. Weitere Masken: schwarz/weiß.

## Offen (erst prüfen, nicht raten)
1. Format der TPF3-Mods/Constructions (Straßen, Gleise, Gebäude). Wiki: `modding:general:moddefinition`, `modding:constructions:basics`, `modding:infrastructure:tracksstreets`.
2. Ob der externe OSM-Importer (`main.exe`) TPF3 unterstützt oder ersetzt werden muss.
3. Ob das vorhandene `TPF2Exporter` / `TPF2LuaWriter` für TPF3 taugt.
4. Namen und Ordnerlayout der Biome-Masken (an echtem Export aus dem Spiel ablesen).
5. (erledigt) Koordinatenursprung in `towns_industries`: Kartenmitte, x Ost, y Nord (siehe oben).
6. (erledigt) Deutsche Namen der Kartengrößen: siehe oben.
7. Farb-/Graustufen-Codierung der drei Biome-Masken (Biome, Berge, Flüsse): an einem Export aus dem Spiel ablesen.
8. Verhalten der Flüsse-Maske im Spiel (Gefälle möglich?) durch Testimport klären, bevor die Gewässer-Anpassung
   der Heightmap gebaut wird.

## Aufgaben

### Phase 1: Daten und Texte (klein, sicher)
Stand 30.09.2026: Größen, Import-Werte-Text, Gewässer-Anpassung (Höhenschwelle, Bäche ausgenommen,
Einstellungen bleiben nach dem Download) und Pfadsuche sind umgesetzt (map_size_presets.py, heightmap_dialog.py,
water_terrain_blend.py, tpf3_paths.py). Offen bleibt der Test im Spiel.
- [ ] `src/gui/map_size_presets.py`: acht Größen x fünf Verhältnisse aus der Tabelle oben, mit Pixelmaßen, `experimental`-Flag, 4 m/Pixel. Bezeichnungen bleiben abwärtskompatibel ("Größenwahnsinnig 1:5" muss weiter gefunden werden).
- [ ] Heightmap-Export: 16-Bit-PNG, Pixelmaße exakt aus der Tabelle, Höhenfenster nach obiger Formel, Anzeige "Trage im Spiel ein: Min / Max / Water Level 0".
- [ ] `tpf3_universelle_import_tabelle.csv` einlesen (`encoding="utf-8-sig"`, Trenner `;`). Unbekannte Größe: Zeile mit ähnlichster Fläche im gleichen Verhältnis-Block.
- [ ] Texte TPF2 -> TPF3: `import_guide_dialog.py`, `feature_overview_dialog.py`, `converter_command_dialog.py`, `mod_checker_dialog.py`, `preflight_dialog.py`.
- [ ] Nutzerhinweis: Tiny/Huge/Megalomaniac/Gigantomaniac brauchen `experimentalMapFeatures = true`.

### Phase 2: Heightmap-Qualität (gemeinsam)
- [ ] Gewässer-Anpassung: Flüsse/Seen aus OSM auf Wasserspiegel bringen, Umgebung sanft mitnehmen (Übergangsbreite einstellbar), Bett-Tiefe begrenzen.
- [x] Schnee-/Felsgrenze ermittelt, Stauchen mit Knie und Warnung im Dialog (siehe oben)
- [ ] Nebenflüsse weit über dem Pegel: nur flache Rinne, kein Wasser (Schwellwert einstellbar).
- [ ] Optional: Glättung gegen Baumkronen im Copernicus-Modell.
- [ ] Vorher/Nachher-Vorschau im Heightmap-Dialog.
- [ ] Testgebiete: Bonn-Koblenz (Rhein + Nebenflüsse), Mittelrhein bei der Loreley.

### Phase 3: Export für das Spiel
- [ ] Ausgabe direkt in den Userdata-Ordner (`heightmaps`, `towns_industries`), Pfad automatisch suchen (Steam-App-ID 3493540) oder einmal abfragen.
- [x] `towns_industries`-Lua aus OSM-Orten erzeugen (Städte): `src/heightmap/towns_export.py`, `src/gui/towns_dialog.py`, Knopf "Städte aus OSM..." im Heightmap-Dialog. Mit echten OSM-Orten am Mittelrhein im Spiel getestet (01.10.2026, 80 Orte gefunden, Import funktioniert). Industrien fehlen (Dateinamen der Industrien aus dem Spiel nötig). Die Overpass-Abfrage lädt die Orte mit (`node["place"~"^(city|town|village|hamlet)$"]`).
- [x] Biome-Masken aus OSM-Landnutzung erzeugen (siehe oben, getestet am Mittelrhein).
- [ ] Straßen/Gleise/Gebäude: erst nach Klärung von "Offen" 1 bis 3.

### Phase 4: Studio-Fehler und Aufräumen
- [x] Layer-Dock links (`layer_dock.py`, `layer_panel.py`, `layer_row.py`) an den Startzustand "Ebenen aus" angleichen.
- [x] `layer_control.js`: "Alle"/"Keine" nur auf Checkboxen anwenden, nicht auf Radio-Knöpfe. (Im Code schon so; die Knöpfe schalten nur Eisenbahnkarte und Maß-Gitter, bewusst so gelassen.)
- [x] `layer_row.py`: doppeltes `__init__` entfernen. (Im aktuellen Stand nur ein `__init__`.)
- [ ] Optional: Waldflächen am Auswahlrand beschneiden.
- [x] Schloss im Layer-Dock sperrt Auswahl und Bearbeitung in der Karte (`window.py`, `map.js`: `setLayerLocked`). Getestet.
- [x] Zeichnen (Straße, Fluss, Gebäude): die passende Ebene wird automatisch eingeschaltet. Getestet (01.10.2026).
- [x] Verschobene, neue und gelöschte Punkte an OSM-Wegen werden gespeichert. Getestet (01.10.2026).
- [x] Hilfetexte: Schloss und Zeichnen erklärt, TPF2 -> TPF3 in Punkt 7 der Hilfe.

## Arbeitsregeln
- Nur EINE Kopie des Projekts. Änderungen immer per Git-Branch (`tpf3`) und Commit.
- Beim Test aus dem Quellcode starten (`python src/main.py`), nicht jedes Mal die `.exe` bauen. `console=False` in `build.spec` nur fürs Release.
- Wichtige Dateien: `src/window.py` (Hauptfenster, OSM-Worker-Thread), `src/map/map_controller.py`, `src/map/web/js/map.js`, `src/map/web/index.html`, `src/gui/docks.py`.
