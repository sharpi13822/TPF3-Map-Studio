"""
Hinweise zu den Hoehen, die beim TPF3-Import eingetragen werden.

Das Spiel faerbt das Gelaende nach der Hoehe der importierten Werte: Fels ab etwa 325 bis 350 m,
Schnee ab etwa 375 bis 425 m. Liegt das ganze Gelaende hoeher (zum Beispiel bei Bern, 488 bis
936 m ueber Meer), wird es ohne den Haken "Werte auf Wasserhoehe 0 beziehen" komplett weiss.
"""

from __future__ import annotations

# Liegt schon die tiefste Stelle hoeher als dies, ist im Spiel alles Fels oder Schnee.
HIGH_TERRAIN_M = 300.0

# Ab dieser Hoehe faerbt das Spiel (nach den bisherigen Tests) Flaechen weiss.
SNOW_LINE_M = 375.0


def height_hint(range_min: float, range_max: float, water: float, relative: bool) -> str | None:
    """
    Kurzer Hinweis zu den Importwerten oder None. range_min/range_max sind die echten Hoehen
    (Meter ueber Meer) des Rasters, water die Wasserhoehe, relative = Haken "Werte auf
    Wasserhoehe 0 beziehen".
    """

    if not relative and range_min >= HIGH_TERRAIN_M:
        return (
            f"Achtung: Das ganze Gelände liegt über etwa {HIGH_TERRAIN_M:.0f} m. Im Spiel wird es "
            "dadurch komplett weiß (Schnee) oder grau (Fels). Den Haken „Werte auf Wasserhöhe 0 "
            "beziehen“ setzen und bei Bedarf „Höhen stauchen“ verwenden."
        )

    top = (range_max - water) if relative else range_max

    if top >= SNOW_LINE_M:
        return (
            f"Hinweis: Die höchsten Stellen liegen bei etwa {top:.0f} m. Ab etwa {SNOW_LINE_M:.0f} m "
            "färbt das Spiel weiß. „Höhen stauchen“ verringert das."
        )

    return None
