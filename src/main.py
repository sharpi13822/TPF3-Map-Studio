import sys

# ---------------------------------------------------------------------
# WICHTIG: In einer per PyInstaller mit console=False gebauten exe
# existieren sys.stdout/sys.stderr nicht (sind None). Jeder print()
# oder traceback.print_exc() im gesamten Programm wuerde dann selbst
# mit einer AttributeError abstuerzen - und zwar lautlos, oft mitten in
# einem Hintergrund-Vorgang (z.B. OSM-Download), ohne dass je eine
# Fehlermeldung im Fenster erscheint. setup_logging() ersetzt beide
# deshalb VOR allem anderen durch einen Stream, der alles in die
# Logdatei schreibt (und beim normalen Python-Start zusaetzlich
# weiterhin auf die Konsole).
# ---------------------------------------------------------------------

from src.logging_config import install_qt_message_handler, setup_logging

setup_logging()

# Die Sprache muss feststehen, BEVOR src.window und die Dialoge importiert
# werden: Texte auf Modulebene werden beim Import einmal uebersetzt. Ein
# Sprachwechsel im Menue wirkt deshalb nach einem Neustart.
from src.i18n import get_language, init_language
from src.qt_translation import install_qt_translations

init_language()

from PySide6.QtWidgets import QApplication
from src.window import MainWindow


def main():
    install_qt_message_handler()

    app = QApplication(sys.argv)

    # Standardknoepfe von Qt (OK, Abbrechen, Ja, Nein ...) in der Studio-Sprache
    app._qt_translators = install_qt_translations(app, get_language())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
