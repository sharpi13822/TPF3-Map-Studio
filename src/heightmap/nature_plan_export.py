"""Natur-Details-Plan neben der Biome-Maske speichern (ein Klick im Biome-Dialog)."""

from __future__ import annotations

from pathlib import Path

from src.heightmap.nature_plan import collect_features, write_csv, write_json

DEFAULT_MIN_AREA_M2 = 500.0


def plan_folder_for(mask_path, game_folder=None) -> Path:
    """Ordner fuer den Plan: neben der Maske, ausser sie liegt im Biome-Ordner
    des Spiels - dort sollen keine CSV/JSON-Dateien herumliegen."""

    folder = Path(mask_path).parent

    if game_folder is not None:
        try:
            if folder.resolve() == Path(game_folder).resolve():
                return Path.home() / "Documents" / "TPF3-Map-Studio" / "plaene"
        except OSError:
            pass

    return folder


def save_plan_for_mask(osm, selection, mask_path, game_folder=None,
                       min_area_m2: float = DEFAULT_MIN_AREA_M2):
    """Schreibt <Maskenname>_natur_details_plan.csv/.json.

    Gibt (csv_pfad, json_pfad) zurueck, oder None, wenn nichts gefunden wurde."""

    features = collect_features(osm, selection, min_area_m2=float(min_area_m2))

    if not features:
        return None

    base = plan_folder_for(mask_path, game_folder) / (
        Path(mask_path).stem + "_natur_details_plan"
    )

    csv_path = base.with_suffix(".csv")
    json_path = base.with_suffix(".json")

    write_csv(features, csv_path)
    write_json(features, json_path)

    return csv_path, json_path
