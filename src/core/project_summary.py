"""
Leichtgewichtiges Einlesen von .tpf2ms-Projektdateien fuer das
Projekt-Dashboard.

Bewusst NICHT ueber ProjectSerializer.load(): das wuerde ein volles
Project/LayerManager-Objekt aufbauen und die OSM-Daten vollstaendig
deserialisieren - fuer eine Uebersicht ueber ggf. viele Projekte
unnoetig teuer. Stattdessen wird die JSON-Datei direkt gelesen und nur
die fuer die Uebersicht relevanten Felder extrahiert.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectSummary:

    file_path: Path
    name: str
    author: str
    modified_field: str
    file_modified_at: str

    has_selection: bool
    selection_text: str

    has_osm: bool
    way_count: int
    node_count: int

    heightmap_exported: bool
    heightmap_exported_at: str

    error: str | None = None


def _selection_text(selection_data: dict | None) -> str:

    if not selection_data:
        return "kein Kartenausschnitt"

    width_m = selection_data.get("width_m")
    height_m = selection_data.get("height_m")
    rotation_deg = selection_data.get("rotation_deg") or 0.0

    if width_m and height_m:

        text = f"{width_m / 1000:.2f} x {height_m / 1000:.2f} km"

        if rotation_deg:
            text += f", {rotation_deg:.1f}° gedreht"

        return text

    min_lat = selection_data.get("min_lat", 0.0)
    max_lat = selection_data.get("max_lat", 0.0)
    min_lon = selection_data.get("min_lon", 0.0)
    max_lon = selection_data.get("max_lon", 0.0)

    return (
        f"Bbox {max_lat - min_lat:.4f}° x {max_lon - min_lon:.4f}°"
    )


def load_project_summary(path: Path) -> ProjectSummary:
    """
    Liest eine einzelne .tpf2ms-Datei und extrahiert die fuer das
    Dashboard relevanten Eckdaten. Bei einem Lesefehler wird eine
    ProjectSummary mit gesetztem 'error'-Feld zurueckgegeben statt eine
    Exception zu werfen - ein defektes Projekt soll die Uebersicht der
    uebrigen Projekte nicht verhindern.
    """

    try:
        file_modified_at = ""

        try:
            import datetime

            file_modified_at = datetime.datetime.fromtimestamp(
                path.stat().st_mtime
            ).isoformat(timespec="seconds")
        except OSError:
            pass

        data = json.loads(path.read_text(encoding="utf-8"))

        project_data = data.get("project", {})
        selection_data = data.get("selection")
        osm_data = data.get("osm") or {}

        way_count = len(osm_data.get("ways", []))
        node_count = len(osm_data.get("nodes", []))

        heightmap_path = project_data.get("heightmap_export_path", "")

        return ProjectSummary(
            file_path=path,
            name=project_data.get("name", path.stem),
            author=project_data.get("author", ""),
            modified_field=project_data.get("modified", ""),
            file_modified_at=file_modified_at,
            has_selection=selection_data is not None,
            selection_text=_selection_text(selection_data),
            has_osm=way_count > 0 or node_count > 0,
            way_count=way_count,
            node_count=node_count,
            heightmap_exported=bool(heightmap_path),
            heightmap_exported_at=project_data.get(
                "heightmap_exported_at", ""
            ),
        )

    except (OSError, json.JSONDecodeError, AttributeError) as exc:

        return ProjectSummary(
            file_path=path,
            name=path.stem,
            author="",
            modified_field="",
            file_modified_at="",
            has_selection=False,
            selection_text="",
            has_osm=False,
            way_count=0,
            node_count=0,
            heightmap_exported=False,
            heightmap_exported_at="",
            error=str(exc),
        )


def scan_projects_folder(folder: Path) -> list[ProjectSummary]:
    """
    Findet alle .tpf2ms-Dateien unterhalb von folder (rekursiv, da
    Projekte oft nach Region in Unterordnern abgelegt werden) und liest
    deren Eckdaten ein.
    """

    if not folder.is_dir():
        return []

    summaries = [
        load_project_summary(path)
        for path in sorted(folder.rglob("*.tpf2ms"))
    ]

    return summaries
