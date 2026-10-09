from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QScrollArea,
    QWidget,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt

from src.i18n import tr


# (Menüpfad, [(Feature-Name, Beschreibung), ...])
# Die Texte stehen hier unuebersetzt; beim Aufbau des Fensters laufen sie durch
# tr(). Die Uebersetzungen stehen in src/i18n_en.py.
FEATURE_GROUPS = (
    (
        "Datei-Menü",
        (
            (
                "Neu und Projekt schließen",
                "Beide beginnen ein neues, leeres Projekt: Marker, Rechteck, "
                "OSM-Daten, eigene Objekte und die Rückgängig-Liste werden "
                "geleert, die Ebenen sind wieder ausgeblendet. Bei "
                "ungespeicherten Änderungen fragt das Studio vorher nach "
                "dem Speichern. Läuft gerade ein OSM-Download, geht es "
                "erst danach.",
            ),
            (
                "Öffnen",
                "Lädt ein gespeichertes Projekt (.tpf2ms) mit Projektname, "
                "Rechteck-Tool-Auswahl (inkl. Drehung), geladenen Layern "
                "und Heightmap-Export-Status. Beim erneuten Öffnen des "
                "Rechteck-Tools werden Mittelpunkt, Größe und Drehwinkel "
                "automatisch aus dem geladenen Projekt vorbelegt.",
            ),
            (
                "Speichern und Speichern unter...",
                "Speichern schreibt in die Datei, die du zuletzt geöffnet "
                "oder gespeichert hast. Gibt es noch keine, fragt es nach "
                "dem Namen. 'Speichern unter...' fragt immer nach dem "
                "Namen. Beim Beenden fragt das Studio bei ungespeicherten "
                "Änderungen nach.",
            ),
            (
                "Projekt-Dashboard...",
                "Übersicht aller gespeicherten .tpf2ms-Projekte in einem "
                "gewählten Ordner (der Ordner wird gemerkt): Auswahl, ob "
                "OSM-Daten geladen sind, ob bereits eine Heightmap "
                "exportiert wurde, letztes Änderungsdatum. Doppelklick "
                "öffnet das Projekt direkt.",
            ),
            (
                "Projekteigenschaften...",
                "Projektname setzen/ändern (z.B. 'Rheintal', 'Nürnberg-"
                "Korridor'). Wird mit gespeichert und erscheint im "
                "Fenstertitel sowie im Projekt-Dashboard.",
            ),
            (
                "Beenden",
                "Schließt das Studio.",
            ),
        ),
    ),
    (
        "Bearbeiten-Menü",
        (
            (
                "Rückgängig / Wiederholen",
                "Macht Änderungen an Markern rückgängig oder stellt sie "
                "wieder her, zum Beispiel Umbenennen und Löschen.",
            ),
        ),
    ),
    (
        "Ansicht-Menü",
        (
            (
                "Docks ein- und ausblenden",
                "Blendet die Bereiche Projekt, Layer und Eigenschaften ein "
                "oder aus.",
            ),
        ),
    ),
    (
        "Werkzeuge-Menü",
        (
            (
                "Marker und Auswahl",
                "Marker setzen: ein Klick auf die Karte setzt einen Marker, "
                "der den Mittelpunkt für das Rechteck-Tool liefert. "
                "Auswahl: einen Bereich auf der Karte auswählen (zwei "
                "Ecken).",
            ),
            (
                "Koordinaten-Messwerkzeug",
                "Zwei Punkte auf der Karte anklicken: erster Klick zeigt "
                "lat/lon, zweiter Klick zeigt zusätzlich die Distanz "
                "(als Linie auf der Karte und in der Statusleiste).",
            ),
            (
                "Rechteck-Tool",
                "Legt ein gedrehtes Kartenband an (Mittelpunkt, Größe, "
                "Drehwinkel). Im Dialog stellst du Breite und Länge des "
                "Mittelpunkts, die Kartengröße im Format des Spiels (der "
                "Dialog zeigt Kilometer und Pixel), den Drehwinkel und den "
                "Sicherheitsrand für Downloads ein (Standard 500 m, ein "
                "zusätzlicher Rand um das Rechteck). Das Rechteck lässt sich "
                "auf der Karte verschieben (blauer Punkt) und drehen "
                "(oranger Punkt). Beim erneuten Öffnen füllt es sich mit "
                "den Werten der aktuellen Projekt-Auswahl vor.",
            ),
            (
                "OSM laden",
                "Lädt die Daten für den gewählten Ausschnitt über die "
                "Overpass-API von OpenStreetMap. Die Statusleiste zeigt den "
                "Fortschritt. Danach erscheinen die Bahnhöfe automatisch "
                "auf der Karte, die übrigen Ebenen schaltest du im Layer-Dock "
                "ein.",
            ),
            (
                "Overpass-Abfrage...",
                "Stellt per Checkboxen ein, was aus OpenStreetMap geladen "
                "wird: Gleistypen (Straßenbahn ein/aus), Straßentypen, "
                "Gebäude, Parks und Gärten, Flächennutzung, Vegetation, "
                "Gewässer, Orte, Siedlung/Heide/Moor/Fels (für die Biome) "
                "und Industrie-Objekte. Bahnhöfe und Haltepunkte werden "
                "immer mitgeladen. Zeigt eine Live-Vorschau der "
                "resultierenden Abfrage und erlaubt wiederverwendbare "
                "Vorlagen. Nach einer Änderung muss OSM neu geladen "
                "werden.",
            ),
            (
                "Converter-Befehl anzeigen...",
                "Setzt den fertigen Aufrufbefehl für main.exe bzw. main.py "
                "(über venv) automatisch aus der aktuellen Auswahl "
                "zusammen (Kartengröße + Bounds-Koordinaten als Arg 3/4) - "
                "mit Kopieren-Button. Warnt, wenn die Auswahl gedreht ist "
                "(der Converter kennt keine Drehung).",
            ),
            (
                "Vorab-Prüfung...",
                "Ampel-Checks für die geladenen OSM-Daten, bevor du "
                "weiterarbeitest: strukturelle Plausibilität (z.B. Knoten/Wege-"
                "Verhältnis), 0-Treffer trotz aktivierter Kategorie, "
                "besondere Prüfung für 'Orte' (0 Städte bei aktivierter "
                "Kategorie = Fehler). Dichte-Kennzahlen (Straßen/Gebäude/"
                "Orte pro km²) werden nur angezeigt, nicht bewertet.",
            ),
            (
                "Heightmap herunterladen",
                "Öffnet den Heightmap-Dialog (siehe nächste Gruppe): "
                "Höhendaten laden, Gelände und Wasser einstellen, die "
                "Heightmap exportieren und Biome, Städte, Industrien und "
                "Bahnhöfe aus OSM erzeugen.",
            ),
        ),
    ),
    (
        "Heightmap-Dialog",
        (
            (
                "Höhenquelle",
                "Copernicus: weltweit, aber nur 30 m fein und mit "
                "Baumkronen. DGM1 Deutschland: 1-m-Geländemodell der "
                "Bundesländer, die Kacheln werden über hoehendaten.de "
                "geladen (etwa 20 Kacheln pro Minute, danach liegen sie im "
                "Zwischenspeicher), die Quellenangabe zeigt der Dialog an. "
                "Eigene Kacheln: GeoTIFF-Dateien (1-km-Raster), die du "
                "selbst bei einem Landesportal heruntergeladen hast. "
                "swissALTI3D Schweiz: Geländemodell von swisstopo für die "
                "Schweiz und Liechtenstein (2 m), die Kacheln kommen von "
                "data.geo.admin.ch. Die Auswahl erscheint nur bei Karten "
                "dort. Wo DGM1- oder swissALTI3D-Daten fehlen, ergänzt das "
                "Studio aus Copernicus.",
            ),
            (
                "Schnellvorschau",
                "Zeigt vor dem echten Download eine Vorschau in niedriger "
                "Auflösung. Sie nutzt immer Copernicus, auch wenn unten eine "
                "DGM1-Quelle gewählt ist. Danach lädt 'Höhendaten "
                "herunterladen' die volle Auflösung.",
            ),
            (
                "Voreinstellung",
                "Original: alle Optionen aus, die echten Höhen. Empfohlen: "
                "hängt von der Höhenquelle ab (bei Copernicus Glätten, "
                "Einebnen und Wasser nach OSM, bei DGM1 und swissALTI3D ohne Glätten, "
                "Einebnen 10 m und Wasser nach OSM mit Böschung 10 m). "
                "Optionen, die OSM-Daten brauchen, bleiben ohne geladene "
                "OSM-Daten aus. Eigene Einstellungen entstehen, sobald du "
                "etwas änderst.",
            ),
            (
                "Wasserhöhe",
                "Das Spiel kennt nur eine Wasserhöhe. Der Dialog schlägt "
                "einen Wert aus der Fläche vor und erkennt Ausreißer wie "
                "Bergbau-Restlöcher. Dann lässt sich der Höhenbereich ohne "
                "sie darstellen ('Ausreißer ausschließen', standardmäßig "
                "aus). 'Wasserhöhe aus den OSM-Gewässern vorschlagen' liest "
                "die Höhen des Hauptflusses und setzt den Wert in die Mitte "
                "zwischen tiefstem und höchstem Punkt.",
            ),
            (
                "Gelände glätten und Höhen stauchen",
                "Glätten gegen Treppenstufen und Kristallflächen an Hängen "
                "(das Copernicus-Modell hat nur etwa 30 m pro Pixel). Höhen "
                "stauchen drückt alle Höhen über dem Wasserspiegel auf einen "
                "Anteil, falls Hochflächen im Spiel über die Schneegrenze "
                "ragen (weiße Flächen). Die Hänge werden dabei flacher.",
            ),
            (
                "Höhenzonen in der Vorschau",
                "Zeigt in der Vorschau grün, Fels und Schnee nach der Höhe "
                "über dem Wasserspiegel. Felsgrenze und Schneegrenze stellst "
                "du mit Feld oder Schieber ein (Schätzwerte, nur für die "
                "Vorschau, nicht für den Export). Darunter stehen das Maximum "
                "und die Flächenanteile. Der Schieber unter 'Höhen stauchen "
                "auf' rechnet beim Loslassen neu. Echter Fels hängt im Spiel "
                "zusätzlich an der Neigung.",
            ),
            (
                "Höhenfenster begrenzen",
                "Der Karteneditor von TPF3 nimmt nur Höhen von -20 bis 3177 m "
                "an. Mit dem Haken legst du das Gelände in ein Fenster (Felder "
                "'Fenster von ... bis', ein Schieberegler verschiebt es). Für "
                "Werte außerhalb gibt es drei Modi: Oben kappen (Gipfel werden "
                "flach gesetzt), Unten abschneiden (Tiefen werden flach "
                "gesetzt) und Stauchen (alles wird ins Fenster gedrückt, die "
                "Wasserhöhe bleibt). Die Vorschau färbt betroffene Stellen ein "
                "(rot: tiefer gesetzt, hellblau: höher gesetzt) und zeigt, wie "
                "viel Fläche planiert wird. Vorschau, Zahlen und Export "
                "benutzen dasselbe Raster. Ohne Haken warnt der Dialog, wenn "
                "die Höhen außerhalb der Editor-Grenzen liegen.",
            ),
            (
                "Trassen und Siedlungen einebnen",
                "Bahnstrecken, größere Straßen und Gebäude aus OSM: das "
                "Gelände dort wird abgeflacht, damit im Spiel weniger Rampen "
                "nötig sind. Braucht geladene OSM-Daten. Die Glättung "
                "bestimmt, wie eben es wird.",
            ),
            (
                "Gefälle ausgleichen",
                "Legt Flüsse und Seen auf eine gemeinsame Ebene und zieht "
                "das Gelände relativ dazu mit. Das Relief über dem jeweiligen "
                "Wasserspiegel bleibt erhalten, die absoluten Höhen über NN "
                "stimmen danach aber nicht mehr. Gewässer, die deutlich "
                "höher liegen (Bergseen, Nebenflüsse), dienen nicht als "
                "Bezug.",
            ),
            (
                "Wasser nur dort, wo OpenStreetMap Wasser hat",
                "Gewässer bekommen ein festes Bett mit Böschung und Tiefe, "
                "alles andere Land liegt knapp über dem Wasserspiegel: keine "
                "überfluteten Auen und Tümpel. Ersetzt die sanfte Anpassung "
                "darunter.",
            ),
            (
                "Terrain sanft ans Wasserniveau anpassen",
                "Verhindert trockenfallende Flüsse und Seen, weicht dafür "
                "geringfügig von den echten Höhendaten ab. Sehr kleine "
                "Einzelgewässer werden ausgenommen, um Krater zu vermeiden. "
                "Das Gelände unterhalb des Wasserspiegels wird zusätzlich "
                "weichgezeichnet.",
            ),
            (
                "Werte auf Wasserhöhe 0 beziehen",
                "Empfehlung des TPF3-Wikis für Biome und Materialien. Die "
                "Mindesthöhe kann dabei negativ werden.",
            ),
            (
                "Im TPF3-Import eintragen",
                "Zeigt unten im Dialog Mindesthöhe, Maximalhöhe, "
                "Wasserhöhe und das Kartenformat, die beim Import der "
                "Heightmap im Editor von Transport Fever 3 eingetragen "
                "werden.",
            ),
            (
                "Exportieren...",
                "Speichert die fertige Heightmap als 16-Bit-PNG und "
                "schlägt dafür den heightmaps-Ordner von TPF3 vor. Die "
                "Anleitung im Dialog öffnet mit F1.",
            ),
            (
                "Biome-Maske aus OSM...",
                "Erzeugt aus der geladenen OSM-Landnutzung eine Maske für "
                "den Biome-Tab im Karteneditor. Braucht geladene OSM-Daten.",
            ),
            (
                "Städte aus OSM...",
                "Erzeugt aus den geladenen OSM-Orten eine Städte-Datei für "
                "den Ordner towns_industries. Die Größe lässt sich per "
                "Faktor anpassen, die Auswahl erfolgt je Ort.",
            ),
            (
                "Industrien aus OSM...",
                "Erzeugt aus geladenen OSM-Objekten (Höfe, Steinbrüche, "
                "Sägewerke, ...) eine Industrien-Datei für den Ordner "
                "towns_industries. Dabei werden Hang, Wasser und Kartenrand "
                "geprüft.",
            ),
            (
                "Bahnhöfe aus OSM...",
                "Liest Bahnhöfe, Haltepunkte, Bahnsteige, Bahnhofsgebäude "
                "und Haltepositionen aus den geladenen OSM-Daten "
                "(aufgegebene, im Bau befindliche und Betriebsbahnhöfe sind "
                "gekennzeichnet) und speichert sie als bahnhoefe.json (alles) "
                "und bahnhoefe.csv (eine Zeile je Bahnhof) mit Koordinaten "
                "in Metern ab Kartenmitte. Im Spiel wird nichts gebaut, die "
                "Dateien dienen als Nachschlagewerk. Aneinanderstoßende "
                "Bahnsteig-Wege gelten als ein Bahnsteig, bei "
                "Bahnsteigflächen zählt die Länge statt des Umfangs.",
            ),
        ),
    ),
    (
        "Karte und Ebenen",
        (
            (
                "Kartenquelle",
                "Wechselt zwischen der normalen Straßenkarte "
                "(OpenStreetMap) und 'Karte + Relief' mit einem im Browser "
                "berechneten Schattenrelief, das Täler, Hänge und Bergkämme "
                "zeigt. Die Eisenbahnkarte (OpenRailwayMap) legt Gleise, "
                "Bahnhöfe und Signale darüber, das Maß-Gitter hilft beim "
                "Abschätzen von Abständen und Größen.",
            ),
            (
                "Layer-Dock",
                "Je Ebene: Haken (ein- und ausblenden), Schloss (sperrt "
                "Auswahl und Bearbeitung in der Karte), Balken (Deckkraft) "
                "und Pfeile (Reihenfolge). Rechtsklick auf eine Zeile: "
                "anzeigen, ausblenden, sperren, entsperren oder die "
                "Deckkraft zurücksetzen.",
            ),
            (
                "Ebene Bahnhöfe",
                "Nach 'OSM laden' erscheinen die Bahnhöfe als Kreise mit "
                "Namen auf der Karte. Blau ist ein Bahnhof, grün ein "
                "Haltepunkt, rot aufgegeben, orange im Bau, lila ein "
                "Betriebsbahnhof und grau ein zweifelhafter Eintrag "
                "(zum Beispiel Bergbahn). Die Namen erscheinen ab einer "
                "bestimmten Zoomstufe. Im Layer-Dock lässt sich die Ebene "
                "ein- und ausschalten.",
            ),
            (
                "Zeichnen und JSON",
                "Eigene Straßen, Flüsse und Gebäude zeichnen: Knopf wählen, "
                "Punkte auf der Karte anklicken, dann 'Fertig'. 'JSON "
                "Export' speichert die Objekte der Karte als Datei, 'JSON "
                "Import' lädt sie wieder. 'Alle' und 'Keine' schalten alle "
                "Ebenen im Panel ein oder aus.",
            ),
            (
                "Marker-Liste (Dock Projekt)",
                "Rechtsklick auf einen Marker: auf den Marker zentrieren, "
                "umbenennen oder löschen. Doppelklick zentriert die Karte "
                "auf den Marker.",
            ),
        ),
    ),
    (
        "Hilfe-Menü",
        (
            (
                "Funktionsübersicht (dieses Fenster)",
                "Diese Liste der Funktionen des Studios, gruppiert nach "
                "Menü und Dialog.",
            ),
        ),
    ),
)


