"""
Bahnhoefe aus den geladenen OSM-Daten speichern (Knopf "Bahnhoefe aus OSM..." im Heightmap-Dialog).

Die eigentliche Arbeit macht src/heightmap/station_export.py; hier steht nur die Bedienung
(Dateiauswahl und Meldungen).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox

from src.heightmap.station_export import collect_stations, summary, write_stations

TITLE = "Bahnhöfe aus OSM"


def save_stations_dialog(parent, selection, osm) -> bool:
    """
    Liest die Bahnhoefe, laesst den Speicherort waehlen und schreibt .json und .csv.
    Gibt True zurueck, wenn Dateien geschrieben wurden.
    """

    try:
        data = collect_stations(osm, selection)
    except Exception as error:  # noqa: BLE001 - dem Nutzer melden, nicht abstuerzen
        QMessageBox.warning(parent, TITLE, f"Die Bahnhöfe konnten nicht gelesen werden:\n{error}")
        return False

    if not data["stations"]:
        QMessageBox.information(
            parent,
            TITLE,
            "In den geladenen OSM-Daten wurden keine Bahnhöfe oder Haltepunkte gefunden.\n\n"
            "Zuerst Werkzeuge → OSM laden ausführen und die Ebene Eisenbahn laden. Bleibt es leer, "
            "lädt die OSM-Abfrage Bahnhofsdaten (railway=station/halt/platform, "
            "building=train_station) möglicherweise nicht mit.",
        )
        return False

    chosen, _selected_filter = QFileDialog.getSaveFileName(
        parent,
        TITLE,
        str(Path.home() / "bahnhoefe.json"),
        "JSON (*.json)",
    )

    if not chosen:
        return False

    try:
        json_path, csv_path = write_stations(data, chosen)
    except OSError as error:
        QMessageBox.warning(parent, TITLE, f"Die Dateien konnten nicht geschrieben werden:\n{error}")
        return False

    QMessageBox.information(
        parent,
        TITLE,
        f"{summary(data)}\n\nGespeichert:\n{json_path}\n{csv_path}",
    )

    return True
