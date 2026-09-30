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
Koordinaten x/y in Metern (Ursprung vermutlich Kartenmitte: ungeprüft).

### Biome
- Export aus einer generierten Karte mit `Biomes Data` liefert Masken-Bilder; Import aus dem Ordner `biomes`.
- Maske `Biomes`: Graustufen, 0 bis 100 % in gleich große Intervalle je Anzahl Biome. Weitere Masken: schwarz/weiß.

## Offen (erst prüfen, nicht raten)
1. Format der TPF3-Mods/Constructions (Straßen, Gleise, Gebäude). Wiki: `modding:general:moddefinition`, `modding:constructions:basics`, `modding:infrastructure:tracksstreets`.
2. Ob der externe OSM-Importer (`main.exe`) TPF3 unterstützt oder ersetzt werden muss.
3. Ob das vorhandene `TPF2Exporter` / `TPF2LuaWriter` für TPF3 taugt.
4. Namen und Ordnerlayout der Biome-Masken (an echtem Export aus dem Spiel ablesen).
5. Koordinatenursprung in `towns_industries` (an echtem Export ablesen).
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
- [ ] Nebenflüsse weit über dem Pegel: nur flache Rinne, kein Wasser (Schwellwert einstellbar).
- [ ] Optional: Glättung gegen Baumkronen im Copernicus-Modell.
- [ ] Vorher/Nachher-Vorschau im Heightmap-Dialog.
- [ ] Testgebiete: Bonn-Koblenz (Rhein + Nebenflüsse), Mittelrhein bei der Loreley.

### Phase 3: Export für das Spiel
- [ ] Ausgabe direkt in den Userdata-Ordner (`heightmaps`, `towns_industries`), Pfad automatisch suchen (Steam-App-ID 3493540) oder einmal abfragen.
- [ ] `towns_industries`-Lua aus OSM-Orten erzeugen (Format oben).
- [ ] Biome-Masken aus OSM-Landnutzung erzeugen (erst Beispielexport aus dem Spiel ansehen).
- [ ] Straßen/Gleise/Gebäude: erst nach Klärung von "Offen" 1 bis 3.

### Phase 4: Studio-Fehler und Aufräumen
- [ ] Layer-Dock links (`layer_dock.py`, `layer_panel.py`, `layer_row.py`) an den Startzustand "Ebenen aus" angleichen.
- [ ] `layer_control.js`: "Alle"/"Keine" nur auf Checkboxen anwenden, nicht auf Radio-Knöpfe.
- [ ] `layer_row.py`: doppeltes `__init__` entfernen.
- [ ] Optional: Waldflächen am Auswahlrand beschneiden.

## Arbeitsregeln
- Nur EINE Kopie des Projekts. Änderungen immer per Git-Branch (`tpf3`) und Commit.
- Beim Test aus dem Quellcode starten (`python src/main.py`), nicht jedes Mal die `.exe` bauen. `console=False` in `build.spec` nur fürs Release.
- Wichtige Dateien: `src/window.py` (Hauptfenster, OSM-Worker-Thread), `src/map/map_controller.py`, `src/map/web/js/map.js`, `src/map/web/index.html`, `src/gui/docks.py`.
