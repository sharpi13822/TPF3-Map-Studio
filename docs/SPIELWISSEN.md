# Spielwissen: Was im Karteneditor von Transport Fever 3 gilt

[Deutsch](SPIELWISSEN.md) | [English](SPIELWISSEN.en.md)

Messwerte und Beobachtungen, auf denen das Studio beruht. Sie stammen aus dem [offiziellen Wiki](https://wiki.transportfever3.com) und aus eigenen Tests im Spiel (Oktober 2026). Das Spiel kann sich mit Updates ändern, und die Werte sind Richtwerte. Wer etwas anderes misst, ist herzlich eingeladen, ein [Issue](https://github.com/sharpi13822/TPF3-Map-Studio/issues) zu eröffnen.

Inoffiziell, keine Verbindung zu Urban Games oder dem Herausgeber.

## Heightmap

- 16-Bit-Graustufen-PNG. Ein Pixel entspricht 4 × 4 m im Spiel. Kantenlänge in Metern = (Pixel − 1) × 4.
- Der Import hat drei Felder: **Mindesthöhe** (Höhe der schwarzen Pixel), **Maximalhöhe** (Höhe der weißen Pixel) und **Wasserhöhe**. Das Wiki empfiehlt Wasserhöhe 0 für die besten Ergebnisse bei Biomen und Materialien.
- Es gibt nur **einen flachen Wasserspiegel** für die ganze Karte.
- Standardwerte im Dialog: −100 / 500 / 0. Sie ändern sich nicht mit der Kartengröße.
- **Grenzen des Editors (im Spiel getestet):** Der Import nimmt Höhen von **−20 bis 3177 m** (Spanne 3197 m). Mehr geht nicht. Für höheres Gelände hilft das Höhenfenster des Studios (Gipfel kappen, Tiefen abschneiden oder stauchen). Das Höhenfenster selbst ist im Spiel noch nicht geprüft.
- Die Formel des Studios bei Wasserspiegel 0 und Höhen relativ zum Fluss: Minimum = −Puffer unten, Maximum = (Höhe Berg − Höhe Fluss) + Zuschlag oben.

## Schnee und Fels

Test mit zwölf flachen Terrassen von 25 bis 575 m (Import mit Wasser 0):

- Das Spiel färbt nach der **Höhe über dem Wasserspiegel**, nicht nach dem Anteil der Höhenspanne und nicht nach der Höhe über Meer.
- Fels beginnt zwischen etwa **325 und 350 m**, Schnee zwischen etwa **375 und 425 m** über dem Wasser. Die Übergänge sind weich.
- Die Berge- und die Flüsse-Maske ändern daran nichts.
- Beispiel Mittelrhein (Wasser bei 68 m): unbearbeitet etwa 574 m über Wasser, große weiße Flächen auf den Hochflächen. Auf 45 % gestaucht (258 m über Wasser) gab es keine weißen Flächen mehr.
- Graue Streifen an steilen Hängen blieben, vermutlich Fels wegen der Neigung (nicht geprüft). Ob die Grenzen vom Klima oder Biom abhängen, ist nicht geprüft (getestet nur mit dem Standardbiom).

## Kartengrößen

Exakt ist (Pixel − 1) × 4 m. Die Anzeige im Spiel rundet. Größen mit `*` erscheinen laut Wiki nur mit `experimentalMapFeatures = true` in der `settings.lua` (im Spiel ist ungeprüft, ob das für die Auswahl nötig ist).

| Größe \ Verhältnis | 1:1 | 1:2 | 1:3 | 1:4 | 1:5 |
|---|---|---|---|---|---|
| Tiny* | 1025×1025 | 641×1281 | 513×1537 | 513×1537 | 385×1921 |
| Small | 2049×2049 | 1409×2817 | 1153×3457 | 1025×4097 | 897×4481 |
| Medium | 2817×2817 | 2049×4097 | 1665×4993 | 1537×6145 | 1281×6401 |
| Large | 3585×3585 | 2561×5121 | 2049×6145 | 1793×7169 | 1537×8065 |
| Very Large | 4097×4097 | 2817×5633 | 2305×6913 | 2049×8193 | 1793×8961 |
| Huge* | 5121×5121 | 3585×7169 | 2945×8833 | 2561×10241 | 2177×10881 |
| Megalomaniac* | 6145×6145 | 4225×8449 | 3457×10369 | 3073×12289 | 2689×13441 |
| Gigantomaniac* | 7169×7169 | 5121×10241 | 4097×12289 | 3585×14337 | 3201×16001 |

(Pixel, Breite × Höhe.) Beispiel: Megalomaniac 1:5 sind 10,752 × 53,76 km, das alte „Größenwahnsinnig 1:5“.

## Biome-Masken

Drei getrennte Bilder im Biome-Tab: **Biome**, **Berge** und **Flüsse**. Alle werden auf die Kartengröße gestreckt, das Seitenverhältnis muss also zur Karte passen.

- **Biome:** 8-Bit-Graustufen in fünf gleich breiten Intervallen. Nimm die Mitten: Grauwert **26, 77, 128, 179, 230** für Biom 0 bis 4.
- **Berge:** weiß = Bergfläche, schwarz = keine.
- **Flüsse:** eine weiße Linie wird als Fluss dargestellt. Ob Flüsse ein Gefälle bekommen oder einen festen Pegel haben, ist nicht geprüft.

So sehen die Biome aus:

| Biom | Grauwert | Aussehen |
|---|---|---|
| 0 | 26 | helle, grüne Wiese ohne Bäume |
| 1 | 77 | Wiese mit Baumgruppen und einzelnen Bäumen |
| 2 | 128 | dunkle, bewachsene Wiese ohne Bäume |
| 3 | 179 | trockene Steppe, gelbbraun |
| 4 | 230 | grün-braun gemischt (Savanne), **kein Schnee** |

Nur Biom 1 hat Bäume. Dichter Wald ist mit den Biomen nicht zu erreichen, die Baumdichte lässt sich im Biome-Tab nicht einstellen. Schnee kommt nur von der Höhe.

Die Biome-Maske des Studios ordnet OSM-Flächen vor: Wiese, Weide, Park → 0; Wald → 1; Moor, Sumpf, Heide → 2; Acker, Weinberg, Obstbau sowie Fels, Sand und Abbau → 3; Siedlung, Industrie, Gewerbe → 4. Die Zuordnung lässt sich im Dialog ändern. Siedlung als Biom 4 ergibt einen weichen Übergang und bleibt Standard.

## Städte und Industrien (`towns_industries`)

Eine Lua-Datei im Ordner `towns_industries` des Userdata-Verzeichnisses.

- **Koordinaten** in Metern ab der **Kartenmitte**, x nach Osten, y nach Norden (im Spiel getestet).
- **Einwohner:** Die **mittlere** Zahl von `sizeFactors` bestimmt die Anfangs-Einwohner, etwa 98 je Faktor. Beispiele: 0,2 → 19, 1 → 98, 5 → 500, 10 → 999, 30 → 2892. Bei 100 sind es nur 4476, es gibt also eine Obergrenze. Die erste und dritte Zahl änderten die Einwohner nicht.
- Das Studio rechnet den Faktor aus der OSM-Einwohnerzahl (Standardmaßstab 0,03 × Wurzel(Einwohner), begrenzt auf 0,2 bis 30) und trifft die Zahlen im Spiel (Koblenz 979, Bingen 478).
- **Industrien:** Pro Eintrag `fileName` (`::/industries/<name>/<name>.con`), `position`, `angle`, `onWater` und `tag`. Im Spiel bestätigte Namen sind unter anderem `farm`, `forest`, `fishing_grounds`, `oil_platform`, `oil_refinery`, `bricks_works`, `clay_pit`, `livestock_farm`, `saw_mill`, `quarry`, `coal_mine`, `iron_ore_mine`, `sand_pit`, `oil_well`, `cotton_farm`, `steel_mill`, `machine_factory`, `tool_factory`, `vehicle_factory`, `glass_works`, `brewery`, `food_factory`, `furniture_factory`, `chemical_plant`, `textile_factory` und `weaving_mill`.
- Laut Wiki gibt es 32 Industrien. Beim Kartenbeginn sind nur die Rohstoff-Industrien und wenige weitere vorhanden, der Rest entsteht im Spiel.
- Städte brauchen Warenbedürfnisse (`com` und `ind`), das Studio schreibt dafür echte Waren hinein.
- **Beobachtungen:** Steinbrüche und Höfe sehen auf bewaldeten Hängen und am Ufer schlecht aus, Höfe auf flachen Hochflächen gut. Industrien am Kartenrand lassen Felder über den Rand ragen, deshalb hält das Studio 500 m Abstand.

## Ordner

- Steam: `…\Steam\userdata\<Nummer>\3493540\local`. Steam liegt nicht immer unter `C:\Program Files`, es kann zum Beispiel auf `D:` sein.
- GOG oder Epic: `C:\Users\<Name>\AppData\Roaming\Transport Fever 3`
- Darin unter anderem: `heightmaps`, `biomes`, `towns_industries`, `save_maps`, `mods` und `settings.lua`.

## Noch offen

- Format der Mods (Straßen, Gleise, Gebäude) im neuen Spiel
- Farb- und Graustufen-Codierung der Berge- und Flüsse-Maske an einem Export aus dem Spiel
- Verhalten der Flüsse-Maske (Gefälle möglich?)
- Bedeutung der ersten und dritten Zahl von `sizeFactors`
- Abhängigkeit der Schnee- und Felsgrenze von Klima und Biom
