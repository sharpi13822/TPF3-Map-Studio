from pathlib import Path

from PySide6.QtGui import QIcon


ICON_DIR = Path(__file__).parent.parent / "icons" / "material"


def icon(name: str) -> QIcon:
    path = ICON_DIR / f"{name}.svg"

    print(path)
    print(path.exists())

    return QIcon(str(path))