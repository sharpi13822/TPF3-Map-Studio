# TPF3 Map Studio v0.3.0

3D preview, height zones and more control over snow and rock. / 3D-Vorschau, Höhenzonen und mehr Kontrolle über Schnee und Fels.

## English

**What's new**
- **3D preview** in the heightmap dialog, next to the 2D preview: terrain as a block with earth walls, water like an aquarium, rotate with the mouse, zoom with the wheel, relief exaggeration 1x to 5x. It is for checking only and does not change the export.
- **Height zones** in the preview (green, rock, snow) with adjustable rock and snow limits and the share of each zone. The limits are estimates from game tests.
- **Compress elevations** now goes down to 5 % (before 20 %) and has a slider that recalculates when released. This helps against white areas on high terrain.
- **Biome mask:** optionally replace trees above a height limit with a biome without trees.
- **Height window:** the map editor accepts elevations from -100 m (before -20 m). Confirmed in the game down to -38 m; -100 m itself has not been measured yet.
- **JSON export** works again and opens a save dialog.
- The heightmap dialog opens large, so the window no longer has to be dragged wider.

**Install:** download `TPF3-Map-Studio-v0.3.0-win64.zip`, extract the **whole** ZIP, run `TPF3-Map-Studio.exe`. Windows may warn on first start ("More info" -> "Run anyway"); antivirus false positives are known for PyInstaller programs.

**Note:** unofficial tool, not affiliated with Urban Games. The 3D preview uses Three.js (MIT licence, see THIRD_PARTY_NOTICES).

SHA-256: `31d3d4f38b3a4f7fb9ac960e8e2ca49951b29f5d40e8affaa1cafcb433d4947d`

## Deutsch

**Neu**
- **3D-Vorschau** im Heightmap-Dialog neben der 2D-Vorschau: Gelände als Block mit Erdwänden, Wasser wie in einem Aquarium, mit der Maus drehen, mit dem Rad zoomen, Überhöhung 1× bis 5×. Sie dient nur der Kontrolle und ändert den Export nicht.
- **Höhenzonen** in der Vorschau (grün, Fels, Schnee) mit einstellbarer Fels- und Schneegrenze und den Flächenanteilen. Die Grenzen sind Schätzwerte aus Spieltests.
- **Höhen stauchen** geht jetzt bis 5 % (vorher 20 %) und hat einen Schieber, der beim Loslassen neu rechnet. Das hilft gegen weiße Flächen auf hohem Gelände.
- **Biome-Maske:** Bäume ab einer Höhengrenze lassen sich optional durch ein Biom ohne Bäume ersetzen.
- **Höhenfenster:** Der Karteneditor nimmt Höhen ab -100 m (vorher -20 m). Im Spiel bis -38 m bestätigt, -100 m selbst ist noch nicht gemessen.
- **JSON-Export** funktioniert wieder und öffnet einen Speichern-Dialog.
- Der Heightmap-Dialog öffnet groß, das Fenster muss nicht mehr breit gezogen werden.

**Download:** `TPF3-Map-Studio-v0.3.0-win64.zip`, **komplett** entpacken, `TPF3-Map-Studio.exe` starten. Beim ersten Start warnt Windows ("Weitere Informationen" -> "Trotzdem ausführen").

Prüfsumme (SHA-256): `31d3d4f38b3a4f7fb9ac960e8e2ca49951b29f5d40e8affaa1cafcb433d4947d`
