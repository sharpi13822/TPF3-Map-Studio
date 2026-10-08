# Heightmap from TPF3 Map Studio to Transport Fever 3

[Deutsch](ANLEITUNG_HEIGHTMAP.md) | [English](ANLEITUNG_HEIGHTMAP.en.md)

This guide leads step by step from an empty map to a finished heightmap imported in the game.
Whatever has not been tested in the game yet is marked where it appears.

The program itself is in German for now. Menu and button names are given as they appear in the program, with a translation in brackets where useful.

---

## Part A: In the Studio

### 1. Set the map area
1. Start the Studio. In the panel on the map, under **Kartenquelle** (map source), best choose **Karte + Relief** (map + relief). This shows valleys and slopes.
2. Zoom to the area you want. With the **Marker** tool, place a marker in the middle (optional, the marker later provides the centre point).
3. Open **Werkzeuge → Rechteck-Tool** (Tools → Rectangle tool):
   - check the **Mittelpunkt** (centre, it comes from the marker),
   - choose the **Kartengröße** (map size) exactly as in the game (Winzig to Gigantomanisch, i.e. Tiny to Gigantomaniac, ratio 1:1 to 1:5),
   - adjust the **Drehwinkel** (rotation) until the band fits your river or route,
   - **OK**. The blue band shows what will be loaded later. You can move it with the blue dot and rotate it with the orange one.

### 2. Load OSM data
4. **Werkzeuge → OSM laden** (Tools → Load OSM) and wait. Large areas take a few minutes, the status bar shows progress.
5. Switch the layers on in the **Layer dock on the left** to check the result (all are off at start).

Without OSM data, the options "Wasser nur dort, wo OpenStreetMap Wasser hat" (water only where OpenStreetMap has water) and "Trassen und Siedlungen einebnen" (level routes and settlements) do not work.

### 3. Get elevation data
6. Open **Werkzeuge → Heightmap herunterladen** (Tools → Download heightmap).
7. At the top of the dialog choose the **Höhenquelle** (elevation source):
   - **Copernicus** (worldwide, 30 m, includes tree canopy) is the default and available everywhere.
   - **DGM1 Deutschland** (1 m) loads tiles through hoehendaten.de, about 20 tiles per minute. Large maps take half an hour.
   - **DGM1 from your own GeoTIFF tiles** (folder), if you downloaded the tiles yourself from a state portal.
   - **swissALTI3D** (Switzerland and Liechtenstein, 2 m) from swisstopo, only selectable for maps there. Attribution is mandatory (see below).

   Optional: **Schnellvorschau** (quick preview, a rough image from Copernicus, available immediately, not exportable).
8. **Höhendaten herunterladen** (download elevation data) and wait. The first time, the Studio loads the tiles and keeps them in the cache. After that it is faster. Where a source has no data, the Studio fills the gaps from Copernicus. At the top it finally says "Geladen: … Pixel".

### 4. Settings in the dialog
**Quick start:** at the top of the dialog under **Voreinstellung** (preset) choose "Empfohlen" (recommended: smoothing, levelling, water from OSM with the default values) or "Original" (all options off, real heights). With the DGM1 (1 m) the default values for smoothing and levelling are smaller (10 m) because the model is already precise. The preset jumps to "Eigene Einstellungen" (custom) as soon as you change something by hand. Options that need OSM data stay off without loaded OSM data.

Recommended order. Every change updates the preview. The numbers at the bottom of the dialog change with it.

