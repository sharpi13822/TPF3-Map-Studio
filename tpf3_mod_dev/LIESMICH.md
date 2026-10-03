# Diagnose-Version des Map-Studio-Mods (v11)

`mapstudio.script.lua` ist die Version v10 aus deinem Lauf (2085 Wege, 1201 gebaut) mit zusätzlicher Diagnose.
Gebaut wird genauso wie vorher. Es wird nur mehr ins Log geschrieben.

## Zum Testen (ohne das Studio zu ändern)
1. Datei kopieren nach
   `D:\Steam\userdata\<Nummer>\3493540\local\mods\map_studio_osm_import_1\content\mapstudio.script.lua`
   (die vorhandene überschreiben). Das Studio schreibt beim nächsten „Mod schreiben…“ wieder seine eigene Version darüber.
2. Spiel starten, Import wie bisher auslösen. Im Log muss `OSMBAU bereit, Version: mapstudio v11` stehen.
3. Danach `stdout.txt` schicken.

## Was neu ist
- **`DIAG sendCommand wirft:`** und **`DIAG Weg <nr> sendCommand-Ausnahme | ...`**: Bei jeder Ausnahme beim Bauen (bisher
  `Unknown exception`, 58 Wege) steht jetzt je vorhandenem Anschlussknoten: Abstand zur geplanten Position, Höhe,
  die angeschlossenen Kanten (Vorlage, Typ), ob der Knoten zu einer Konstruktion oder einem Bahnübergang gehört,
  Stadtkreuzung, Knotenkonfiguration. Höchstens 120 Zeilen.
- **`DIAG Weg <nr> Pruefung: ...`**: dasselbe für die ersten 25 Wege, deren Prüfung gescheitert ist und die an vorhandene Knoten anschließen.
- **Fehlerliste (`Weg ... [osm ...]`)**: Bei jeder Prüfmeldung (z. B. „Bau nicht möglich“) stehen jetzt Kollisionspartner,
  Warnungen (`W:`) und Infos (`I:`) des Spiels dabei. Je Fehlergrund höchstens 60 Einträge, insgesamt 600 (vorher nur die ersten 300 Fehler).
- Die Grund-Zusammenfassung zeigt 14 statt 8 Gründe.
