"""
Bahnhoefe fuer die Studio-Karte aufbereiten (Ebene "Bahnhoefe").

Die Bahnhoefe liegen im Export in Metern ab Kartenmitte (x, y). Die Karte braucht Breite und Laenge;
die Rueckrechnung macht TPF2Geometry.inverse() mit derselben Kartenmitte und Drehung wie beim Export.
Reine Rechnung, keine Oberflaeche - deshalb testbar.
"""

from __future__ import annotations

from src.tpf2.tpf2_geometry import TPF2Geometry

# Nur diese Zusaetze stehen im Schild; "zweifelhaft" und Betriebsbahnhof zeigt die Farbe des Kreises.
STATUS_TEXT = {
    "aufgegeben": "aufgegeben",
    "im_bau": "im Bau",
}


def _label(station: dict) -> str:
    name = (station.get("name") or "").strip() or "(ohne Namen)"
    status = STATUS_TEXT.get(station.get("status") or "")
    return f"{name} ({status})" if status else name


def station_marker_data(data: dict) -> list[dict]:
    """Liste fuer window.MapApi.showStations(): id, label, kind, status, doubtful, lat, lon."""

    info = data["map"]
    geometry = TPF2Geometry(
        info["center_lat"], info["center_lon"], info.get("rotation_deg", 0.0)
    )

    result = []

    for station in data.get("stations", []):
        lat, lon = geometry.inverse(station["x"], station["y"])
        result.append({
            "id": station.get("id"),
            "label": _label(station),
            "kind": station.get("kind", ""),
            "status": station.get("status", ""),
            "doubtful": bool(station.get("doubtful")),
            "lat": round(lat, 7),
            "lon": round(lon, 7),
        })

    return result
