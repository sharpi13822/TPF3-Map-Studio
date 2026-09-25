from __future__ import annotations

import math
from typing import Any

from src.tpf2.tpf2_geometry import TPF2Geometry


class TPF2Exporter:
    STREET_TYPE = "standard/town_medium_new.lua"
    TRACK_TYPE = "standard.lua"

    def __init__(self, origin_lat: float, origin_lon: float, rotation_deg: float = 0.0):
        self.geometry = TPF2Geometry(origin_lat, origin_lon, rotation_deg)

    @classmethod
    def from_coordinates(cls, coordinates, rotation_deg: float = 0.0):
        if not coordinates:
            raise ValueError("Keine Koordinaten vorhanden.")
        lats = [float(p[0]) for p in coordinates]
        lons = [float(p[1]) for p in coordinates]
        return cls(
            (min(lats) + max(lats)) / 2.0,
            (min(lons) + max(lons)) / 2.0,
            rotation_deg,
        )

    @classmethod
    def from_selection(cls, selection):
        """Erstellt den Exporter direkt aus einer (ggf. gedrehten)
        Selection - Mittelpunkt und Drehwinkel kommen 1:1 von dort,
        statt wie bei from_coordinates() aus der Bounding Box der
        tatsaechlichen Strassen-/Gleisgeometrien hergeleitet zu werden
        (was bei einem gedrehten Band den falschen Ursprung ergaebe).
        """
        center_lat, center_lon = selection.center
        return cls(center_lat, center_lon, selection.rotation_deg)

    @classmethod
    def from_export_data(cls, export_data):
        coordinates = []
        for name in ("roads", "railways"):
            for item in getattr(export_data, name, []):
                geometry = getattr(item, "geometry", None)
                if cls._is_line_geometry(geometry):
                    coordinates.extend(
                        (float(p[0]), float(p[1])) for p in geometry
                    )
        if not coordinates:
            raise ValueError("Keine Liniengeometrien für TPF2 vorhanden.")
        return cls.from_coordinates(coordinates)

    def export(self, export_data) -> dict[str, Any]:
        nodes = {}
        edges = {}

        roads = self._export_lines(
            getattr(export_data, "roads", []),
            "street", nodes, edges, "r"
        )
        railways = self._export_lines(
            getattr(export_data, "railways", []),
            "track", nodes, edges, "t"
        )

        return {
            "version": 2,
            "nodes": nodes,
            "edges": edges,
            "roads": roads,
            "railways": railways,
        }

    def _export_lines(self, items, edge_kind, nodes, edges, prefix):
        result = []

        for item in items:
            geometry = getattr(item, "geometry", None)
            if not self._is_line_geometry(geometry):
                continue

            local = self.geometry.line(geometry)
            if len(local) < 2:
                continue

            item_edges = []

            for index in range(len(local) - 1):
                p0 = local[index]
                p1 = local[index + 1]

                x0, y0 = float(p0[0]), float(p0[1])
                x1, y1 = float(p1[0]), float(p1[1])
                dx, dy = x1 - x0, y1 - y0

                if math.hypot(dx, dy) < 0.05:
                    continue

                node0 = f"{prefix}{item.id}_{index}"
                node1 = f"{prefix}{item.id}_{index + 1}"
                edge_id = f"{prefix}{item.id}_{index}"

                nodes.setdefault(node0, {"pos": [x0, y0]})
                nodes.setdefault(node1, {"pos": [x1, y1]})

                edge = {
                    "id": edge_id,
                    "node0": node0,
                    "node1": node1,
                    "tangent0": [dx, dy, 0.0],
                    "tangent1": [dx, dy, 0.0],
                }

                if edge_kind == "track":
                    props = dict(getattr(item, "properties", {}) or {})
                    edge["track"] = {
                        "type": "rail",
                        "electrified": bool(props.get("electrified", False)),
                    }
                else:
                    edge["street"] = {
                        "type": "road",
                        "oneway": False,
                    }

                edges[edge_id] = edge
                item_edges.append(edge_id)

            if item_edges:
                result.append({
                    "id": item.id,
                    "edge_ids": item_edges,
                    "properties": dict(getattr(item, "properties", {}) or {}),
                })

        return result

    @staticmethod
    def _is_line_geometry(geometry):
        if not isinstance(geometry, (list, tuple)) or len(geometry) < 2:
            return False
        return all(
            isinstance(p, (list, tuple))
            and len(p) == 2
            and all(isinstance(v, (int, float)) for v in p)
            for p in geometry
        )