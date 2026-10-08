# Game knowledge: what applies in the Transport Fever 3 map editor

[Deutsch](SPIELWISSEN.md) | [English](SPIELWISSEN.en.md)

Measurements and observations the Studio is based on. They come from the [official wiki](https://wiki.transportfever3.com) and from our own tests in the game (October 2026). The game may change with updates, and the values are rules of thumb. If you measure something different, please open an [issue](https://github.com/sharpi13822/TPF3-Map-Studio/issues).

Unofficial, not affiliated with Urban Games or the publisher. The game is German-localised in our tests, so German in-game names are given in brackets where useful.

## Heightmap

- 16-bit greyscale PNG. One pixel equals 4 × 4 m in the game. Edge length in metres = (pixels − 1) × 4.
- The import has three fields: **minimum height** (height of the black pixels), **maximum height** (height of the white pixels) and **water level**. The wiki recommends water level 0 for the best results with biomes and materials.
- There is only **one flat water level** for the whole map.
- Defaults in the dialog: −100 / 500 / 0. They do not change with the map size.
- **Editor limits (tested in the game):** the import accepts heights from **−20 to 3177 m** (span 3197 m). Nothing beyond that. For higher terrain, the Studio's height window helps (cap peaks, cut off lows or squash). The height window itself has been tested in the game and works.
- The Studio's formula with water level 0 and heights relative to the river: minimum = −buffer below, maximum = (mountain height − river height) + margin above.

## Snow and rock

Test with twelve flat terraces from 25 to 575 m (imported with water 0):

- The game colours by **height above the water level**, not by share of the height range and not by height above sea level.
- Rock starts between about **325 and 350 m**, snow between about **375 and 425 m** above the water. The transitions are soft.
- The mountains and rivers masks change nothing about this.
- Example Middle Rhine (water at 68 m): unprocessed about 574 m above water, large white areas on the plateaus. Squashed to 45 % (258 m above water) there were no white areas left.
- Grey streaks on steep slopes remained, probably rock because of the slope (not checked). Whether the limits depend on climate or biome is not checked (tested only with the default biome).

## Map sizes

Exact is (pixels − 1) × 4 m. The in-game display rounds. Sizes marked `*` appear according to the wiki only with `experimentalMapFeatures = true` in `settings.lua` (whether that is required for selecting them in the game is unchecked).

| Size \ ratio | 1:1 | 1:2 | 1:3 | 1:4 | 1:5 |
|---|---|---|---|---|---|
| Tiny* | 1025×1025 | 641×1281 | 513×1537 | 513×1537 | 385×1921 |
| Small | 2049×2049 | 1409×2817 | 1153×3457 | 1025×4097 | 897×4481 |
| Medium | 2817×2817 | 2049×4097 | 1665×4993 | 1537×6145 | 1281×6401 |
| Large | 3585×3585 | 2561×5121 | 2049×6145 | 1793×7169 | 1537×8065 |
| Very Large | 4097×4097 | 2817×5633 | 2305×6913 | 2049×8193 | 1793×8961 |
| Huge* | 5121×5121 | 3585×7169 | 2945×8833 | 2561×10241 | 2177×10881 |
| Megalomaniac* | 6145×6145 | 4225×8449 | 3457×10369 | 3073×12289 | 2689×13441 |
| Gigantomaniac* | 7169×7169 | 5121×10241 | 4097×12289 | 3585×14337 | 3201×16001 |

(Pixels, width × height.) Example: Megalomaniac 1:5 is 10.752 × 53.76 km, the old "Größenwahnsinnig 1:5" (the largest scale of Transport Fever 2).

## Biome masks

Three separate images in the biome tab: **biomes**, **mountains** and **rivers**. All are stretched to the map size, so the aspect ratio must match the map.

- **Biomes:** 8-bit greyscale in five equally wide intervals. Use the middles: grey value **26, 77, 128, 179, 230** for biome 0 to 4.
- **Mountains:** white = mountain area, black = none.
- **Rivers:** a white line is drawn as a river. Whether rivers get a gradient or a fixed level is not checked.

What the biomes look like:

| Biome | Grey value | Look |
|---|---|---|
| 0 | 26 | light, green meadow without trees |
| 1 | 77 | meadow with groups of trees and single trees |
| 2 | 128 | dark, overgrown meadow without trees |
| 3 | 179 | dry steppe, yellow-brown |
| 4 | 230 | mixed green and brown (savanna), **no snow** |

Only biome 1 has trees. Dense forest cannot be reached with the biomes, and the tree density cannot be set in the biome tab. Snow comes from height only.

The Studio's biome mask pre-assigns OSM areas: meadow, pasture, park → 0; forest → 1; bog, marsh, heath → 2; farmland, vineyard, orchard as well as rock, sand and quarries → 3; residential, industrial, commercial → 4. The assignment can be changed in the dialog. Settlements as biome 4 give a soft transition and stay the default.

## Towns and industries (`towns_industries`)

A Lua file in the `towns_industries` folder of the user data directory.

- **Coordinates** in metres from the **map centre**, x east, y north (tested in the game).
- **Inhabitants:** the **middle** number of `sizeFactors` sets the starting inhabitants, about 98 per factor. Examples: 0.2 → 19, 1 → 98, 5 → 500, 10 → 999, 30 → 2892. At 100 it is only 4476, so there is an upper limit. The first and third numbers did not change the inhabitants.
- The Studio computes the factor from the OSM population (default scale 0.03 × square root of the population, limited to 0.2 to 30) and hits the numbers in the game (Koblenz 979, Bingen 478).
- **Industries:** each entry has `fileName` (`::/industries/<name>/<name>.con`), `position`, `angle`, `onWater` and `tag`. Names confirmed in the game include `farm`, `forest`, `fishing_grounds`, `oil_platform`, `oil_refinery`, `bricks_works`, `clay_pit`, `livestock_farm`, `saw_mill`, `quarry`, `coal_mine`, `iron_ore_mine`, `sand_pit`, `oil_well`, `cotton_farm`, `steel_mill`, `machine_factory`, `tool_factory`, `vehicle_factory`, `glass_works`, `brewery`, `food_factory`, `furniture_factory`, `chemical_plant`, `textile_factory` and `weaving_mill`.
- According to the wiki there are 32 industries. At the start of a map only the raw-material industries and a few others exist, the rest appear during play.
- Towns need cargo needs (`com` and `ind`), for which the Studio writes real goods.
- **Observations:** quarries and farms look poor on wooded slopes and on the shore, farms on flat plateaus look good. Industries at the map edge let fields stick out over the edge, so the Studio keeps 500 m distance.

## Folders

- Steam: `…\Steam\userdata\<number>\3493540\local`. Steam is not always under `C:\Program Files`, it can be on `D:`, for example.
- GOG or Epic: `C:\Users\<name>\AppData\Roaming\Transport Fever 3`
- Inside, among others: `heightmaps`, `biomes`, `towns_industries`, `save_maps`, `mods` and `settings.lua`.

## Still open

- Format of mods (roads, tracks, buildings) in the new game
- Colour and greyscale coding of the mountains and rivers masks, from an export of the game
- Behaviour of the rivers mask (gradient possible?)
- Meaning of the first and third number of `sizeFactors`
- Dependence of the snow and rock limit on climate and biome