class FeatureOverviewDialog(QDialog):
    """
    Listet die Funktionen des Studios auf, gruppiert nach Menue und Dialog,
    mit Kurzbeschreibung.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle(tr("Funktionsübersicht"))
        self.setMinimumSize(760, 640)

        outer_layout = QVBoxLayout(self)

        intro = QLabel(
            tr(
                "Übersicht der Funktionen des Studios, gruppiert nach dem "
                "Menü oder Dialog, in dem sie zu finden sind."
            )
        )
        intro.setWordWrap(True)
        outer_layout.addWidget(intro)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer_layout.addWidget(scroll)

        content = QWidget()
        layout = QVBoxLayout(content)
        scroll.setWidget(content)

        for menu_name, features in FEATURE_GROUPS:

            group = QGroupBox(tr(menu_name))
            group_layout = QVBoxLayout(group)

            for feature_name, description in features:

                name_label = QLabel(tr(feature_name))
                name_label.setStyleSheet("font-weight: bold;")
                group_layout.addWidget(name_label)

                desc_label = QLabel(tr(description))
                desc_label.setWordWrap(True)
                desc_label.setTextInteractionFlags(
                    Qt.TextSelectableByMouse
                )
                group_layout.addWidget(desc_label)

            layout.addWidget(group)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        outer_layout.addWidget(buttons)
