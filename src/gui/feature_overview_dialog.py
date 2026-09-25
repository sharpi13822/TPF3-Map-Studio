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
                "Ersetzt die früher fest verdrahtete Overpass-Abfrage durch "
                "Checkboxen (Gleise, Straßen, Tram ja/nein, Gebäude, Parks, "
                "Flächennutzung, Vegetation, Gewässer, Orte). Zeigt eine "
                "Live-Vorschau der resultierenden Abfrage und erlaubt "
                "wiederverwendbare Vorlagen. Mit allen Standard-Häkchen "
                "entspricht das Ergebnis exakt der alten Abfrage.",
            ),
            (
                "OSM als .osm exportieren...",
                "Schreibt die aktuell geladenen OSM-Daten als Standard-OSM-"
                "XML-Datei (inkl. note/meta/bounds-Elementen und den "
                "Standard-Attributen version/timestamp/changeset/uid/user, "
                "die der Converter-Parser erwartet) - Eingabeformat für "
                "den Converter-Teil des OSM-TPF2-Importers.",
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
                "Mod-Checker...",
                "Gleicht installierte Mods (Steam-Workshop-Ordner + "
                "lokaler mod-Ordner) gegen die offizielle Mod-Liste des "
                "OSM-TPF2-Importers ab, gruppiert nach Kategorie mit "
                "Checkboxen für genutzte Funktionen. Warnt vor bekannten "
                "Absturz-Mods und doppelt installiertem Importer.",
            ),
            (
                "Heightmap herunterladen",
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
        "Hilfe-Menü",
        (
            (
                "Import-Anleitung...",
                "Die kompletten 5 Schritte (0-4) des OSM-TPF2-Importers "
                "mit exakten Befehlen aus der offiziellen Dokumentation, "
                "je mit Kopieren-Button. Für Schritt 3 zusätzlich alle 14 "
                "Bau-Optionen per Checkbox, die generierte Lua-Tabelle "
                "wird live aktualisiert.",
            ),
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
