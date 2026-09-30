"""
Terrain-Anpassung ans Wasserniveau.

TPF2/TPF3 kennen kein Gefälle beim Wasser (Flüsse/Seen sind immer eine
flache Ebene) - bei echten Höhendaten führt das dazu, dass Flüsse und
Seen "trockenfallen", sobald das reale Gelände an einer Stelle über
dem gewählten Wasserniveau liegt. Bisher musste man das von Hand
nachbessern (Canyons graben oder Wasser manuell aufmalen).

Diese Funktion senkt das Gelände automatisch sanft auf Wasserniveau ab:
- Innerhalb einer Wasserfläche/eines Wasserwegs: feste Zieltiefe
- In einem Übergangsbereich darum herum: weiche Überblendung
- Weiter weg: Original-Gelände bleibt unangetastet

Das verfälscht die reale Geländehöhe in einem schmalen Streifen um
jedes Gewässer - bewusster Kompromiss zwischen "geografisch exakt" und
"ohne Nacharbeit im Spiel nutzbar" (Idee stammt von einem
Community-Mitglied).
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, label

from src.osm.objects.osm_data import OSMData
from src.osm.osm_filter import OSMFilter
from src.tpf2.tpf2_geometry import TPF2Geometry


def _latlon_to_pixel(
    geometry: TPF2Geometry,
    lat: float,
    lon: float,
    width_m: float,
    height_m: float,
    w_px: int,
    h_px: int,
) -> tuple[float, float] | None:
    """
    Wandelt einen OSM-Punkt in eine Pixelkoordinate im Hoehenraster um -
    exakt dieselbe Gitterdefinition wie in heightmap_exporter._sample_grid,
    damit Wassermaske und Hoehenraster pixelgenau zueinander passen.
    """

    x, y = geometry.convert(lat, lon)

    col = (x + width_m / 2) / (width_m / w_px) - 0.5
    row = (height_m / 2 - y) / (height_m / h_px) - 0.5

    return (col, row)


def filter_small_water_bodies(
    water_mask: np.ndarray,
    min_area_px: float,
) -> np.ndarray:
    """
    Entfernt zusammenhängende Wasserflächen unter min_area_px Pixeln aus
    der Maske. Sehr kleine, isolierte Gewässer (1-2 Pixel - z.B.
    einzelne Toteislöcher/Tümpel in einem Filz/Moor) erzeugen bei der
    Terrain-Anpassung eher kraterartige Vertiefungen als saubere kleine
    Teiche, weil der Übergangsbereich meist größer ist als die Fläche
    selbst. Diese Flächen bleiben stattdessen unverändertes
    Original-Gelände - nur groß genuge, zusammenhängende Gewässer
    werden angepasst.

    Liefert eine NEUE Maske, verändert water_mask nicht.
    """

    labeled, num_features = label(water_mask)

    if num_features == 0:
        return water_mask.copy()

    sizes = np.bincount(labeled.ravel())

    # sizes[0] ist der Hintergrund (Label 0), nie ein Gewaesser.
    keep_mask = sizes >= min_area_px
    keep_mask[0] = False

    return keep_mask[labeled]


def assemble_rings(node_lists: list[list[int]]) -> list[list[int]]:
    """
    Setzt die Teilstuecke (Wege) eines Multipolygons zu Ringen zusammen.

    Grosse Wasserflaechen wie der Rhein bestehen in OSM aus vielen
    einzelnen Uferwegen, die zusammen erst einen geschlossenen Ring ergeben.
    Wuerde jeder Weg fuer sich als Polygon gefuellt, entstuenden gerade
    Verbindungslinien quer ueber das Land (Keile und Streifen). Deshalb
    werden die Wege ueber gemeinsame Endpunkte zu Ketten verbunden. Das
    Ergebnis sind geschlossene Ringe (erster == letzter Knoten) oder, wenn
    Teilstuecke fehlen, offene Ketten.
    """

    chains = [list(nodes) for nodes in node_lists if len(nodes) >= 2]

    rings: list[list[int]] = []

    while chains:

        chain = chains.pop()

        while chain[0] != chain[-1]:

            joined = False

            for index, other in enumerate(chains):

                if other[0] == chain[-1]:
                    chain = chain + other[1:]
                elif other[-1] == chain[-1]:
                    chain = chain + other[-2::-1]
                elif other[-1] == chain[0]:
                    chain = other + chain[1:]
                elif other[0] == chain[0]:
                    chain = other[::-1] + chain[1:]
                else:
                    continue

                chains.pop(index)

                joined = True

                break

            if not joined:
                break

        rings.append(chain)

    return rings


def ring_is_usable(points: list[tuple[float, float]]) -> bool:
    """
    Ein geschlossener Ring ist immer brauchbar. Eine offene Kette (es
    fehlen Wege) darf nur gefuellt werden, wenn ihre Anfangs- und Endpunkte
    nahe beieinander liegen - sonst entsteht beim Schliessen eine lange
    gerade Linie quer durchs Gelaende.
    """

    if len(points) < 3:
        return False

    if points[0] == points[-1]:
        return True

    length = sum(
        math.dist(points[i], points[i + 1])
        for i in range(len(points) - 1)
    )

    chord = math.dist(points[0], points[-1])

    return length > 0 and chord < 0.3 * length


def build_water_mask(
    osm: OSMData,
    selection,
    w_px: int,
    h_px: int,
    waterway_width_px: int = 3,
    waterway_types: frozenset[str] | None = None,
) -> np.ndarray:
    """
    Baut eine binäre Maske (True=Wasser) in derselben Auflösung wie das
    Höhenraster, aus den geladenen OSM-Wasserflächen (inkl. Inseln bei
    Multipolygonen) und Wasserwegen (als Linien mit fester Pixelbreite).

    waterway_types: Beschränkt die Wasserwege auf bestimmte OSM-Werte des
    Tags "waterway" (z.B. {"river", "canal"} - ohne Bäche/Gräben). None =
    alle Wasserwege. Wasserflächen (Seen, Teiche, breite Flüsse als
    Fläche) sind davon nicht betroffen.
    """

    center_lat, center_lon = selection.center
    geometry = TPF2Geometry(center_lat, center_lon, selection.rotation_deg)
    width_m, height_m = selection.width_m, selection.height_m

    mask_img = Image.new("L", (w_px, h_px), 0)
    draw = ImageDraw.Draw(mask_img)

    def way_points(way):
        return node_points(way.nodes)

    def node_points(node_ids):
        points = []
        for node_id in node_ids:
            node = osm.nodes.get(node_id)
            if node is None:
                continue
            points.append(
                _latlon_to_pixel(
                    geometry, node.lat, node.lon, width_m, height_m, w_px, h_px
                )
            )
        return points

    # Eigenständige Wasserflächen (einfache geschlossene Polygone)
    for way in OSMFilter.water_ways(osm):
        points = way_points(way)
        if ring_is_usable(points):
            draw.polygon(points, fill=255)

    # Multipolygone: äußere Ringe füllen, innere Ringe (Inseln) wieder
    # aushöhlen (Reihenfolge: erst alle äußeren, dann alle inneren, so
    # bleibt eine Insel auch dann ausgehöhlt, wenn ein äußerer Ring
    # zufällig danach nochmal darüber gezeichnet würde).
    for relation in OSMFilter.water_relations(osm):

        outer_ways, inner_ways = [], []

        for member in relation.members:
            if member.type != "way":
                continue
            way = osm.ways.get(member.ref)
            if way is None:
                continue
            (inner_ways if member.role == "inner" else outer_ways).append(way)

        for ring in assemble_rings([w.nodes for w in outer_ways]):
            points = node_points(ring)
            if ring_is_usable(points):
                draw.polygon(points, fill=255)

        for ring in assemble_rings([w.nodes for w in inner_ways]):
            points = node_points(ring)
            if ring_is_usable(points):
                draw.polygon(points, fill=0)

    # Wasserwege (Flüsse/Bäche) - als Linie mit fester Breite, da sie in
    # OSM nur als Mittellinie ohne Flächen-Geometrie vorliegen.
    for way in OSMFilter.waterways(osm):

        if (
            waterway_types is not None
            and way.tags.get("waterway") not in waterway_types
        ):
            continue

        points = way_points(way)
        if len(points) >= 2:
            draw.line(points, fill=255, width=waterway_width_px)

    return np.array(mask_img, dtype=bool)


def blend_terrain_to_water(
    heightmap: np.ndarray,
    water_mask: np.ndarray,
    water_level_m: float,
    transition_m: float,
    pixel_size_m: float,
    water_depth_m: float = 1.0,
    min_area_px: float | None = None,
    max_height_above_water_m: float | None = None,
) -> np.ndarray:
    """
    Passt das Terrain sanft an das Wasserniveau an. Liefert eine NEUE
    Kopie - das übergebene heightmap-Array bleibt unverändert.

    - Innerhalb von water_mask: feste Zieltiefe (water_level_m - water_depth_m)
    - Im Übergangsbereich (transition_m Meter um das Wasser herum):
      weiche Überblendung (Smoothstep) zwischen Zieltiefe und Original
    - Weiter weg: Original-Höhe unverändert

    min_area_px: zusammenhängende Wasserflächen kleiner als dieser
    Pixelwert werden von der Anpassung ausgenommen (siehe
    filter_small_water_bodies - verhindert kraterartige Artefakte bei
    winzigen Gewässern). Ohne Angabe wird automatisch die Kreisfläche
    des Übergangsbereichs selbst verwendet - ein Gewässer sollte
    mindestens so groß wie sein eigener Übergangsbereich sein, damit
    ein sauberer "Kern" entsteht statt nur ein Trichter.

    max_height_above_water_m: Nur Wasserpixel, deren ORIGINALE Höhe höchstens
    so viel über water_level_m liegt, werden angepasst. Gewässer, die
    natürlich viel höher liegen (Bäche in den Bergen, Bergseen), bleiben
    unangetastet - sonst würden sie tief ins Gelände geschnitten und zu
    Schluchten. None = keine Begrenzung (altes Verhalten).
    """

    if heightmap.shape != water_mask.shape:
        raise ValueError(
            "heightmap und water_mask müssen dieselbe Form haben "
            f"({heightmap.shape} != {water_mask.shape})"
        )

    transition_px = max(1.0, transition_m / pixel_size_m)

    if min_area_px is None:
        min_area_px = math.pi * transition_px ** 2

    active_mask = water_mask

    if max_height_above_water_m is not None:
        active_mask = water_mask & (
            heightmap <= water_level_m + max_height_above_water_m
        )

    filtered_mask = filter_small_water_bodies(active_mask, min_area_px)

    if not filtered_mask.any():
        # Kein (ausreichend grosses) Wasser im Ausschnitt - nichts zu
        # tun, Original unveraendert.
        return heightmap.copy()

    # Distanz (in Pixeln) jedes Punkts zum naechsten Wasserpixel;
    # innerhalb des Wassers selbst ist die Distanz 0.
    distance_px = distance_transform_edt(~filtered_mask)

    # Smoothstep: 1 direkt am/im Wasser, 0 ab transition_px Entfernung.
    t = np.clip(1.0 - distance_px / transition_px, 0.0, 1.0)
    weight = t * t * (3 - 2 * t)

    target_height = water_level_m - water_depth_m

    blended = heightmap * (1 - weight) + target_height * weight

    return blended.astype(heightmap.dtype)


def enforce_osm_water(
    heightmap: np.ndarray,
    water_mask: np.ndarray,
    water_level_m: float,
    pixel_size_m: float,
    transition_m: float = 60.0,
    bed_depth_m: float = 5.0,
    bank_height_m: float = 2.0,
    max_height_above_water_m: float | None = 15.0,
    min_area_px: float = 50.0,
) -> np.ndarray:
    """
    Wasser nur dort, wo OpenStreetMap Wasser hat.

    Das Spiel kennt nur EINEN Wasserspiegel: alles Gelaende darunter steht
    unter Wasser. Ein Fluss wie der Rhein liegt aber nur wenige Meter unter
    seiner Aue - bei jedem einzelnen Pegel wird dadurch entweder das ganze
    Tal geflutet oder der Fluss faellt trocken. Diese Funktion dreht die
    Logik um:

    - Gelaende ausserhalb der Gewaesser wird mindestens auf
      water_level_m + bank_height_m angehoben: dort kann nie Wasser stehen.
    - Innerhalb der Gewaesser (aus OSM) liegt das Bett auf
      water_level_m - bed_depth_m.
    - Dazwischen glaettet eine Boeschung der Breite transition_m (Smoothstep).

    max_height_above_water_m: Gewaesser, die von Natur aus hoeher als
    Wasserspiegel + Grenze liegen (Baeche und Bergseen), bleiben unangetastet.
    min_area_px: kleinere zusammenhaengende Wasserflaechen werden ignoriert.

    Liefert eine NEUE Kopie, heightmap bleibt unveraendert. Die Wasserlinie
    liegt etwas ausserhalb der OSM-Kante (Boeschung), typisch 0.3 x
    transition_m je Ufer.
    """

    if heightmap.shape != water_mask.shape:
        raise ValueError(
            "heightmap und water_mask müssen dieselbe Form haben "
            f"({heightmap.shape} != {water_mask.shape})"
        )

    heights = heightmap.astype(np.float32)

    active = water_mask

    if max_height_above_water_m is not None:
        active = active & (heights <= water_level_m + max_height_above_water_m)

    if min_area_px:
        active = filter_small_water_bodies(active, min_area_px)

    if not active.any():
        return heightmap.copy()

    land = np.maximum(heights, np.float32(water_level_m + bank_height_m))

    bed = np.float32(water_level_m - bed_depth_m)

    transition_px = max(1.0, transition_m / pixel_size_m)

    distance_px = distance_transform_edt(~active)

    t = np.clip(1.0 - distance_px / transition_px, 0.0, 1.0)
    weight = (t * t * (3 - 2 * t)).astype(np.float32)

    result = land * (1 - weight) + bed * weight

    return result.astype(heightmap.dtype, copy=False)
