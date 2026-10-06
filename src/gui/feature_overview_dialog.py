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


# (Menüpfad, [(Feature-Name, Beschreibung), ...])
FEATURE_GROUPS = (
    (
        "Datei-Menü",
        (
            (
                "Projekteigenschaften...",
                "Projektname setzen/ändern (z.B. 'Rheintal', 'Nürnberg-"
                "Korridor'). Wird mit gespeichert und erscheint im "
                "Fenstertitel sowie im Projekt-Dashboard.",
            ),
            (
                "Projekt-Dashboard...",
                "Übersicht aller gespeicherten .tpf2ms-Projekte in einem "
                "gewählten Ordner: Auswahlgröße/-drehung, ob OSM-Daten "
                "geladen sind, ob bereits eine Heightmap exportiert wurde, "
                "letztes Änderungsdatum. Doppelklick öffnet das Projekt "
                "direkt.",
            ),
            (
                "Speichern / Öffnen",
                "Speichert bzw. lädt Projektname, Rechteck-Tool-Auswahl "
                "(inkl. Drehung), geladene Layer und Heightmap-Export-"
                "Status. Beim erneuten Öffnen des Rechteck-Tools werden "
                "Mittelpunkt, Größe und Drehwinkel automatisch aus dem "
                "geladenen Projekt vorbelegt.",
            ),
        ),
    ),
    (
        "Werkzeuge-Menü",
        (
            (
                "Koordinaten-Messwerkzeug",
                "Zwei Punkte auf der Karte anklicken: erster Klick zeigt "
                "lat/lon, zweiter Klick zeigt zusätzlich die Distanz "
                "(als Linie auf der Karte und in der Statusleiste).",
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
                "Ampel-Checks für das geladene OSM-Projekt vor dem großen "
                "Import-Lauf: strukturelle Plausibilität (z.B. Knoten/Wege-"
                "Verhältnis), 0-Treffer trotz aktivierter Kategorie, "
                "besondere Prüfung für 'Orte' (0 Städte bei aktivierter "
                "Kategorie = Fehler). Dichte-Kennzahlen (Straßen/Gebäude/"
                "Orte pro km²) werden nur angezeigt, nicht bewertet.",
            ),
            (
                "Heightmap herunterladen",
                "Erzeugt die Heightmap für den gewählten Ausschnitt. "
                "Höhenquelle ist das DGM1 für Deutschland (1 m Auflösung, "
                "über hoehendaten.de; die Quellenangabe steht im Dialog). "
                "Zusätzlich zum bisherigen Ablauf: Button 'Schnellvorschau' "
                "vor dem eigentlichen Download (gleiche Kacheln, aber nur "
                "~300px statt voller Auflösung - bei großen Bändern das "
                "~2000-fache weniger Rechenarbeit). Der Wasserhöhen-"
                "Vorschlag erkennt jetzt zusätzlich Ausreißer wie Bergbau-"
                "Restlöcher (Tukey-3×IQR-Methode) und bietet eine Checkbox "
                "an, sie aus dem exportierten Höhenbereich auszuschließen "
                "(standardmäßig aus, damit sich am Exportverhalten nichts "
                "automatisch ändert).",
            ),
            (
                "Rechteck-Tool",
                "Unverändert in der Bedienung, aber: füllt sich beim "
                "erneuten Öffnen automatisch mit Mittelpunkt/Größe/"
                "Drehwinkel der aktuellen Projekt-Auswahl vor.",
            ),
        ),
    ),
    (
        "Heightmap-Dialog (Werkzeuge, Heightmap herunterladen)",
        (
            (
                "Wasser und Gelände",
                "Die Wasserhöhe lässt sich aus den OSM-Gewässern "
                "vorschlagen. 'Wasser nur dort, wo OpenStreetMap Wasser "
                "hat' formt Flussbetten mit Böschung und Tiefe. 'Gefälle "
                "ausgleichen' gleicht das Gefälle großer Flüsse aus, weil "
                "das Spiel nur eine Wasserhöhe kennt. Dazu kommen Glätten, "
                "Höhen stauchen und das Einebnen von Trassen und "
                "Siedlungen. Die Anleitung öffnet mit F1.",
            ),
            (
                "Im TPF3-Import eintragen",
                "Zeigt unten im Dialog Mindesthöhe, Maximalhöhe, "
                "Wasserhöhe und das Kartenformat, die beim Import der "
                "Heightmap im Editor von Transport Fever 3 eingetragen "
                "werden.",
            ),
            (
                "Biome-Maske aus OSM...",
                "Erzeugt aus der geladenen OSM-Landnutzung eine "
                "Biome-Maske (Kategorie 'Siedlung, Heide, Moor, Fels').",
            ),
            (
                "Städte aus OSM...",
                "Schreibt die Orte aus OSM als Datei für den Städte-Import "
                "im Editor. Die Größe lässt sich per Faktor anpassen, die "
                "Auswahl erfolgt je Ort.",
            ),
            (
                "Industrien aus OSM...",
                "Sucht Industrie-Objekte wie Sägewerke oder Ziegeleien in "
                "OSM und schreibt eine Datei für den Industrie-Import im "
                "Editor. Dabei werden Hang, Wasser und Kartenrand geprüft.",
            ),
            (
                "Bahnhöfe aus OSM...",
                "Liest Bahnhöfe und Haltepunkte aus den geladenen OSM-Daten "
                "(mit Bahnsteigen, Haltepositionen und Gebäuden; "
                "aufgegebene, im Bau befindliche und Betriebsbahnhöfe sind "
                "gekennzeichnet) und schreibt bahnhoefe.json und "
                "bahnhoefe.csv mit Koordinaten in Metern ab Kartenmitte. "
                "Im Spiel wird nichts gebaut, die Dateien dienen als "
                "Nachschlagewerk. Aneinanderstoßende Bahnsteig-Wege gelten "
                "als ein Bahnsteig, bei Bahnsteigflächen zählt die Länge "
                "statt des Umfangs.",
            ),
        ),
    ),
    (
        "Karte und Ebenen",
        (
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
        ),
    ),
    (
        "Hilfe-Menü",
        (
            (
                "Funktionsübersicht (dieses Fenster)",
                "Diese Liste - fasst alle in gemeinsamer Arbeit "
                "hinzugefügten Funktionen zusammen.",
            ),
        ),
    ),
)


class FeatureOverviewDialog(QDialog):
    """
    Listet alle in dieser Zusammenarbeit hinzugefuegten Studio-Funktionen
    auf, gruppiert nach Menue, mit Kurzbeschreibung.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Funktionsübersicht")
        self.setMinimumSize(760, 640)

        outer_layout = QVBoxLayout(self)

        intro = QLabel(
            "Übersicht aller Funktionen, die im Lauf der Zusammenarbeit "
            "zum Studio hinzugekommen sind - gruppiert nach dem Menü, in "
            "dem sie zu finden sind."
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

            group = QGroupBox(menu_name)
            group_layout = QVBoxLayout(group)

            for feature_name, description in features:

                name_label = QLabel(feature_name)
                name_label.setStyleSheet("font-weight: bold;")
                group_layout.addWidget(name_label)

                desc_label = QLabel(description)
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