9. Check the **Wasserhöhe** (water level). The Studio suggests a value. Tip: a little above the lowest part of the river, but not so high that the river is more than 10 to 15 m above the level at its highest point. For river valleys with a gradient (for example the Rhine) this is a compromise. The button **"Wasserhöhe aus den OSM-Gewässern vorschlagen"** (suggest water level from OSM waters) sets it halfway between the lowest and highest point of the main river and adjusts the limit "Nur Gewässer bis" (needs OSM data).
10. Tick **Gelände glätten** (smooth terrain), default 15 m. This removes the terraces on slopes (the elevation model has only 30 m per pixel, the game 4 m).
11. Tick **Trassen und Siedlungen einebnen**, default 60 m. Railway lines, larger roads and buildings are flattened so that fewer ramps are needed in the game. Needs OSM data. (Whether it helps noticeably when building has not been tested in the game yet.)
12. Tick **Wasser nur dort, wo OpenStreetMap Wasser hat** (recommended). This prevents flooded floodplains and ponds. Default values:
    - embankment 60 m (wider = flatter bank),
    - depth at the bank 2 m, depth in the middle 8 m (channel),
    - bank above water 2 m,
    - only waters up to 15 m above the water level (higher streams and mountain lakes stay unchanged).

    The option **"Terrain sanft ans Wasserniveau anpassen"** (adapt terrain softly to the water level) switches off here, the two do not work together.
13. **Höhen stauchen** (squash heights) against white and grey areas on the heights. The game colours by the height above the water: rock from about 325 to 350 m, snow from about 375 to 425 m. The highest point ends up at the set share of its height above the water; the lower part of the terrain stays unchanged. On the Rhine (574 m above water) **45 %** worked. The dialog warns when the highest point is more than 270 m above the water. Default 100 % = unchanged.
14. **Gefälle ausgleichen** (equalise gradient) only when needed and with care: it shifts all heights. Default: strength 100 %, smoothing 400 m, reference: waters up to 30 m above the water level. The numbers for the game change a lot, so always use the new ones.
15. **Höhenfenster begrenzen** (limit height window, checkbox). The TPF3 map editor accepts only heights from **−20 to 3177 m** on import (tested in the game). If your terrain lies outside, for example in the Alps, you place a window over it here. It acts last, after smoothing and squashing. The values are entry values, i.e. the numbers you enter in the game (relative to the water if "Werte auf Wasserhöhe 0 beziehen" is ticked).
    - **Mode:** *Oben kappen* (cap the top) sets peaks flat to the upper limit, *Unten abschneiden* (cut the bottom) sets lows flat to the lower limit, *Stauchen* (squash) presses the whole terrain into the window without stretching it. The water level is preserved.
    - **Setting the window:** with the two fields (lower and upper) and the **slider**, which spans the whole range of the editor. If the terrain already fits completely, you move the window with the slider and see at once what drops out.
    - **Preview:** red is lowered (capped or squashed), cyan is raised (cut off). One line says how many percent of the area are levelled.
    - While the window is on, the option for outliers is ignored.

### 5. Check and export
16. Check in the preview: the river should be a continuous band in the valley, no straight stripes or wedges, no ponds except those from OSM.
17. **Read the text at the bottom of the dialog** and copy it down or photograph it:
    > Im TPF3-Import eintragen: Mindesthöhe …, Maximalhöhe …, Wasserhöhe …
    > Kartengröße und -format im Spiel: …

    (Enter in the TPF3 import: minimum height …, maximum height …, water level …; map size and format in the game: …)

    These are the **real heights** (positive values above sea level). They always apply to exactly the current settings. With the checkbox **"Werte auf Wasserhöhe 0 beziehen"** (relate values to water level 0) you switch to the variant the TPF3 wiki recommends for biomes and materials (the minimum height may then become negative). With real heights everything lies correspondingly higher in the game, so white areas on the heights may increase.
18. **Exportieren…** (export). The dialog suggests the TPF3 heightmaps folder (on Steam for example `…\userdata\<number>\3493540\local\heightmaps`). **Give the file a unique name**, for example `rhein_osmwasser.png`.

---

## Part B: In TPF3

19. Open the map editor. In the settings under **Welt** (world) choose the same **map size** and the same **map format** as in the Studio text. Only then does the aspect ratio fit. The game stretches every image to the map size.
    If a size is missing (for example Gigantomanisch), the wiki says the switch `experimentalMapFeatures` in `settings.lua` in the user data folder is responsible.
