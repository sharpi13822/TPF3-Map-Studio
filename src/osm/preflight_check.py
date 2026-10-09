"""
Vorab-Pruefung der geladenen OSM-Daten.

Zwei Arten von Ergebnissen, bewusst getrennt:

- Strukturelle Plausibilitaets-Checks (status ok/warning/error): Dinge,
  die unabhaengig vom konkreten Gebiet immer gelten (z.B. "ein Weg
  braucht mindestens 2 Knoten"). Nur hierfuer wird tatsaechlich eine
  Ampel gesetzt.
- Informative Kennzahlen (status info): Dichte-Werte wie "Gebaeude pro
  km²". Es gibt keine seriöse, gebietsunabhaengige Schwelle dafuer, ob
  ein Wert "richtig" ist - Rheintal und Nuernberg sind nicht vergleichbar.
  Diese Werte werden nur angezeigt, nicht bewertet; die Einschaetzung
  bleibt bei dir.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.osm.overpass_query_builder import OverpassQueryConfig
from src.i18n import tr


@dataclass
class CheckResult:
    label: str
    # "ok" | "warning" | "error" | "info"
    status: str
    message: str


STATUS_ICONS = {
    "ok": "✅",
    "warning": "⚠️",
    "error": "❌",
    "info": "ℹ️",
}


def _estimate_area_km2(selection) -> float | None:
    """
    Grobe Flaechenschaetzung des Kartenausschnitts in km².

    Bei einer gedrehten Auswahl (Rechteck-Tool) liegt die reale Groesse
    bereits in Metern vor - das ist exakt. Bei einer einfachen
    achsenparallelen Bbox wird ueber die Breiten-/Laengengrad-Spannen
    genaehert (dieselbe Naeherung wie in Selection.from_center()).
    """

    if selection is None:
        return None

    if selection.width_m and selection.height_m:
        return selection.width_m * selection.height_m / 1_000_000

    lat_span_m = (selection.max_lat - selection.min_lat) * 111_320
    center_lat = (selection.min_lat + selection.max_lat) / 2
    lon_span_m = (
        (selection.max_lon - selection.min_lon)
        * 111_320
        * math.cos(math.radians(center_lat))
    )

    area = abs(lat_span_m * lon_span_m) / 1_000_000

    return area if area > 0 else None


def run_preflight_check(
    project,
    overpass_config: OverpassQueryConfig | None = None,
) -> list[CheckResult]:
    """
    Prueft das aktuell geladene OSM-Projekt auf offensichtliche
    Auffaelligkeiten, bevor weitere Dateien erzeugt werden.
    """

    results: list[CheckResult] = []

    selection = project.selection
    osm = project.osm

    if overpass_config is None:
        overpass_config = OverpassQueryConfig()

    # -------------------------------------------------------------
    # Grundvoraussetzungen
    # -------------------------------------------------------------

    if selection is None:

        results.append(
            CheckResult(
                tr("Kartenausschnitt"), "error",
                tr("Kein Kartenausschnitt gesetzt (Rechteck-Tool verwenden).")
            )
        )

        return results

    if osm.node_count == 0 and osm.way_count == 0:

        results.append(
            CheckResult(
                tr("OSM-Daten"), "error",
                tr("Keine OSM-Daten geladen. Zuerst 'OSM laden' ausführen.")
            )
        )

        return results

    # -------------------------------------------------------------
    # Strukturelle Plausibilitaet
    # -------------------------------------------------------------

    if osm.way_count == 0:

        results.append(
            CheckResult(
                tr("Wege"), "error",
                tr("0 Wege geladen - die Overpass-Antwort war vermutlich leer "
                "oder der Download ist fehlgeschlagen.")
            )
        )

    else:

        results.append(
            CheckResult(
                tr("Wege"), "ok",
                tr("{way_count} Wege geladen.").format(way_count=osm.way_count)
            )
        )

        ratio = osm.node_count / osm.way_count

        if ratio < 1.5:

            results.append(
                CheckResult(
                    tr("Knoten/Wege-Verhältnis"), "error",
                    tr("Nur {ratio:.2f} Knoten pro Weg im Schnitt ({node_count} Knoten, {way_count} Wege). Ein Weg braucht mindestens 2 Knoten - der Download wirkt unvollständig.").format(ratio=ratio, node_count=osm.node_count, way_count=osm.way_count)
                )
            )

        else:

            results.append(
                CheckResult(
                    tr("Knoten/Wege-Verhältnis"), "ok",
                    tr("{ratio:.2f} Knoten pro Weg im Schnitt - unauffällig.").format(ratio=ratio)
                )
            )

    # -------------------------------------------------------------
    # Kategorie-Zaehlungen, nur bewertet, wenn die Kategorie in der
    # Overpass-Abfrage tatsaechlich aktiviert war
    # -------------------------------------------------------------

    category_checks = (
        ("highways", tr("Straßen"), list(osm.highways())),
        ("buildings", tr("Gebäude"), list(osm.buildings())),
        ("railways", tr("Gleise"), list(osm.railways())),
    )

    for toggle_name, label, items in category_checks:

        enabled = getattr(overpass_config, toggle_name)

        if not enabled:
            continue

        if len(items) == 0:

            results.append(
                CheckResult(
                    label, "warning",
                    tr("'{label}' war in der Overpass-Abfrage aktiviert, aber es wurden 0 gefunden.").format(label=label)
                )
            )

        else:

            results.append(
                CheckResult(
                    label, "ok",
                    tr("{count}× {label} gefunden.").format(count=len(items), label=label)
                )
            )

    # -------------------------------------------------------------
    # Orte - besonders hervorgehoben, da frueher in diesem Projekt
    # schon einmal 0 statt der tatsaechlich vorhandenen Orte
    # aufgetreten ist
    # -------------------------------------------------------------

    places = list(osm.places())

    if overpass_config.places:

        if len(places) == 0:

            results.append(
                CheckResult(
                    tr("Orte"), "error",
                    tr("'Orte' war aktiviert, aber 0 Städte/Dörfer gefunden. "
                    "Für ein bewohntes Gebiet ungewöhnlich - Download prüfen, "
                    "bevor der grosse Lauf gestartet wird.")
                )
            )

        else:

            results.append(
                CheckResult(
                    tr("Orte"), "ok",
                    tr("{count} Orte gefunden.").format(count=len(places))
                )
            )

    else:

        results.append(
            CheckResult(
                tr("Orte"), "info",
                tr("'Orte' war in der Overpass-Abfrage nicht aktiviert - "
                "unter Werkzeuge > Overpass-Abfrage einschalten, falls "
                "die Städteanzahl geprüft werden soll.")
            )
        )

    # -------------------------------------------------------------
    # Flaeche und Dichte - rein informativ, keine Bewertung
    # -------------------------------------------------------------

    area_km2 = _estimate_area_km2(selection)

    if area_km2:

        results.append(
            CheckResult(
                tr("Fläche"), "info",
                tr("Ausgewähltes Gebiet: ca. {area_km2:.2f} km².").format(area_km2=area_km2)
            )
        )

        highways = [w for w in osm.highways()]
        buildings = [w for w in osm.buildings()]

        if highways:

            results.append(
                CheckResult(
                    tr("Straßendichte"), "info",
                    tr("{value:.1f} Straßen-Segmente pro km² (nur zur eigenen Einschätzung, kein automatisches Urteil).").format(value=len(highways) / area_km2)
                )
            )

        if buildings:

            results.append(
                CheckResult(
                    tr("Gebäudedichte"), "info",
                    tr("{value:.1f} Gebäude pro km² (nur zur eigenen Einschätzung).").format(value=len(buildings) / area_km2)
                )
            )

        if places:

            results.append(
                CheckResult(
                    tr("Ortsdichte"), "info",
                    tr("{value:.2f} Orte pro 100 km² (nur zur eigenen Einschätzung).").format(value=len(places) / area_km2 * 100)
                )
            )

    return results
