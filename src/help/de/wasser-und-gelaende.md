# Wasser und Gelände einstellen

Oben im Dialog wählst du eine **Voreinstellung**:

- **Original**: alle Optionen aus, die echten Höhen.
- **Empfohlen**: hängt von der Höhenquelle ab (siehe [Höhenquellen](help:hoehenquellen)). Optionen, die OSM-Daten brauchen, bleiben ohne geladene OSM-Daten aus.
- **Eigene Einstellungen** entstehen, sobald du etwas von Hand änderst.

Jede Änderung aktualisiert die Vorschau und die Zahlen unten im Dialog. Die einzelnen Optionen in der empfohlenen Reihenfolge:

## Wasserhöhe

Das Spiel kennt **nur eine Wasserhöhe**. Der Dialog schlägt einen Wert aus der Fläche vor und erkennt Ausreißer wie Bergbau-Restlöcher (*Ausreißer ausschließen*, standardmäßig aus, der Export nutzt immer den vollen Bereich).

Der Knopf **Wasserhöhe aus den OSM-Gewässern vorschlagen** liest die Höhen des Hauptflusses und setzt den Wert in die Mitte zwischen tiefstem und höchstem Punkt. So wird der Fluss an beiden Enden um etwa gleich viel korrigiert. Braucht OSM-Daten.

> Eine Wasserhöhe gleich der Mindesthöhe bedeutet **kein Wasser**.

## Gelände glätten

Entfernt Treppenstufen an den Hängen, Standard 15 m. Nötig bei Copernicus (nur 30 m pro Pixel). Bei den genauen Modellen (DGM1, swissALTI3D, AHN, BEV, Luxemburg) meist nicht, die Voreinstellung *Empfohlen* lässt es dort aus.

## Trassen und Siedlungen einebnen

Bahnstrecken, größere Straßen und Gebäude aus OSM werden abgeflacht, damit im Spiel weniger Rampen nötig sind. Standard 60 m, bei *Empfohlen* mit genauen Modellen 10 m. Braucht OSM-Daten. *Im Spiel getestet, funktioniert.*

## Wasser nur dort, wo OpenStreetMap Wasser hat (empfohlen)

Gewässer bekommen ein festes Bett mit Böschung und Tiefe, alles andere Land liegt knapp über dem Wasserspiegel: keine überfluteten Auen, keine Tümpel. Standardwerte: Böschung 60 m (breiter = flacheres Ufer), Tiefe am Ufer 2 m, Tiefe in der Mitte 8 m, Ufer über Wasser 2 m, nur Gewässer bis 15 m über dem Wasserspiegel. Höher gelegene Bäche und Bergseen bleiben unverändert. Die Option *Terrain sanft ans Wasserniveau anpassen* schaltet sich dabei ab, beide zusammen gehen nicht.

## Gefälle ausgleichen

Für lange Flüsse mit starkem Gefälle. Das Studio legt Flüsse und Seen auf eine gemeinsame Ebene und zieht das Gelände relativ dazu mit. Das Relief über dem jeweiligen Wasserspiegel bleibt erhalten, die **absoluten Höhen über NN stimmen danach nicht mehr**. Standard: Stärke 100 %, Glättung 400 m, Bezug: Gewässer bis 30 m über dem Wasserspiegel.

## Gelände sanft mitsenken

Das Spiel kennt nur einen Wasserspiegel. Liegt ein See höher (zum Beispiel der Schliersee neben dem Tegernsee), entsteht um ihn sonst eine Steilküste. Mit diesem Haken wird jeder solche See auf den Wasserspiegel gesenkt und das Gelände drumherum sanft mitgenommen. Der *Auslauf* (Standard 1500 m) bestimmt, wie weit vom Ufer die Absenkung ausläuft: größer = sanfter, aber mehr Umgebung ändert sich. Berge weit weg vom See bleiben unverändert. Braucht OSM-Daten. *Im Spiel noch nicht geprüft.*

## Meeresboden absenken

Die Höhendaten (Copernicus, DGM1 usw.) enthalten keine Meerestiefen. Das offene Meer liegt deshalb flach auf 0 m und fällt im Spiel schnell als Strand trocken, die Küstenlinie ist dann kaum zu erkennen. Mit diesem Haken (Standard: an) liegt das Meer an der Küste 2 m unter dem Wasserspiegel und wird nach außen über etwa 300 m sanft bis zur eingestellten *Tiefe* (Standard 10 m) abgesenkt. Land bleibt unverändert. Die Import-Werte unten im Dialog rechnen die neue Tiefe automatisch ein. Wirkt nur, wenn das Rechteck offenes Meer enthält.

## Höhen stauchen

Gegen weiße und graue Flächen auf den Höhen: Das Spiel färbt nach der Höhe der importierten Werte (Fels ab etwa 325 bis 350 m, Schnee ab etwa 375 bis 425 m). Stauchen drückt alle Höhen über dem Wasserspiegel auf einen Anteil. Standard 100 % (unverändert). Am Rhein hat 45 % funktioniert, bei Bern etwa 75 % (mit dem Haken *Werte auf Wasserhöhe 0 beziehen*). Der Dialog zeigt unten einen Hinweis, wenn das Gelände zu hoch liegt.
