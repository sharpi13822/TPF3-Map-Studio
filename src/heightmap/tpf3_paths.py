"""
Findet den heightmaps-Ordner von Transport Fever 3 im Userdata-Verzeichnis.

Steam-App-ID von TPF3: 3493540. Der Userdata-Ordner liegt nicht immer unter
"C:/Program Files (x86)/Steam" - bei einem Nutzer z.B. auf
"D:/Steam/userdata/<Nummer>/3493540/local". Deshalb wird zuerst der in der
Windows-Registry eingetragene Steam-Pfad gesucht, dann typische Orte auf
allen Laufwerken. Ergebnis ist nur ein Vorschlag fuer den Speichern-Dialog,
der Nutzer kann jederzeit einen anderen Ordner waehlen.
"""

from __future__ import annotations

import os
import string
from pathlib import Path

TPF3_STEAM_APP_ID = "3493540"


def _steam_roots() -> list[Path]:

    roots: list[Path] = []

    # Windows: Steam-Pfad aus der Registry (zuverlaessigste Quelle)
    try:
        import winreg  # nur unter Windows vorhanden

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"
        ) as key:
            value, _ = winreg.QueryValueEx(key, "SteamPath")
            roots.append(Path(value))
    except Exception:
        pass

    # Typische Orte auf allen Laufwerken (Windows)
    if os.name == "nt":
        for letter in string.ascii_uppercase:
            drive = Path(f"{letter}:/")
            for sub in ("Steam", "Program Files (x86)/Steam", "Program Files/Steam"):
                roots.append(drive / sub)

    # Linux / macOS
    home = Path.home()
    roots.append(home / ".local/share/Steam")
    roots.append(home / ".steam/steam")
    roots.append(home / "Library/Application Support/Steam")

    return roots


def _other_store_folders() -> list[Path]:
    """GOG und Epic: gleicher Userdata-Ordner unter AppData/Roaming."""

    folders: list[Path] = []

    appdata = os.environ.get("APPDATA")

    if appdata:
        folders.append(Path(appdata) / "Transport Fever 3" / "heightmaps")

    folders.append(
        Path.home() / "Library/Application Support/Transport Fever 3/heightmaps"
    )
    folders.append(Path.home() / ".local/share/Transport Fever 3/heightmaps")

    return folders


def find_tpf3_heightmaps_folder() -> Path | None:
    """Gibt den heightmaps-Ordner zurueck, sonst None. Bei mehreren
    Steam-Konten gewinnt der zuletzt veraenderte Ordner."""

    found: list[Path] = []

    seen: set[str] = set()

    for root in _steam_roots():

        key = str(root).lower()

        if key in seen:
            continue

        seen.add(key)

        userdata = root / "userdata"

        try:
            if not userdata.is_dir():
                continue

            for candidate in userdata.glob(
                f"*/{TPF3_STEAM_APP_ID}/local/heightmaps"
            ):
                if candidate.is_dir():
                    found.append(candidate)
        except OSError:
            continue

    for folder in _other_store_folders():
        try:
            if folder.is_dir():
                found.append(folder)
        except OSError:
            continue

    if not found:
        return None

    return max(found, key=lambda p: p.stat().st_mtime)