20. Open the **Heightmap importieren** dialog (import heightmap, tab **Heightmap**).
21. Click the exported file in the list. If it is not there: close the dialog and reopen it, and check that the file really is in the `heightmaps` folder.
22. Enter the values from step 17:
    - **Mindesthöhe**, **Maximalhöhe** and **Wasserhöhe** exactly as in the Studio text,
    - **Assets behalten: Nein** (keep assets: no).
23. Look at the preview on the right: is the shape right? Is only the river under water (blue)?
24. Click **Import**.

### Optional: trees and materials (tab Biome)
25. The biome mask determines the distribution of trees. A uniform mask is enough for a test (grey value 77 = biome 1, 128 = biome 2, 179 = biome 3, one file each in the `biomes` folder). Under **Biome** choose the file, leave **Berge** (mountains) and **Flüsse** (rivers) empty, **Anwenden** (apply).
    In the test the rivers mask does not create a river, and the mountains mask does not remove white areas.

---

## Part C: If something is wrong

| Problem | Cause and solution |
|---|---|
| The river is a huge lake | The game knows only one water level and floods the floodplain. Tick **"Wasser nur dort, wo OpenStreetMap Wasser hat"**. |
| The river runs dry in places | Raise the water level in the Studio a little. Read the values for the game again. |
| The river stays dry in the upper part (steep gradient, e.g. Koblenz–Bingen about 18 m) | With "Wasser nur dort, wo OpenStreetMap Wasser hat" raise the limit **"Nur Gewässer bis … m über Wasserspiegel"** to 25 to 30 m. Also put the water level halfway between the lowest and highest river section (about 68 m there). Not tested in the game yet. |
| Steep wall at the bank | Raise the embankment from 60 to 100 m. In gorges (Middle Rhine) part of it is natural. |
| Terraces on the slopes | **Gelände glätten**, 15 m, 30 m if needed. |
| Straight stripes or wedges in the water | This was an error when joining the OSM bank pieces. Fixed in the current version. |
| Warning "Der Karteneditor nimmt nur Höhen von -20 bis 3177 m" | Your range lies outside what the editor accepts. Tick **Höhenfenster begrenzen** (step 15) or use **Höhen stauchen**. |
| Nothing changes in the height window | The terrain lies completely inside the window. Make the window smaller or move it with the slider or narrower fields. |
| White areas on the heights | Snow line in the game. Do the terrace test and use **Höhen stauchen**. |
| Grey rock stripes on steep slopes | From a certain slope the game colours rock. Soften the slopes with the embankment or with squashing. |
| The terrain is distorted in the game | Map size or map format in the game does not match the Studio text. |
| Wrong heights in the game | Use the numbers at the bottom of the Studio dialog, not old values. They change with every option. |
| Message "Keine Gewässer" (no waters) | First **Werkzeuge → OSM laden** for the same area. |
| Error "Map preview exception … No such file" in the game | The file was deleted or renamed. Reopen the dialog and choose the file again. |

### Snow line test (one-off)
The test file `hoehen_schneegrenze_test.png` has twelve terraces from 25 m to 575 m in 50 m steps, lowest at the bottom.
1. Copy the file to `heightmaps`.
2. In the game choose the same map size (format 1:5) as in the guide above.
3. Import with **minimum height 0, maximum height 600, water level 0**.
4. Count from the bottom at which terrace white begins. Height = 25 + 50 × (number − 1).

---

## Sources you should credit on published maps
Credit the source of the elevation data you used. The heightmap dialog shows the exact wording.
- Heights worldwide (Copernicus): Copernicus DEM GLO-30, © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018, provided under COPERNICUS by the European Union and ESA.
- Heights Germany (DGM1): depending on the federal state, Data licence Germany, attribution, version 2.0 (dl-de/by-2-0), for example "© GeoBasis-DE / LVermGeoRP (2025), dl-de/by-2-0" for Rhineland-Palatinate.
- Heights Switzerland and Liechtenstein (swissALTI3D): © swisstopo (Bundesamt für Landestopografie swisstopo). **Attribution is mandatory.**
- Map and water data: © OpenStreetMap contributors.
- Relief background in the Studio (display only): AWS Terrain Tiles (Mapzen/Tilezen).
