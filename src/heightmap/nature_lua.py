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


def plan_to_lua(plan: dict, row_every: int = 1) -> tuple[str, dict]:
    """Gibt den Lua-Text und eine Zaehlung je Art zurueck. row_every: nur jede N-te Reihe bauen."""

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
            f"\treihe_jede = {max(1, int(row_every))},",
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


EMPTY_NATURDATA_LUA = plan_to_lua({"features": []})[0]


def features_to_lua(features, row_every: int = 1) -> tuple[str, dict]:
    """NatureFeature-Objekte (aus nature_plan.collect_features) -> Lua-Text, Zaehlung."""

    plan = {
        "features": [
            {
                "kind": f.kind,
                "osm_id": f.osm_id,
                "row_direction_deg": f.row_direction_deg,
                "points": list(f.points),
            }
            for f in features
        ]
    }
    return plan_to_lua(plan, row_every)


def add_to_content_json(text: str, filename: str = "naturdata.lua", after: str = "osmdata.lua") -> str:
    """Traegt eine Datei in die Liste von _content.json ein (das Spiel laedt nur gelistete Dateien)."""

    data = json.loads(text)
    files = list(data.get("files") or [])
    if filename not in files:
        index = files.index(after) + 1 if after in files else len(files)
        files.insert(index, filename)
    data["files"] = files
    return json.dumps(data, indent=4) + "\n"


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
