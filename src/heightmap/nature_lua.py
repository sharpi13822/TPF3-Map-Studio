"""Natur-Details-Plan (JSON) -> naturdata.lua fuer den Map-Studio-Import-Mod.

Der Mod baut daraus im Spiel Weinberge und Felder als Reihen und Mauern als Linien
(nach Mustern, die der Spieler vorher auf die Karte setzt). Koordinaten in
Spielmetern ab Kartenmitte, wie im Plan.

Aufruf:  python -m src.heightmap.nature_lua <plan.json> <naturdata.lua>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

AREA_KINDS = ("vineyard", "field")
LINE_KINDS = ("wall",)


def _num(value: float) -> str:
    text = f"{float(value):.1f}"
    return "0.0" if text == "-0.0" else text


def _flat(points) -> str:
    return ",".join(f"{_num(x)},{_num(y)}" for x, y in points)


def plan_to_lua(plan: dict) -> tuple[str, dict]:
    """Gibt den Lua-Text und eine Zaehlung je Art zurueck."""

    areas, lines = [], []
    counts = {kind: 0 for kind in AREA_KINDS + LINE_KINDS}

    for feature in plan.get("features", []):
        kind = feature.get("kind")
        points = feature.get("points") or []
        osm_id = int(feature.get("osm_id") or 0)

        if kind in AREA_KINDS and len(points) >= 3:
            direction = feature.get("row_direction_deg") or 0.0
            areas.append(f'\t\t{{ k = "{kind}", id = {osm_id}, r = {_num(direction)}, p = {{ {_flat(points)} }} }},')
            counts[kind] += 1
        elif kind in LINE_KINDS and len(points) >= 2:
            lines.append(f'\t\t{{ k = "{kind}", id = {osm_id}, p = {{ {_flat(points)} }} }},')
            counts[kind] += 1

    text = "\n".join(
        [
            "-- Natur-Daten fuer den Map-Studio-Import (erzeugt vom TPF3 Map Studio)",
            "return {",
            "\tformat = 1,",
            "\tflaechen = {",
            *areas,
            "\t},",
            "\tlinien = {",
            *lines,
            "\t},",
            "}",
            "",
        ]
    )
    return text, counts


def write_naturdata(plan_path, out_path) -> dict:
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    text, counts = plan_to_lua(plan)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    return counts


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print("Aufruf: python -m src.heightmap.nature_lua <plan.json> <naturdata.lua>")
        return 2
    counts = write_naturdata(args[0], args[1])
    print(
        "naturdata.lua geschrieben: "
        f"{counts['vineyard']} Weinberge, {counts['field']} Felder, {counts['wall']} Mauern -> {args[1]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
