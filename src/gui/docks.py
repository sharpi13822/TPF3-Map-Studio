from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QWidget,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTextBrowser,
    QVBoxLayout,
)


GUIDE_HTML = """
<h3>So arbeitest du mit dem Studio</h3>

<p><b>1. Bereich festlegen</b><br>
Zuerst sagst du dem Studio, welches Stück Land du brauchst.
Setze mit dem <i>Marker</i>-Werkzeug einen Marker in die Mitte des
gewünschten Gebiets. Öffne dann <i>Werkzeuge &rarr; Rechteck-Tool</i>
und wähle Kartengröße und Drehwinkel. Ein ausgewählter Marker
liefert den Mittelpunkt. Das blaue Rechteck zeigt, was später
geladen wird. Mit den beiden Punkten daran kannst du es
verschieben (blau) und drehen (orange).</p>

<p><b>2. Daten laden</b><br>
<i>Werkzeuge &rarr; OSM laden</i> holt Straßen, Gebäude, Gewässer und
mehr aus OpenStreetMap. Bei großen Gebieten kann das einige Minuten
dauern, die Statusleiste zeigt den Fortschritt. Was geladen wird,
stellst du unter <i>Werkzeuge &rarr; Overpass-Abfrage</i> ein.</p>

<p><b>3. Ebenen ein- und ausblenden</b><br>
Im Panel <i>Layer</i> auf der Karte bestimmst du mit den Haken,
was du siehst. Fahre mit der Maus über einen Eintrag, dann erscheint
eine kurze Erklärung.</p>
<ul>
<li><b>Landnutzung:</b> Felder, Wiesen, Obst- und Weinanbau,
Gärtnereien.</li>
<li><b>Vegetation:</b> Wälder und Baumreihen.</li>
<li><b>Parks:</b> Parks und Gärten.</li>
<li><b>Straßen:</b> alle Straßen und Wege.</li>
<li><b>Schienen:</b> Bahnstrecken.</li>
<li><b>Wasser:</b> Seen, Teiche und breite Flüsse als Fläche.</li>
<li><b>Wasserwege:</b> Bäche und Flüsse als Linie.</li>
<li><b>Gebäude:</b> alle Gebäudeumrisse.</li>
</ul>
<p>Bei großen Gebieten kann die Karte langsam werden, wenn alles
gleichzeitig sichtbar ist. Dann blendest du einzelne Ebenen aus.</p>

<p><b>4. Hintergrundkarte wählen</b><br>
Unter <i>Kartenquelle</i> wechselst du zwischen Straßenkarte und
Satellitenbild. <i>Satellit + Relief</i> und <i>Karte + Relief</i>
legen ein Schattenrelief darüber: Täler, Hänge und Bergkämme werden
sichtbar, das hilft beim Wählen des Ausschnitts. Die
<i>Eisenbahnkarte</i> legt Gleise und Bahnhöfe darüber, praktisch zum
Prüfen von Strecken. Das <i>Maß-Gitter</i>
hilft beim Abschätzen von Abständen und Größen.</p>

<p><b>5. Eigenes zeichnen</b><br>
Mit <i>Zeichnen</i> legst du eigene Objekte an:</p>
<ul>
<li>Zuerst auf <i>Straße</i>, <i>Fluss</i> oder <i>Gebäude</i> klicken.
Der Knopf bestimmt, was du zeichnest.</li>
<li>Dann die Punkte nacheinander auf der Karte anklicken. Eine rote
Linie zeigt den Verlauf.</li>
<li>Mit <i>Fertig</i> (oder einem Doppelklick) wird das Objekt
übernommen. Eine Straße und ein Fluss brauchen mindestens 2 Punkte,
ein Gebäude mindestens 3. Ein Gebäude schließt sich von selbst.</li>
<li>Nach <i>Fertig</i> ist das Zeichnen beendet. Für das nächste Objekt
wieder zuerst den Knopf (<i>Straße</i>, <i>Fluss</i> oder
<i>Gebäude</i>) anklicken.</li>
<li>Das Objekt liegt in der passenden Ebene (Straßen, Flüsse oder
Gebäude). Ist deren Haken im Layer-Panel aus, siehst du es nicht.</li>
<li>Ein Klick auf das Objekt zeigt seine Eckpunkte. Die Punkte lassen
sich ziehen.</li>
</ul>
<p><i>JSON Export</i> und <i>JSON Import</i> speichern und laden die
Objekte der Karte als Datei.</p>

<p><b>6. Werkzeuge</b><br>
In der Leiste oben wählst du, was ein Klick auf die Karte tut:
Marker setzen, zwei Ecken für eine Auswahl festlegen oder mit dem
Messwerkzeug Koordinaten und Entfernungen anzeigen.</p>

<p><b>7. Speichern und weiterverarbeiten</b><br>
Speichere dein Projekt mit <i>Datei &rarr; Speichern</i>. Für den
Import in Transport Fever 3 gibt es unter <i>Werkzeuge</i> den
OSM-Export, die Heightmap, die Vorab-Prüfung und den Mod-Checker.
Die Schritte dazu stehen unter <i>Hilfe &rarr; Import-Anleitung</i>.</p>
"""


def create_project_dock(parent):

    dock = QDockWidget("Projekt", parent)
    dock.setAllowedAreas(Qt.LeftDockWidgetArea)

    parent.project_list = QListWidget()

    dock.setWidget(
        parent.project_list
    )

    return dock
    

def create_properties_dock(parent):

    dock = QDockWidget("Eigenschaften", parent)
    dock.setAllowedAreas(Qt.RightDockWidgetArea)

    form = QWidget()

    layout = QFormLayout(form)

    parent.prop_id = QLabel()

    parent.prop_name = QLineEdit()
    parent.prop_name.editingFinished.connect(
        parent._marker_name_changed
    )

    parent.prop_lat = QLabel()

    parent.prop_lon = QLabel()

    parent.delete_marker_button = QPushButton(
        "Marker löschen"
    )

    parent.delete_marker_button.clicked.connect(
        parent._delete_marker
    )

    layout.addRow(
        "ID:",
        parent.prop_id
    )

    layout.addRow(
        "Name:",
        parent.prop_name
    )

    layout.addRow(
        "Breite:",
        parent.prop_lat
    )

    layout.addRow(
        "Länge:",
        parent.prop_lon
    )

    layout.addRow(
       parent.delete_marker_button
    ) 

    # Anleitung unter dem Formular: scrollbar, damit sie auch in einem
    # schmalen Dock lesbar bleibt.
    guide = QTextBrowser()
    guide.setOpenLinks(False)
    guide.setHtml(GUIDE_HTML)

    container = QWidget()

    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(0, 0, 0, 0)

    container_layout.addWidget(form)
    container_layout.addWidget(guide, 1)

    dock.setMinimumWidth(280)

    dock.setWidget(container)

    return dock