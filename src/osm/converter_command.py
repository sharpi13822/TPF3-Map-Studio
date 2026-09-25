"""
Baut den Aufrufbefehl fuer den externen OSM-TPF-Converter (main.exe /
main.py aus dem OSM-TPF2-Importer-Projekt) aus der aktuellen Selection.

Offizielle Befehlssyntax (siehe python/README.md des Importer-Projekts):

    main.exe <input.osm> <output.lua> <breite_m,hoehe_m> <minlat,minlon,maxlat,maxlon>

WICHTIG: Der Converter kennt keine Drehung - er erwartet eine einfache,
achsenparallele Bounding Box und skaliert sie 1:1 auf die Kartenraender.
Bei einer gedrehten Selection (Rechteck-Tool mit Drehwinkel != 0) passt
die hier berechnete Bbox NICHT sauber zum gedrehten Band - das wird
deshalb explizit als Warnung zurueckgegeben, statt es zu verschweigen.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.map.objects.selection import Selection


@dataclass
class ConverterCommand:
    command: str
    is_rotated: bool
    width_m: float
    height_m: float


def _effective_size_m(selection: Selection) -> tuple[float, float]:
    """
    Liefert (width_m, height_m) der Selection in Metern - direkt aus dem
    Rechteck-Tool, falls vorhanden, sonst ueber dieselbe Grad->Meter-
    Naeherung wie an anderen Stellen im Studio (z.B. preflight_check.py).
    """

    if selection.width_m and selection.height_m:
        return selection.width_m, selection.height_m

    center_lat = (selection.min_lat + selection.max_lat) / 2

    height_m = (selection.max_lat - selection.min_lat) * 111_320
    width_m = (
        (selection.max_lon - selection.min_lon)
        * 111_320
        * math.cos(math.radians(center_lat))
    )

    return abs(width_m), abs(height_m)


def build_converter_command(
    selection: Selection,
    osm_file_path: str,
    output_file: str = "osmdata.lua",
    exe_name: str = "main.exe",
) -> ConverterCommand:

    width_m, height_m = _effective_size_m(selection)

    command = (
        f'{exe_name} "{osm_file_path}" {output_file} '
        f'{width_m:.0f},{height_m:.0f} '
        f'{selection.min_lat:.6f},{selection.min_lon:.6f},'
        f'{selection.max_lat:.6f},{selection.max_lon:.6f}'
    )

    return ConverterCommand(
        command=command,
        is_rotated=bool(selection.rotation_deg),
        width_m=width_m,
        height_m=height_m,
    )
