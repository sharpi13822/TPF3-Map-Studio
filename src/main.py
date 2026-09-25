import sys
import io

# ---------------------------------------------------------------------
# WICHTIG: In einer per PyInstaller mit console=False gebauten exe
# existieren sys.stdout/sys.stderr nicht (sind None). Jeder print()
# oder traceback.print_exc() im gesamten Programm wuerde dann selbst
# mit einer AttributeError abstuerzen - und zwar lautlos, oft mitten in
# einem Hintergrund-Vorgang (z.B. OSM-Download), ohne dass je eine
# Fehlermeldung im Fenster erscheint. Deshalb hier VOR allem anderen
# durch einen harmlosen Platzhalter ersetzen, der .write()/.flush()
# einfach ignoriert, statt eine Exception zu werfen. Im normalen
# Python-Start (nicht gebaute exe) bleiben stdout/stderr unveraendert.
# ---------------------------------------------------------------------

if sys.stdout is None:
    sys.stdout = io.StringIO()

if sys.stderr is None:
    sys.stderr = io.StringIO()

from PySide6.QtWidgets import QApplication
from src.window import MainWindow


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()