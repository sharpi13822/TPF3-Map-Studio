"""
Strassen- und Gleisnetz aus OSM fuer den TPF3-Mod "Map Studio Import".

Das Studio schreibt keine Spielobjekte, sondern eine Datendatei (Knoten und
Wege). Ein kleiner Mod im Spiel liest sie und baut das Netz Weg fuer Weg.

Im Spiel getestet (Oktober 2026, Testmod osm_import_test_1):
- Strassen, Gleise, Kreuzungen (gemeinsame Knoten), Bruecken (Typ trestle) und
  Tunnel (tunnel_a_car fuer Strassen, tunnel_a fuer Gleise) werden gebaut.
- Hoehen plant der Mod selbst: jeder Knoten bekommt EINMAL eine Hoehe aus dem
  Gelaende, danach wird das ganze Netz so geglaettet, dass die Steigungsgrenze
  eingehalten wird. Das Studio schreibt deshalb nur x/y.
- Koordinaten: Meter ab Kartenmitte, x nach Osten, y nach Norden (wie bei den
  Staedten, siehe towns_export.py).

NICHT im Spiel getestet (nur hier im Studio geprueft):
- die Zuordnung OSM-Typ -> Strassenvorlage (Tabellen unten),
- Bruecken-Typ nach Laenge, Strassenbahn, gemeinsame Knoten von Strasse und
  Gleis (werden hier absichtlich getrennt),
- die Vereinfachung der Linien (Douglas-Peucker, Mindestabstand).

NETWORK_EXPORT_VERSION = "v23"

Datenformat 3 (Datei osmdata.lua im Mod, Details siehe network_to_lua):
  nodes: je Zeile "x y", Knoten-id = Zeilennummer (ab 1)
  ways:  je Zeile "art vorlage t typ maxG osmId n1 n2 ..."
(Format 2 ohne osmId liest der Mod weiterhin.)

Reihenfolge der Wege in der Datei: Bahn zuerst, dann Strassen nach Wichtigkeit.
Der Mod baut in dieser Reihenfolge; scheitern zwei Wege aneinander (Kollision),
trifft es so den unwichtigeren.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

from src.heightmap import network_cleanup
from src.tpf2.tpf2_geometry import TPF2Geometry

NETWORK_EXPORT_VERSION = "v23"

# ---------------------------------------------------------------------------
# Zuordnung OSM -> Strassenvorlage des Spiels
#
# Die Namen sind ENDUNGEN der Vorlagen (der Mod sucht die volle Vorlage in der
# Liste des Spiels). Sie stammen aus der Vorlagenliste des Spiels
# (api.res.streetTemplateRep), die Auswahl je OSM-Typ ist ein Vorschlag.
# ---------------------------------------------------------------------------

# Landstrassen (trunk/primary/secondary) sind in OSM meist zweispurig. Im Spiel zaehlt die Breite
# von country_new_small: 2 Fahrspuren (je 5 m) plus je 2 m Fussweg = 14 m. country_new_medium hat
# 4 und country_new_large 6 Fahrspuren (belegt im Spiel-Log, "Breite ..."-Zeilen).
HIGHWAY_TEMPLATES: dict[str, str] = {
    "motorway": "/highway/highway_new_large.street_template",
    "motorway_link": "/highway/highway_new_small.street_template",
    "trunk": "/country/country_new_small.street_template",
    "trunk_link": "/country/country_new_small.street_template",
    "primary": "/country/country_new_small.street_template",
    "primary_link": "/country/country_new_small.street_template",
    "secondary": "/country/country_new_small.street_template",
    "secondary_link": "/country/country_new_small.street_template",
    "tertiary": "/country/country_new_small.street_template",
    "tertiary_link": "/country/country_new_small.street_template",
    "unclassified": "/country/country_new_small.street_template",
    "residential": "/town/town_new_small.street_template",
    "living_street": "/town/town_new_xsmall.street_template",
    "service": "/town/town_new_xsmall.street_template",
}

# Standardmaessig NICHT exportiert (Parkplatzzufahrten gibt es tausende).
DEFAULT_HIGHWAYS = frozenset(HIGHWAY_TEMPLATES) - {"service"}

SKIP_SERVICE = frozenset({
    "parking_aisle", "driveway", "drive-through", "emergency_access",
})

# Hoechste Steigung je Strassenklasse (Anteil, 0.08 = 8 %). Fehlt ein Eintrag,
# gilt der Standard des Mods (0.12 fuer Strassen, 0.03 fuer Gleise).
# Schaetzwerte, im Spiel nicht geprueft; Strassen haben dort bis etwa 33 %
# funktioniert, 46 % wurden abgelehnt.
HIGHWAY_GRADE: dict[str, float] = {
    "motorway": 0.08,
    "motorway_link": 0.10,
    "trunk": 0.10,
}

RAIL_STANDARD = "/track/standard/standard.street_template"
RAIL_STANDARD_CAT = "/track/standard/standard_catenary.street_template"
RAIL_SIMPLE = "/track/simple/simple.street_template"
RAIL_SIMPLE_CAT = "/track/simple/simple_catenary.street_template"
RAIL_FAST = "/track/high_speed/high_speed.street_template"
RAIL_FAST_CAT = "/track/high_speed/high_speed_catenary.street_template"

TRAM_TEMPLATE = "/tram/tram_new.street_template"

# railway-Werte, die als Gleis exportiert werden
DEFAULT_RAILWAYS = frozenset({"rail", "light_rail"})

# Hoechste Steigung fuer Gleise ausser dem Standard (0.03 im Mod)
LIGHT_RAIL_GRADE = 0.05
TRAM_GRADE = 0.06

STREET_TUNNEL = "/tunnel_a_car.tunnel"
RAIL_TUNNEL = "/tunnel_a.tunnel"

# Bruecken: (bis Laenge in m, Typ). Reihenfolge wichtig. Typen im Spiel:
# cable, concrete, placeholder, steel, stone, suspension, tarch, trestle,
# trestle_s. Getestet ist nur "trestle"; lange Spannweiten sind ungeprueft.
DEFAULT_BRIDGE_TYPES: tuple[tuple[float, str], ...] = (
    (120.0, "/trestle.bridge"),
    (1.0e12, "/steel.bridge"),
)

# Einbahnstrassen: schmale Einbahn-Vorlage statt der zweispurigen. Im Spiel kollidierten
# parallele Richtungsfahrbahnen (je ein OSM-Weg mit oneway=yes) mit Kanten DERSELBEN
# Vorlage; Autobahnen haben keine Einbahn-Vorlage und bleiben wie sie sind.
# Die Namen stammen aus der Vorlagenliste des Spiels; die Fahrtrichtung folgt der
# Knotenreihenfolge (ungeprueft im Spiel).
ONEWAY_TEMPLATES: dict[str, str] = {
    "/country/country_new_large.street_template":
        "/town/town_new_one_way_medium.street_template",
    "/country/country_new_medium.street_template":
        "/town/town_new_one_way_medium.street_template",
    "/country/country_new_small.street_template":
        "/town/town_new_one_way_small.street_template",
    "/town/town_new_small.street_template":
        "/town/town_new_one_way_small.street_template",
    "/town/town_new_xsmall.street_template":
        "/town/town_new_one_way_xsmall.street_template",
}

ART_STREET = 0
ART_TRACK = 1

# Reihenfolge beim Bauen: kleinere Zahl zuerst. Bahn vor allen Strassen.
BUILD_RANK: dict[str, int] = {
    "railway=rail": 0,
    "railway=light_rail": 1,
    "railway=tram": 2,
    "highway=motorway": 10,
    "highway=motorway_link": 11,
    "highway=trunk": 12,
    "highway=trunk_link": 13,
    "highway=primary": 14,
    "highway=primary_link": 15,
    "highway=secondary": 16,
    "highway=secondary_link": 17,
    "highway=tertiary": 18,
    "highway=tertiary_link": 19,
    "highway=unclassified": 20,
    "highway=residential": 21,
    "highway=living_street": 22,
    "highway=service": 23,
}

KIND_NORMAL = 0
KIND_BRIDGE = 1
KIND_TUNNEL = 2


@dataclass
class NetworkOptions:
    include_streets: bool = True
    include_rail: bool = True
    include_tram: bool = False  # ungetestet, darum aus
    highways: frozenset = DEFAULT_HIGHWAYS
    railways: frozenset = DEFAULT_RAILWAYS
    include_bridges: bool = True
    include_tunnels: bool = True
    # Kuerzere "Brücken" (Durchlaesse, kleine Ueberfuehrungen) werden als
    # gewoehnliche Kante gebaut. Im Spiel scheiterten alle fuenf Gleisbruecken
    # mit 4 bis 20 m Laenge, die langen gingen.
    min_bridge_m: float = 25.0
    # Bruecken, die kuerzer als min_bridge_free_m sind, werden nur gebaut, wenn sie einen anderen Weg
    # (Strasse oder Gleis) kreuzen. Sonst sind es Durchlaesse ueber Baeche und Graeben, die es im Spiel
    # nicht gibt: Das Spiel setzt dort ein Holzdeck (Bockbruecke) mitten auf das Gleis, mit Gras darunter, und
    # die Strecke bekommt Knicke an den Enden. Im Netz vom Rhein kreuzen nur 3 von 18 Bruecken etwas.
    # 0 = alle Bruecken ab min_bridge_m bauen.
    min_bridge_free_m: float = 25.0
    # Einbahnstrassen (oneway=yes/-1, Kreisverkehr) mit schmaler Einbahn-Vorlage bauen.
    oneway_templates: bool = True
    # Linien vereinfachen: Formpunkte, die weniger als diese Abweichung
    # ausmachen, entfallen. Kreuzungen und Wegenden bleiben immer.
    simplify_tolerance_m: float = 3.0
    # Formpunkte naeher als dieser Abstand zum Nachbarn entfallen ebenfalls
    # (sehr kurze Kanten sind in TPF2 oft gescheitert, TPF3 ungeprueft).
    min_segment_m: float = 8.0
    # Groesster Abstand zweier Knoten: Auf laengeren Kanten werden gleichmaessig Knoten
    # eingefuegt (auf der Linie, die Form aendert sich nicht). Grund: Zwischen zwei Knoten
    # verlaeuft die Hoehe im Spiel geradlinig; bei Kanten von mehreren hundert Metern liegt das
    # Gleis dann ueber dem Gelaende (Damm) oder darin (Einschnitt mit Stuetzwand). In der
    # Rechnung an den Daten vom Rhein wich das Gleis auf 69 % der Strecke mehr als 1 m vom
    # Gelaende ab, mit Knoten alle 80 m und der Gleisterrasse (Heightmap) auf 0,5 %.
    # Bruecken und Tunnel bleiben unveraendert. 0 = aus.
    max_edge_m: float = 80.0
    # Die zusaetzlichen Knoten werden auf der URSPRUENGLICHEN OSM-Linie gesetzt (echte OSM-Punkte),
    # nicht auf der vereinfachten Sehne. Grund: Nach der Vereinfachung (3 m) bestehen zwei parallele
    # Gleise in einer Kurve aus langen Sehnen mit Knoten an verschiedenen Stellen; ihr Abstand
    # schwankte von 1,8 bis 4,7 m, im Spiel beruehren oder kreuzen sich die Gleise.
    # False = Knoten auf der Sehne (v15).
    max_edge_follows_osm: bool = True
    # Mindestabstand Strasse - Gleis (Mittellinie zu Mittellinie, in m). Die Strassenvorlage ist 14 m,
    # das Gleis mit Masten rund 7 m breit: Bei 9 m (Standard) beruehren sich die Raender nicht, die
    # Strassen bleiben nahe an ihrer OSM-Lage, aber es bleibt kein freier Streifen: Dort laesst sich im
    # Spiel weder Gelaende anheben noch etwas pflanzen. 14 m lassen etwa 3,5 m frei. Strassen, die
    # parallel dichter neben einem Gleis liegen, werden bis zu max_road_shift_m von ihm weg gerueckt
    # (sanft auslaufend). Bahnuebergaenge und kreuzende Strassen bleiben. 0 = aus.
    min_road_track_m: float = 9.0
    # Abstand paralleler Gleise (Mittellinie zu Mittellinie, in m). Die Gleisvorlage ist 4 m breit: Bei
    # mehr als etwa 4,3 m bleibt zwischen den Gleisbetten unbefestigter Boden, auf dem Gras waechst (im
    # Spiel am rechten Rheinufer, wo das Doppelgleis 4,6 m Abstand hat; das Dreifachgleis mit 4,1 m hatte
    # durchgehend Schotter). Folgegleise, die parallel zwischen track_spacing_min_m und
    # track_spacing_max_m neben einem Hauptgleis liegen, werden auf diesen Abstand gerueckt (hoechstens 1,5 m,
    # sanft auslaufend). Weichenbereiche (Abstand darunter) bleiben. 0 = aus.
    track_spacing_m: float = 4.1
    track_spacing_min_m: float = 3.4
    track_spacing_max_m: float = 5.6
    # Haengen Gleiswege an gemeinsamen Knoten zusammen, bekommen sie dieselbe Gleisvorlage (die der
    # laengsten Wege). Im Log des Spiels scheiterten Weichen und Anschluesse dort, wo Hauptgleis
    # (standard) und Nebengleis (simple) zusammentreffen: 4 von 14 beteiligten Wegen, an Knoten mit
    # gleicher Vorlage nur 1 von 60. Hochgeschwindigkeitsgleise bleiben unveraendert. False = aus.
    unify_track_templates: bool = True
    max_road_shift_m: float = 5.0
    bridge_types: tuple = DEFAULT_BRIDGE_TYPES
    # Rand der Karte: Punkte ausserhalb (minus Rand) werden abgeschnitten.
    edge_margin_m: float = 50.0
    # Ausschnitt: nur Wege in diesem Quadrat (Mitte in Metern ab Kartenmitte, Kantenlaenge in m).
    # clip_size_m = 0: ganze Karte.
    clip_center_m: tuple = (0.0, 0.0)
    clip_size_m: float = 0.0
    # Einmuendungen zusammenlegen: Knoten (Kreuzungen und Wegenden) derselben Art, die naeher als
    # dieser Abstand beieinander liegen, werden ein Knoten; Kurzstuecke dazwischen entfallen.
    # Grund: Im Spiel scheiterten Wege vor allem dort, wo zwei Einmuendungen dichter als die
    # (breiten) Spiel-Strassen liegen. Im Modell auf den Daten des Grümpentals brachte 10 m etwa
    # +155 Wege, 14 m etwa +290. Im Spiel NICHT getestet. 0 = aus.
    merge_junctions_m: float = 10.0
    # Aufraeumen (network_cleanup.py), beides im Spiel NICHT getestet, darum standardmaessig aus:
    # Richtungsfahrbahnen (zwei parallele Einbahn-Wege) zu einem zweispurigen Weg zusammenfassen.
    # Gilt nur fuer Kategorien mit Einbahn-Vorlage; Autobahnen haben keine zweispurige Vorlage
    # und bleiben unveraendert.
    merge_dual_carriageways: bool = False
    # Doppelt gezeichnete Gleise (Haupt- und Servicegleis auf derselben Trasse) entfernen.
    dedupe_tracks: bool = False


@dataclass
class NetWay:
    art: int
    template: str
    kind: int
    bridge_or_tunnel: str | None
    max_grade: float | None
    nodes: list[int]
    osm_id: int = 0
    rank: int = 99


@dataclass
class Network:
    nodes: list[tuple[float, float]] = field(default_factory=list)
    ways: list[NetWay] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Einordnen eines OSM-Weges
# ---------------------------------------------------------------------------

def _oneway_direction(tags: dict) -> int:
    """+1: Fahrtrichtung = Zeichenrichtung, -1: umgekehrt, 0: keine Einbahnstrasse."""

    value = tags.get("oneway")

    if value in ("yes", "true", "1"):
        return 1

    if value in ("-1", "reverse"):
        return -1

    if value == "no":
        return 0

    if tags.get("junction") in ("roundabout", "circular"):
        return 1

    if tags.get("highway") in ("motorway", "motorway_link"):
        return 1

    return 0


def _classify(tags: dict, opt: NetworkOptions):
    """
    Liefert (art, vorlage, art_von_weg, max_steigung, kategorie, richtung) oder None.
    art_von_weg ist KIND_NORMAL/KIND_BRIDGE/KIND_TUNNEL.
    richtung ist +1/-1 bei Einbahn-Vorlage (-1: Knotenreihenfolge umdrehen), sonst 0.
    """

    if tags.get("area") == "yes":
        return None

    highway = tags.get("highway")
    railway = tags.get("railway")
    direction = 0

    if highway and opt.include_streets:

        if highway not in opt.highways or highway not in HIGHWAY_TEMPLATES:
            return None

        if highway == "service" and tags.get("service") in SKIP_SERVICE:
            return None

        art = ART_STREET
        template = HIGHWAY_TEMPLATES[highway]
        grade = HIGHWAY_GRADE.get(highway)
        category = f"highway={highway}"

        if opt.oneway_templates and template in ONEWAY_TEMPLATES:
            direction = _oneway_direction(tags)

            if direction != 0:
                template = ONEWAY_TEMPLATES[template]

    elif railway and opt.include_rail and railway in opt.railways:

        art = ART_TRACK

        electrified = tags.get("electrified") in {
            "contact_line", "yes", "rail", "4th_rail", "3rd_rail",
        }

        service_track = (
            "service" in tags
            or tags.get("usage") in {"industrial", "military"}
        )

        fast = tags.get("highspeed") == "yes"

        if fast:
            template = RAIL_FAST_CAT if electrified else RAIL_FAST
        elif service_track:
            template = RAIL_SIMPLE_CAT if electrified else RAIL_SIMPLE
        else:
            template = RAIL_STANDARD_CAT if electrified else RAIL_STANDARD

        grade = LIGHT_RAIL_GRADE if railway == "light_rail" else None
        category = f"railway={railway}"

    elif railway == "tram" and opt.include_tram:

        art = ART_STREET
        template = TRAM_TEMPLATE
        grade = TRAM_GRADE
        category = "railway=tram"

    else:
        return None

    kind = KIND_NORMAL

    bridge = tags.get("bridge")
    tunnel = tags.get("tunnel")

    if tunnel == "yes" and opt.include_tunnels:
        kind = KIND_TUNNEL
    elif bridge not in (None, "", "no") and opt.include_bridges:
        kind = KIND_BRIDGE

    return art, template, kind, grade, category, direction


# ---------------------------------------------------------------------------
# Geometrie
# ---------------------------------------------------------------------------

def _dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _point_segment_distance(p, a, b) -> float:

    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length2 = dx * dx + dy * dy

    if length2 == 0:
        return _dist(p, a)

    t = ((p[0] - ax) * dx + (p[1] - ay) * dy) / length2
    t = max(0.0, min(1.0, t))

    return _dist(p, (ax + t * dx, ay + t * dy))


def _douglas_peucker(points: list, keep: set[int], tolerance: float) -> set[int]:
    """
    Gibt die Indizes zurueck, die bleiben. Indizes in `keep` (Enden,
    Kreuzungen) bleiben immer; dazwischen wird einzeln vereinfacht.
    """

    result = set(keep)
    result.add(0)
    result.add(len(points) - 1)

    ordered = sorted(result)

    for start, end in zip(ordered, ordered[1:]):

        stack = [(start, end)]

        while stack:

            lo, hi = stack.pop()

            if hi - lo < 2:
                continue

            worst, worst_i = -1.0, -1

            for i in range(lo + 1, hi):

                d = _point_segment_distance(points[i], points[lo], points[hi])

                if d > worst:
                    worst, worst_i = d, i

            if worst > tolerance:
                result.add(worst_i)
                stack.append((lo, worst_i))
                stack.append((worst_i, hi))

    return result


def _enforce_min_spacing(points: list, kept: list[int], forced: set[int],
                         min_m: float) -> list[int]:
    """Entfernt Formpunkte (nicht erzwungene), die zu nah an Nachbarn liegen."""

    if min_m <= 0 or len(kept) <= 2:
        return kept

    changed = True

    while changed:

        changed = False
        out = [kept[0]]

        for pos in range(1, len(kept)):

            idx = kept[pos]
            is_last = pos == len(kept) - 1

            if (
                not is_last
                and idx not in forced
                and _dist(points[out[-1]], points[idx]) < min_m
            ):
                changed = True
                continue

            out.append(idx)

        # rueckwaerts: Formpunkt direkt vor einem erzwungenen Punkt
        cleaned = [out[-1]]

        for pos in range(len(out) - 2, -1, -1):

            idx = out[pos]

            if (
                pos != 0
                and idx not in forced
                and _dist(points[idx], points[cleaned[-1]]) < min_m
            ):
                changed = True
                continue

            cleaned.append(idx)

        kept = list(reversed(cleaned))

    return kept


def _length(points: list) -> float:
    return sum(_dist(a, b) for a, b in zip(points, points[1:]))


def _bridge_type(length_m: float, opt: NetworkOptions) -> str:

    for limit, name in opt.bridge_types:
        if length_m <= limit:
            return name

    return opt.bridge_types[-1][1]


# ---------------------------------------------------------------------------
# Netz aufbauen
# ---------------------------------------------------------------------------

def _refine_kept(points: list, kept: list[int], max_edge_m: float, min_segment_m: float) -> list[int]:
    """
    Fuegt zwischen zwei behaltenen Punkten, deren Verbindung laenger als max_edge_m ist, ECHTE
    Punkte der Originallinie ein (gleichmaessig nach Bogenlaenge). So folgt die vereinfachte Linie
    der Kurve; zwei parallele Gleise behalten ihren Abstand.
    """

    if not max_edge_m or max_edge_m <= 0 or len(kept) < 2:
        return kept

    arc = [0.0]

    for a, b in zip(points, points[1:]):
        arc.append(arc[-1] + _dist(a, b))

    out = {kept[0]}

    for a, b in zip(kept, kept[1:]):

        out.add(b)

        if b - a < 2:
            continue

        chord = _dist(points[a], points[b])
        path = arc[b] - arc[a]

        if max(chord, path) <= max_edge_m:
            continue

        parts = int(math.ceil(max(chord, path) / max_edge_m))
        last = a

        for j in range(1, parts):

            target = arc[a] + path * j / parts

            index = min(range(a + 1, b), key=lambda i: abs(arc[i] - target))

            if index <= last:
                continue

            # nicht dichter als der kleinste Punktabstand an den Nachbarn
            if _dist(points[index], points[last]) < min_segment_m:
                continue
            if _dist(points[index], points[b]) < min_segment_m:
                continue

            out.add(index)
            last = index

    return sorted(out)


def _densify(network: "Network", ids: list[int], max_edge_m: float) -> tuple[list[int], int]:
    """Fuegt auf Kanten laenger als max_edge_m gleichmaessig neue Knoten ein (auf der Linie)."""

    out = [ids[0]]
    added = 0

    for a, b in zip(ids, ids[1:]):

        pa = network.nodes[a - 1]
        pb = network.nodes[b - 1]

        length = _dist(pa, pb)

        parts = int(math.ceil(length / max_edge_m)) if length > max_edge_m else 1

        for j in range(1, parts):
            f = j / parts
            network.nodes.append(
                (pa[0] + (pb[0] - pa[0]) * f, pa[1] + (pb[1] - pa[1]) * f)
            )
            out.append(len(network.nodes))
            added += 1

        out.append(b)

    return out, added


def _segments_cross(a, b, c, d) -> bool:
    """Schneiden sich die Strecken a-b und c-d im Inneren (nicht an den Enden)?"""

    den = (a[0] - b[0]) * (c[1] - d[1]) - (a[1] - b[1]) * (c[0] - d[0])

    if abs(den) < 1e-9:
        return False

    t = ((a[0] - c[0]) * (c[1] - d[1]) - (a[1] - c[1]) * (c[0] - d[0])) / den
    u = -((a[0] - b[0]) * (a[1] - c[1]) - (a[1] - b[1]) * (a[0] - c[0])) / den

    return 0.02 <= t <= 0.98 and 0.02 <= u <= 0.98


def drop_bridges_without_crossing(network: "Network", min_free_m: float) -> int:
    """
    Kurze Bruecken (unter min_free_m), die keinen anderen Weg kreuzen, werden normale Kanten.
    Gibt die Zahl der geaenderten Wege zurueck.
    """

    if not min_free_m or min_free_m <= 0:
        return 0

    nodes = network.nodes

    candidates = []

    for way in network.ways:
        if way.kind != KIND_BRIDGE:
            continue
        length = sum(_dist(nodes[a - 1], nodes[b - 1]) for a, b in zip(way.nodes, way.nodes[1:]))
        if length < min_free_m:
            candidates.append(way)

    if not candidates:
        return 0

    changed = 0

    for bridge in candidates:

        own = set(bridge.nodes)
        crossing = False

        xs = [nodes[i - 1][0] for i in bridge.nodes]
        ys = [nodes[i - 1][1] for i in bridge.nodes]
        x0, x1, y0, y1 = min(xs) - 5, max(xs) + 5, min(ys) - 5, max(ys) + 5

        for other in network.ways:

            if other is bridge or own & set(other.nodes):
                continue

            for c, d in zip(other.nodes, other.nodes[1:]):

                pc, pd = nodes[c - 1], nodes[d - 1]

                if max(pc[0], pd[0]) < x0 or min(pc[0], pd[0]) > x1 or max(pc[1], pd[1]) < y0 or min(pc[1], pd[1]) > y1:
                    continue

                for a, b in zip(bridge.nodes, bridge.nodes[1:]):
                    if _segments_cross(nodes[a - 1], nodes[b - 1], pc, pd):
                        crossing = True
                        break

                if crossing:
                    break

            if crossing:
                break

        if not crossing:
            bridge.kind = KIND_NORMAL
            bridge.bridge_or_tunnel = None
            changed += 1

    return changed


def unify_track_templates(network: "Network") -> int:
    """
    Gleiswege, die sich Knoten teilen, bekommen die Vorlage der laengsten Wege der Gruppe
    (standard / simple, mit oder ohne Oberleitung). Gibt die Zahl der geaenderten Wege zurueck.
    """

    candidates = {RAIL_STANDARD, RAIL_STANDARD_CAT, RAIL_SIMPLE, RAIL_SIMPLE_CAT}

    tracks = [w for w in network.ways if w.art == ART_TRACK and w.kind == KIND_NORMAL
              and w.template in candidates]

    if len(tracks) < 2:
        return 0

    parent = list(range(len(tracks)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    owner: dict[int, int] = {}

    for index, way in enumerate(tracks):
        for node_id in way.nodes:
            if node_id in owner:
                a, b = find(owner[node_id]), find(index)
                if a != b:
                    parent[a] = b
            else:
                owner[node_id] = index

    groups: dict[int, list[int]] = {}

    for index in range(len(tracks)):
        groups.setdefault(find(index), []).append(index)

    changed = 0

    for members in groups.values():

        templates = {tracks[i].template for i in members}

        if len(templates) < 2:
            continue

        length_by_template: dict[str, float] = {}

        for i in members:
            way = tracks[i]
            length = sum(
                _dist(network.nodes[a - 1], network.nodes[b - 1])
                for a, b in zip(way.nodes, way.nodes[1:])
            )
            length_by_template[way.template] = length_by_template.get(way.template, 0.0) + length

        # bei Gleichstand das Hauptgleis (standard vor simple, mit Oberleitung vor ohne)
        order = [RAIL_STANDARD_CAT, RAIL_STANDARD, RAIL_SIMPLE_CAT, RAIL_SIMPLE]
        dominant = max(
            length_by_template,
            key=lambda t: (round(length_by_template[t], 3), -order.index(t)),
        )

        for i in members:
            if tracks[i].template != dominant:
                tracks[i].template = dominant
                changed += 1

    return changed


def normalize_track_spacing(network: "Network", target: float, lo: float = 3.4, hi: float = 5.6,
                            max_shift: float = 1.5, par_min: float = 0.94, decay: float = 0.7) -> int:
    """
    Rueckt Gleisknoten, die parallel im Abstand lo..hi neben einem frueheren Gleisweg liegen, auf den Abstand
    `target` (Mittellinie zu Mittellinie). Nur Knoten, die in genau einem Gleisweg liegen; die Verschiebung
    laeuft entlang des Weges sanft aus. Gibt die Zahl der verschobenen Knoten zurueck.
    """

    if not target or target <= 0:
        return 0

    nodes = network.nodes
    tracks = [(index, way) for index, way in enumerate(network.ways)
              if way.art == ART_TRACK and way.kind == KIND_NORMAL]

    if len(tracks) < 2:
        return 0

    usage: dict[int, int] = {}

    for _index, way in tracks:
        for node_id in way.nodes:
            usage[node_id] = usage.get(node_id, 0) + 1

    cell = 32.0
    grid: dict = {}
    segments = []

    for order, (_index, way) in enumerate(tracks):
        for a, b in zip(way.nodes, way.nodes[1:]):
            pa, pb = nodes[a - 1], nodes[b - 1]
            length = _dist(pa, pb)
            if length <= 0:
                continue
            segments.append((pa[0], pa[1], pb[0] - pa[0], pb[1] - pa[1], length, order))
            sid = len(segments) - 1
            for cx in range(int(math.floor((min(pa[0], pb[0]) - hi) / cell)),
                            int(math.floor((max(pa[0], pb[0]) + hi) / cell)) + 1):
                for cy in range(int(math.floor((min(pa[1], pb[1]) - hi) / cell)),
                                int(math.floor((max(pa[1], pb[1]) + hi) / cell)) + 1):
                    grid.setdefault((cx, cy), []).append(sid)

    wanted: dict[int, tuple[float, float, float]] = {}

    for order, (_index, way) in enumerate(tracks):

        ids = way.nodes
        shift = [0.0] * len(ids)
        direction = [None] * len(ids)

        for k, node_id in enumerate(ids):

            if usage.get(node_id) != 1:
                continue

            p = nodes[node_id - 1]
            prev_p = nodes[ids[max(0, k - 1)] - 1]
            next_p = nodes[ids[min(len(ids) - 1, k + 1)] - 1]
            tx, ty = next_p[0] - prev_p[0], next_p[1] - prev_p[1]
            tl = math.hypot(tx, ty)

            if tl <= 0:
                continue

            tx, ty = tx / tl, ty / tl
            best = None

            for sid in grid.get((int(math.floor(p[0] / cell)), int(math.floor(p[1] / cell))), []):
                x, y, dx, dy, length, other = segments[sid]
                if other >= order:
                    continue
                t = ((p[0] - x) * dx + (p[1] - y) * dy) / (length * length)
                t = min(1.0, max(0.0, t))
                fx, fy = x + t * dx, y + t * dy
                d = math.hypot(p[0] - fx, p[1] - fy)
                if d < lo or d > hi:
                    continue
                if abs(tx * dx / length + ty * dy / length) < par_min:
                    continue
                if best is None or d < best[0]:
                    best = (d, fx, fy)

            if best is not None:
                d, fx, fy = best
                direction[k] = ((p[0] - fx) / d, (p[1] - fy) / d)
                shift[k] = max(-max_shift, min(max_shift, target - d))

        for _ in range(3):
            for k in range(len(ids)):
                if usage.get(ids[k]) != 1:
                    continue
                for kk in (k - 1, k + 1):
                    if 0 <= kk < len(ids) and direction[kk] is not None and abs(shift[kk]) * decay > abs(shift[k]):
                        shift[k] = shift[kk] * decay
                        if direction[k] is None:
                            direction[k] = direction[kk]

        for k, node_id in enumerate(ids):
            if direction[k] is not None and abs(shift[k]) > 1e-6:
                old = wanted.get(node_id)
                if old is None or abs(shift[k]) > abs(old[2]):
                    wanted[node_id] = (direction[k][0], direction[k][1], shift[k])

    for node_id, (ex, ey, amount) in wanted.items():
        x, y = nodes[node_id - 1]
        nodes[node_id - 1] = (x + ex * amount, y + ey * amount)

    return len(wanted)


def separate_roads_from_tracks(network: "Network", min_distance: float, max_shift: float = 5.0,
                               par_min: float = 0.9, decay: float = 0.7) -> int:
    """
    Rueckt Strassenknoten, die parallel dichter als min_distance neben einem Gleis liegen, vom
    Gleis weg (hoechstens max_shift). Die Verschiebung laeuft entlang der Strasse sanft aus.
    Knoten, die Strasse und Gleis teilen (Bahnuebergaenge), bleiben. Gibt die Zahl der
    verschobenen Knoten zurueck.
    """

    if not min_distance or min_distance <= 0:
        return 0

    nodes = network.nodes
    segments = []
    track_nodes = set()

    for way in network.ways:
        if way.art != ART_TRACK:
            continue
        track_nodes.update(way.nodes)
        if way.kind != KIND_NORMAL:
            continue
        for a, b in zip(way.nodes, way.nodes[1:]):
            pa, pb = nodes[a - 1], nodes[b - 1]
            length = _dist(pa, pb)
            if length > 0:
                segments.append((pa[0], pa[1], pb[0] - pa[0], pb[1] - pa[1], length))

    if not segments:
        return 0

    cell = 32.0
    grid: dict = {}

    for index, (x, y, dx, dy, length) in enumerate(segments):
        x1, y1 = x + dx, y + dy
        for cx in range(int(math.floor((min(x, x1) - min_distance) / cell)),
                        int(math.floor((max(x, x1) + min_distance) / cell)) + 1):
            for cy in range(int(math.floor((min(y, y1) - min_distance) / cell)),
                            int(math.floor((max(y, y1) + min_distance) / cell)) + 1):
                grid.setdefault((cx, cy), []).append(index)

    # Verschiebung je Knoten: (ex, ey, Betrag); bei mehreren Strassen am selben Knoten gilt das Maximum
    wanted: dict[int, tuple[float, float, float]] = {}

    for way in network.ways:

        if way.art != ART_STREET or way.kind != KIND_NORMAL:
            continue

        ids = way.nodes
        need = [0.0] * len(ids)
        away = [None] * len(ids)

        for k, node_id in enumerate(ids):

            if node_id in track_nodes:
                continue

            p = nodes[node_id - 1]
            prev_p = nodes[ids[max(0, k - 1)] - 1]
            next_p = nodes[ids[min(len(ids) - 1, k + 1)] - 1]
            tx, ty = next_p[0] - prev_p[0], next_p[1] - prev_p[1]
            tl = math.hypot(tx, ty)

            if tl <= 0:
                continue

            tx, ty = tx / tl, ty / tl
            best = None

            for index in grid.get((int(math.floor(p[0] / cell)), int(math.floor(p[1] / cell))), []):
                x, y, dx, dy, length = segments[index]
                t = ((p[0] - x) * dx + (p[1] - y) * dy) / (length * length)
                t = min(1.0, max(0.0, t))
                fx, fy = x + t * dx, y + t * dy
                d = math.hypot(p[0] - fx, p[1] - fy)
                if d >= min_distance:
                    continue
                if abs(tx * dx / length + ty * dy / length) < par_min:
                    continue
                if best is None or d < best[0]:
                    best = (d, fx, fy)

            if best is not None:
                d, fx, fy = best
                if d < 1e-6:
                    ex, ey = -ty, tx
                else:
                    ex, ey = (p[0] - fx) / d, (p[1] - fy) / d
                need[k] = min(max_shift, min_distance - d)
                away[k] = (ex, ey)

        # sanft auslaufen lassen (Nachbarn bekommen mindestens decay x Nachbarwert)
        for _ in range(3):
            for k in range(len(ids)):
                if ids[k] in track_nodes:
                    continue
                for kk in (k - 1, k + 1):
                    if 0 <= kk < len(ids) and need[kk] * decay > need[k]:
                        need[k] = need[kk] * decay
                        if away[k] is None:
                            away[k] = away[kk]

        for k, node_id in enumerate(ids):
            if need[k] > 1e-6 and away[k] is not None:
                old = wanted.get(node_id)
                if old is None or need[k] > old[2]:
                    wanted[node_id] = (away[k][0], away[k][1], need[k])

    for node_id, (ex, ey, amount) in wanted.items():
        x, y = nodes[node_id - 1]
        nodes[node_id - 1] = (x + ex * amount, y + ey * amount)

    return len(wanted)


def _two_way_template_for(category: str):
    """Zweispurige Vorlage fuer network_cleanup, None wenn es keine Einbahn-Variante gibt."""

    if not category.startswith("highway="):
        return None

    template = HIGHWAY_TEMPLATES.get(category.split("=", 1)[1])

    return template if template in ONEWAY_TEMPLATES else None


def collect_network(osm, selection, options: NetworkOptions | None = None) -> Network:
    """
    Sammelt Strassen und Gleise aus den geladenen OSM-Daten (osm.nodes,
    osm.ways) im Auswahlrechteck und rechnet sie in Meter ab der Kartenmitte um.

    Gemeinsame OSM-Knoten werden zu gemeinsamen Netzknoten (= Kreuzungen).
    Ausnahme: Strassen und Gleise teilen keine Knoten (Bahnuebergaenge
    entstehen im Spiel von selbst, wenn sich beide kreuzen - ungeprueft).
    """

    opt = options or NetworkOptions()

    center_lat, center_lon = selection.center
    geometry = TPF2Geometry(center_lat, center_lon, selection.rotation_deg)

    half_w = selection.width_m / 2 - opt.edge_margin_m
    half_h = selection.height_m / 2 - opt.edge_margin_m

    clip_on = opt.clip_size_m and opt.clip_size_m > 0
    clip_cx, clip_cy = opt.clip_center_m
    clip_half = (opt.clip_size_m or 0.0) / 2

    stats = {
        "ways_osm": len(osm.ways),
        "ways_used": 0,
        "ways_skipped_tags": 0,
        "ways_dropped_outside": 0,
        "nodes_before": 0,
        "nodes_after": 0,
        "bridges": 0,
        "bridges_short": 0,
        "oneway": 0,
        "tunnels": 0,
        "by_category": {},
    }

    # 1. Einordnen und an der Kartengrenze in zusammenhaengende Stuecke teilen
    runs = []  # (art, template, kind, grade, category, [(osm_id, x, y), ...], way_id)

    for way in osm.ways.values():

        info = _classify(way.tags, opt)

        if info is None:
            stats["ways_skipped_tags"] += 1
            continue

        art, template, kind, grade, category, direction = info

        current = []
        pieces = []

        for node_id in way.nodes:

            node = osm.nodes.get(node_id)

            if node is None:
                if len(current) >= 2:
                    pieces.append(current)
                current = []
                continue

            x, y = geometry.convert(node.lat, node.lon)

            inside = abs(x) <= half_w and abs(y) <= half_h

            if inside and clip_on:
                inside = (
                    abs(x - clip_cx) <= clip_half and abs(y - clip_cy) <= clip_half
                )

            if inside:
                current.append((node_id, float(x), float(y)))
            else:
                if len(current) >= 2:
                    pieces.append(current)
                current = []

        if len(current) >= 2:
            pieces.append(current)

        if not pieces:
            stats["ways_dropped_outside"] += 1
            continue

        if direction == -1:
            pieces = [list(reversed(piece)) for piece in pieces]

        for piece in pieces:
            runs.append((art, template, kind, grade, category, piece, way.id))

    # 1b. Aufraeumen (optional): Richtungsfahrbahnen und Doppelgleise zusammenfassen
    if opt.dedupe_tracks:
        runs, cleanup_stats = network_cleanup.dedupe_tracks(
            runs,
            is_service_template=lambda t: t in (RAIL_SIMPLE, RAIL_SIMPLE_CAT),
        )
        stats.update(cleanup_stats)

    if opt.merge_dual_carriageways:
        runs, cleanup_stats = network_cleanup.merge_dual_carriageways(
            runs,
            _two_way_template_for,
            frozenset(ONEWAY_TEMPLATES.values()),
        )
        stats.update(cleanup_stats)

    # 2. Kreuzungen erkennen: Knoten, der in mehr als einem Stueck vorkommt
    usage: dict[tuple[int, int], int] = {}

    for art, _t, _k, _g, _c, piece, _w in runs:
        for node_id, _x, _y in piece:
            key = (node_id, art)
            usage[key] = usage.get(key, 0) + 1

    # 3. Vereinfachen und die kompakten Knoten-IDs vergeben
    compact: dict[tuple[int, int], int] = {}
    network = Network(stats=stats)

    def node_id_for(osm_id, art, x, y) -> int:

        key = (osm_id, art)
        found = compact.get(key)

        if found is None:
            network.nodes.append((x, y))
            found = len(network.nodes)
            compact[key] = found

        return found

    seen_pairs: set[tuple[int, int, int]] = set()

    for art, template, kind, grade, category, piece, way_id in runs:

        stats["nodes_before"] += len(piece)

        points = [(x, y) for _i, x, y in piece]

        forced = {
            i for i, (osm_id, _x, _y) in enumerate(piece)
            if usage[(osm_id, art)] > 1
        }
        forced.add(0)
        forced.add(len(piece) - 1)

        kept = sorted(
            _douglas_peucker(points, forced, opt.simplify_tolerance_m)
        )
        kept = _enforce_min_spacing(points, kept, forced, opt.min_segment_m)

        if opt.max_edge_follows_osm and kind == KIND_NORMAL:
            kept = _refine_kept(points, kept, opt.max_edge_m, opt.min_segment_m)

        ids = []

        for index in kept:

            osm_id, x, y = piece[index]
            nid = node_id_for(osm_id, art, x, y)

            if ids and ids[-1] == nid:
                continue

            ids.append(nid)

        if len(ids) < 2:
            continue

        # geschlossener Weg aus nur zwei verschiedenen Knoten -> doppelte Kante
        if ids[0] == ids[-1] and len(set(ids)) < 3:
            continue

        # Kanten, die schon von einem anderen Weg gebaut werden, nicht doppelt
        fresh = []

        for a, b in zip(ids, ids[1:]):
            pair = (art, min(a, b), max(a, b))
            fresh.append(pair not in seen_pairs)

        if not any(fresh):
            continue

        for a, b in zip(ids, ids[1:]):
            seen_pairs.add((art, min(a, b), max(a, b)))

        crossing_type = None

        if kind == KIND_BRIDGE:
            bridge_length = _length(points)

            if bridge_length < opt.min_bridge_m:
                kind = KIND_NORMAL
                stats["bridges_short"] += 1
            else:
                crossing_type = _bridge_type(bridge_length, opt)
                stats["bridges"] += 1
        elif kind == KIND_TUNNEL:
            crossing_type = STREET_TUNNEL if art == ART_STREET else RAIL_TUNNEL
            stats["tunnels"] += 1

        if kind == KIND_NORMAL and opt.max_edge_m and opt.max_edge_m > 0:
            ids, added = _densify(network, ids, opt.max_edge_m)
            stats["nodes_added"] = stats.get("nodes_added", 0) + added

        network.ways.append(
            NetWay(
                art=art,
                template=template,
                kind=kind,
                bridge_or_tunnel=crossing_type,
                max_grade=grade,
                nodes=ids,
                osm_id=int(way_id),
                rank=BUILD_RANK.get(category, 99),
            )
        )

        if template in ONEWAY_TEMPLATES.values():
            stats["oneway"] += 1

        stats["ways_used"] += 1
        stats["nodes_after"] += len(ids)
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

    # Bahn zuerst, dann Strassen nach Wichtigkeit; innerhalb gleicher Klasse
    # laengere Wege zuerst, bei Gleichstand stabil in OSM-Reihenfolge.
    if opt.merge_junctions_m and opt.merge_junctions_m > 0:
        merge_junctions(network, opt.merge_junctions_m)

    dropped = drop_bridges_without_crossing(network, opt.min_bridge_free_m)

    if dropped:
        stats["bridges_no_crossing"] = dropped
        stats["bridges"] = max(0, stats.get("bridges", 0) - dropped)
        stats["bridges_short"] = stats.get("bridges_short", 0) + dropped

    spaced = normalize_track_spacing(
        network, opt.track_spacing_m, opt.track_spacing_min_m, opt.track_spacing_max_m,
    )

    if spaced:
        stats["tracks_spaced"] = spaced

    if opt.unify_track_templates:
        unified = unify_track_templates(network)
        if unified:
            stats["tracks_unified"] = unified

    moved = separate_roads_from_tracks(network, opt.min_road_track_m, opt.max_road_shift_m)

    if moved:
        stats["roads_moved"] = moved

    # Bruecken zuerst innerhalb ihrer Kategorie: Eine Bruecke ist gerade. Wird sie NACH den Strassen davor und
    # danach gebaut, uebernimmt sie deren Kantenrichtung (glatter Anschluss) und die Fahrbahn schwingt in der
    # Kurve seitlich aus, das Deck sitzt dann nicht mittig auf der Strasse. Zuerst gebaut ist sie gerade,
    # und die Strassen schliessen glatt an sie an.
    network.ways.sort(key=lambda w: (w.rank, 0 if w.kind == KIND_BRIDGE else 1, -len(w.nodes)))

    return network



# ---------------------------------------------------------------------------
# Einmuendungen zusammenlegen
# ---------------------------------------------------------------------------

def merge_junctions(network: Network, distance: float) -> None:
    """
    Legt Knoten zusammen, die naeher als `distance` beieinander liegen.

    Betroffen sind nur Strassenknoten: Kreuzungsknoten (in mehr als einem Weg) und Wegenden;
    Formpunkte bleiben unveraendert. Gleise werden nicht zusammengelegt (siehe unten).
    Ein Cluster darf hoechstens 2 * distance gross sein. Der neue Knoten liegt im Schwerpunkt.
    Wege, die dadurch weniger als zwei verschiedene Knoten haben, entfallen; Kanten, die danach
    doppelt vorhanden waeren, werden nicht ein zweites Mal gebaut.

    Gedacht fuer das Bauen im Spiel: Dort scheiterten Wege vor allem, wo zwei Einmuendungen
    naeher beieinander lagen als die Strassen breit sind.
    """

    nodes = network.nodes
    ways = network.ways

    users: dict[int, set[int]] = {}
    ends: set[int] = set()

    for wi, way in enumerate(ways):

        for nid in way.nodes:
            users.setdefault(nid, set()).add(wi)

        ends.add(way.nodes[0])
        ends.add(way.nodes[-1])

    def group(nid: int) -> int:
        return ways[next(iter(users[nid]))].art

    # Gleise werden nicht zusammengelegt: Die beiden Gleise einer zweigleisigen Strecke liegen nur
    # 4 bis 5 m auseinander, ihre Enden wuerden zu EINEM Knoten (Beobachtung im Spiel: Wegpaare mit
    # identischen Endpunkten scheitern, Test: zwei parallele Gleise wurden zu einem Weg).
    candidates = [
        n for n in users
        if (len(users[n]) >= 2 or n in ends) and group(n) == ART_STREET
    ]

    cell = float(distance)
    grid: dict[tuple, list[int]] = {}

    for nid in candidates:
        x, y = nodes[nid - 1]
        grid.setdefault((int(x // cell), int(y // cell), group(nid)), []).append(nid)

    close_pairs = []

    for nid in candidates:

        x, y = nodes[nid - 1]
        cx, cy, g = int(x // cell), int(y // cell), group(nid)

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for other in grid.get((cx + dx, cy + dy, g), ()):
                    if other > nid:
                        ox, oy = nodes[other - 1]
                        d = math.hypot(x - ox, y - oy)
                        if d < distance:
                            close_pairs.append((d, nid, other))

    close_pairs.sort()

    parent = {n: n for n in candidates}
    members = {n: [n] for n in candidates}
    max_diameter = 2.0 * distance

    def find(n: int) -> int:
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n

    for _d, a, b in close_pairs:

        ra, rb = find(a), find(b)

        if ra == rb:
            continue

        fits = all(
            math.hypot(
                nodes[p - 1][0] - nodes[q - 1][0],
                nodes[p - 1][1] - nodes[q - 1][1],
            )
            <= max_diameter
            for p in members[ra]
            for q in members[rb]
        )

        if fits:
            parent[rb] = ra
            members[ra] += members[rb]
            del members[rb]

    replacement: dict[int, int] = {}
    merged_clusters = 0

    for group_members in members.values():

        if len(group_members) < 2:
            continue

        merged_clusters += 1
        keep = min(group_members)
        mx = sum(nodes[m - 1][0] for m in group_members) / len(group_members)
        my = sum(nodes[m - 1][1] for m in group_members) / len(group_members)
        nodes[keep - 1] = (mx, my)

        for m in group_members:
            replacement[m] = keep

    network.stats["junctions_merged"] = merged_clusters

    if not replacement:
        return

    seen_edges: set[tuple[int, int, int]] = set()
    kept_ways = []
    dropped = 0

    for way in ways:

        new_nodes: list[int] = []

        for nid in way.nodes:
            nid = replacement.get(nid, nid)

            if not new_nodes or new_nodes[-1] != nid:
                new_nodes.append(nid)

        if len(new_nodes) < 2:
            dropped += 1
            continue

        edges = [
            (way.art, min(a, b), max(a, b))
            for a, b in zip(new_nodes, new_nodes[1:])
        ]

        if all(e in seen_edges for e in edges):
            dropped += 1
            continue

        seen_edges.update(edges)
        way.nodes = new_nodes
        kept_ways.append(way)

    network.ways = kept_ways
    network.stats["ways_dropped_merge"] = dropped
    network.stats["ways_used"] = len(kept_ways)

    # Knotenliste verdichten: nur noch benutzte Knoten, Nummern neu vergeben
    used = sorted({n for way in kept_ways for n in way.nodes})
    renumber = {old: new for new, old in enumerate(used, 1)}
    network.nodes = [nodes[old - 1] for old in used]

    for way in kept_ways:
        way.nodes = [renumber[n] for n in way.nodes]

# ---------------------------------------------------------------------------
# Lua-Datei (Format 2)
# ---------------------------------------------------------------------------

def _lua_string(text: str) -> str:

    escaped = (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", " ")
        .replace("\n", " ")
    )

    return f'"{escaped}"'


def network_to_lua(network: Network, name: str = "Map Studio") -> str:
    """
    Baut den Inhalt von osmdata.lua (Format 3).

    Text statt Lua-Tabellen, weil Lua nur eine begrenzte Zahl Konstanten je
    Funktion erlaubt - ein grosses Netz sprengt das als Tabelle.
    """

    templates: list[str] = []
    types: list[str] = []

    def index_of(table: list[str], value: str) -> int:

        if value not in table:
            table.append(value)

        return table.index(value) + 1

    way_lines = []

    for way in network.ways:

        t_idx = index_of(templates, way.template)
        type_idx = (
            index_of(types, way.bridge_or_tunnel)
            if way.bridge_or_tunnel else 0
        )
        grade = "-" if way.max_grade is None else f"{way.max_grade:g}"

        way_lines.append(
            f"{way.art} {t_idx} {way.kind} {type_idx} {grade} {way.osm_id} "
            + " ".join(str(n) for n in way.nodes)
        )

    node_lines = [f"{x:.1f} {y:.1f}" for x, y in network.nodes]

    lines = [
        "-- Erzeugt vom TPF3 Map Studio. Format 3. Nicht von Hand aendern.",
        "return {",
        "\tformat = 3,",
        f"\tname = {_lua_string(name)},",
        "\ttemplates = {",
    ]

    lines += [f"\t\t{_lua_string(t)}," for t in templates]
    lines += ["\t},", "\ttypes = {"]
    lines += [f"\t\t{_lua_string(t)}," for t in types]
    lines += ["\t},", "\tnodes = [==["]
    lines += node_lines
    lines += ["]==],", "\tways = [==["]
    lines += way_lines
    lines += ["]==],", "}", ""]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mod schreiben
# ---------------------------------------------------------------------------

MOD_ID = "map_studio_osm_import_1"

GAME_SCRIPT_LUA = """function data()
\treturn {
\t\tupdateScript = {
\t\t\tfileName = "%(mod)s::/mapstudio.script@update",
\t\t},
\t\thandleEventScript = {
\t\t\tfileName = "%(mod)s::/mapstudio.script@handleEvent",
\t\t},
\t}
end
"""


def _mod_json(mod_id: str) -> str:

    return json.dumps(
        {
            "dependencies": None,
            "incompatibilities": None,
            "modId": mod_id,
            "options": None,
            "params": None,
            "preRunScript": {"fileName": ""},
            "postRunScript": {"fileName": ""},
            "revision": 1,
            "runScript": {"fileName": ""},
            "severityAdd": "None",
            "severityRemove": "None",
        },
        indent=4,
    ) + "\n"


def _content_json() -> str:

    return json.dumps(
        {
            "archives": None,
            "files": ["mapstudio.gs.lua", "mapstudio.script.lua", "osmdata.lua"],
        },
        indent=4,
    ) + "\n"


def _modinfo_json(name: str) -> str:

    return json.dumps(
        {
            "authors": [{"name": "TPF3 Map Studio", "role": "CREATOR"}],
            "description": (
                "Baut Strassen, Gleise, Bruecken und Tunnel aus OSM-Daten, "
                "die das TPF3 Map Studio exportiert hat. Start ueber die "
                "Konsole: api.cmd.sendCommand(api.cmd.makeScriptingSendEventCmd("
                '"", "mapstudio", "import", true)). Gebiet: ' + name
            ),
            "name": "Map Studio Import",
            "summary": "Importiert das OSM-Strassen- und Gleisnetz",
            "tags": ["Script Mod"],
            "url": "",
        },
        indent=4,
    ) + "\n"


def _preview_png(path: Path) -> None:
    """Einfaches Vorschaubild (das Spiel zeigt sonst ein Fragezeichen)."""

    try:
        from PIL import Image, ImageDraw
    except Exception:
        return

    image = Image.new("RGB", (1280, 720), (24, 38, 52))
    draw = ImageDraw.Draw(image)

    draw.rectangle((40, 40, 1240, 680), outline=(110, 160, 210), width=6)
    draw.text((90, 300), "Map Studio Import", fill=(235, 240, 245))
    draw.text((90, 340), "OSM -> Strassen und Gleise", fill=(170, 190, 210))

    image.save(path)


def find_tpf3_mods_folder() -> Path | None:
    """Der mods-Ordner liegt neben dem heightmaps-Ordner im Userdata-Ordner."""

    from src.heightmap.tpf3_paths import find_tpf3_heightmaps_folder

    heightmaps = find_tpf3_heightmaps_folder()

    if heightmaps is None:
        return None

    return heightmaps.parent / "mods"


def write_mod(
    mods_dir: str | Path,
    network: Network,
    name: str = "Map Studio",
    mod_id: str = MOD_ID,
) -> Path:
    """
    Schreibt den Mod-Ordner <mods_dir>/<mod_id>. Ein vorhandener Ordner wird
    ueberschrieben (nur die eigenen Dateien, nichts wird geloescht).
    """

    from src.heightmap.network_mod_script import IMPORT_SCRIPT_TEMPLATE

    root = Path(mods_dir) / mod_id
    (root / "content").mkdir(parents=True, exist_ok=True)
    (root / "_metadata").mkdir(parents=True, exist_ok=True)

    def write(path: Path, text: str):
        # UTF-8 ohne BOM, Zeilenende immer "\n"
        path.write_bytes(text.encode("utf-8"))

    write(root / "mod.json", _mod_json(mod_id))
    write(root / "_content.json", _content_json())
    write(root / "_metadata" / "modinfo.json", _modinfo_json(name))
    write(root / "content" / "mapstudio.gs.lua", GAME_SCRIPT_LUA % {"mod": mod_id})
    write(
        root / "content" / "mapstudio.script.lua",
        IMPORT_SCRIPT_TEMPLATE.replace("__MOD_ID__", mod_id),
    )
    write(root / "content" / "osmdata.lua", network_to_lua(network, name))

    _preview_png(root / "_metadata" / "0.png")

    return root


def summary_text(network: Network) -> str:
    """Kurze Zusammenfassung fuer den Dialog."""

    s = network.stats

    lines = [
        f"Wege: {s.get('ways_used', 0)} von {s.get('ways_osm', 0)} OSM-Wegen",
        f"Knoten: {len(network.nodes)} "
        f"(vor der Vereinfachung {s.get('nodes_before', 0)} Punkte)",
        f"Bruecken: {s.get('bridges', 0)}, Tunnel: {s.get('tunnels', 0)}",
    ]

    if s.get("junctions_merged", 0):
        lines.append(
            f"  {s['junctions_merged']} Einmuendungen zusammengelegt, "
            f"{s.get('ways_dropped_merge', 0)} Kurzstuecke entfallen"
        )

    if s.get("tracks_spaced", 0):
        lines.append(
            f"  {s['tracks_spaced']} Gleisknoten auf gleichmäßigen Gleisabstand gerückt"
        )

    if s.get("tracks_unified", 0):
        lines.append(
            f"  {s['tracks_unified']} Gleiswege auf die Vorlage ihres Gleisnetzes angeglichen"
        )

    if s.get("roads_moved", 0):
        lines.append(
            f"  {s['roads_moved']} Straßenknoten vom Gleis weggerückt (Mindestabstand)"
        )

    if s.get("nodes_added", 0):
        lines.append(
            f"  {s['nodes_added']} Knoten auf langen Kanten eingefügt"
        )

    if s.get("merged_pairs", 0):
        lines.append(
            f"  {s['merged_pairs']} Richtungsfahrbahnen zusammengefasst"
        )

    if s.get("tracks_removed", 0):
        lines.append(f"  {s['tracks_removed']} Doppelgleise entfernt")

    if s.get("oneway", 0):
        lines.append(
            f"  {s['oneway']} Einbahnstrassen mit schmaler Einbahn-Vorlage"
        )

    if s.get("bridges_short", 0):
        lines.append(
            f"  {s['bridges_short']} sehr kurze Bruecken werden als "
            "gewoehnliche Kante gebaut"
        )

    for category, count in sorted(
        s.get("by_category", {}).items(), key=lambda kv: -kv[1]
    ):
        lines.append(f"  {category}: {count}")

    return "\n".join(lines)
