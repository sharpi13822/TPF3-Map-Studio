"""
Tests fuer src/heightmap/network_export.py (ohne Oberflaeche, ohne Spiel).

Starten:  python -m unittest tests.test_network_export -v
"""

import json
import math
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.heightmap import network_export as ne
from src.osm.objects.node import Node
from src.osm.objects.way import Way

CENTER_LAT, CENTER_LON = 50.0, 7.6
M_LAT = 111_320.0
M_LON = M_LAT * math.cos(math.radians(CENTER_LAT))


def node(node_id, x, y, tags=None):
    """OSM-Knoten an einer Stelle in Metern ab der Kartenmitte."""
    return Node(
        id=node_id,
        lat=CENTER_LAT + y / M_LAT,
        lon=CENTER_LON + x / M_LON,
        tags=tags or {},
    )


def make_osm(nodes, ways):
    return SimpleNamespace(
        nodes={n.id: n for n in nodes},
        ways={w.id: w for w in ways},
    )


SELECTION = SimpleNamespace(
    center=(CENTER_LAT, CENTER_LON),
    rotation_deg=0.0,
    width_m=10_000.0,
    height_m=10_000.0,
)


def parse_format2(text):
    """Liest osmdata.lua so, wie es das Lua-Skript tut (Gegenprobe)."""

    def block(name):
        start = text.index(f"{name} = [==[") + len(f"{name} = [==[")
        end = text.index("]==]", start)
        return text[start:end].strip("\n").split("\n")

    templates = [
        line.strip().strip(",").strip('"')
        for line in text.split("templates = {")[1].split("},")[0].strip().split("\n")
        if line.strip()
    ]

    nodes = [tuple(float(v) for v in line.split()) for line in block("nodes")]
    ways = []

    for line in block("ways"):
        tok = line.split()
        ways.append({
            "art": int(tok[0]), "v": templates[int(tok[1]) - 1],
            "t": int(tok[2]), "tp": int(tok[3]),
            "g": None if tok[4] == "-" else float(tok[4]),
            "osm": int(tok[5]),
            "n": [int(v) for v in tok[6:]],
        })

    return nodes, ways


class NetworkExportTest(unittest.TestCase):

    def test_collinear_shape_points_are_removed_but_junctions_stay(self):
        # Strasse A: 6 Punkte auf einer Linie, Knoten 3 ist auch Teil von B
        a = [node(i, i * 100, 0) for i in range(1, 7)]
        b_extra = [node(10, 200, 150), node(11, 200, 300)]
        osm = make_osm(
            a + b_extra,
            [
                Way(1, [1, 2, 3, 4, 5, 6], {"highway": "residential"}),
                Way(2, [3, 10, 11], {"highway": "residential"}),
            ],
        )
        opt = ne.NetworkOptions(max_edge_m=0, min_segment_m=0, simplify_tolerance_m=3)
        net = ne.collect_network(osm, SELECTION, opt)

        self.assertEqual(len(net.ways), 2)
        way_a = net.ways[0]
        # Linie ist gerade: nur Enden und die Kreuzung bleiben
        self.assertEqual(len(way_a.nodes), 3)
        way_b = net.ways[1]
        # die Kreuzung ist in beiden Wegen derselbe Netzknoten
        self.assertIn(way_a.nodes[1], way_b.nodes)

    def test_curve_points_are_kept(self):
        pts = [node(1, 0, 0), node(2, 100, 0), node(3, 200, 60), node(4, 300, 60)]
        osm = make_osm(pts, [Way(1, [1, 2, 3, 4], {"highway": "tertiary"})])
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0))
        self.assertEqual(len(net.ways[0].nodes), 4)

    def test_rail_templates_and_separate_nodes_for_street_and_rail(self):
        shared = node(5, 0, 0)
        osm = make_osm(
            [shared, node(6, 300, 0), node(7, 0, 300)],
            [
                Way(1, [5, 6], {"railway": "rail", "electrified": "contact_line"}),
                Way(2, [5, 7], {"highway": "secondary"}),
            ],
        )
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions())
        rail = [w for w in net.ways if w.art == ne.ART_TRACK][0]
        street = [w for w in net.ways if w.art == ne.ART_STREET][0]
        self.assertEqual(rail.template, ne.RAIL_STANDARD_CAT)
        self.assertEqual(street.template, "/country/country_new_small.street_template")
        self.assertNotEqual(rail.nodes[0], street.nodes[0])

    def test_service_track_and_highspeed(self):
        osm = make_osm(
            [node(1, 0, 0), node(2, 400, 0), node(3, 0, 200), node(4, 400, 200)],
            [
                Way(1, [1, 2], {"railway": "rail", "service": "siding"}),
                Way(2, [3, 4], {"railway": "rail", "highspeed": "yes", "electrified": "contact_line"}),
            ],
        )
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions())
        templates = {w.template for w in net.ways}
        self.assertEqual(templates, {ne.RAIL_SIMPLE, ne.RAIL_FAST_CAT})

    def test_bridge_and_tunnel(self):
        osm = make_osm(
            [node(i, i * 60, 0) for i in range(1, 4)]
            + [node(i, (i - 10) * 60, 500) for i in range(11, 14)],
            [
                Way(1, [1, 2, 3], {"highway": "primary", "bridge": "yes"}),
                Way(2, [11, 12, 13], {"railway": "rail", "tunnel": "yes"}),
            ],
        )
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0))
        bridge = [w for w in net.ways if w.kind == ne.KIND_BRIDGE][0]
        tunnel = [w for w in net.ways if w.kind == ne.KIND_TUNNEL][0]
        self.assertEqual(bridge.bridge_or_tunnel, "/trestle.bridge")
        self.assertEqual(tunnel.bridge_or_tunnel, ne.RAIL_TUNNEL)
        self.assertEqual(net.stats["bridges"], 1)
        self.assertEqual(net.stats["tunnels"], 1)

    def test_oneway_ways_use_narrow_template_and_direction(self):
        osm = make_osm(
            [node(1, 0, 0), node(2, 200, 0), node(3, 0, 300), node(4, 200, 300),
             node(5, 0, 600), node(6, 200, 600), node(7, 0, 900), node(8, 200, 900)],
            [
                Way(1, [1, 2], {"highway": "primary", "oneway": "yes"}),
                Way(2, [3, 4], {"highway": "primary", "oneway": "-1"}),
                Way(3, [5, 6], {"highway": "primary"}),
                Way(4, [7, 8], {"highway": "motorway"}),
            ],
        )
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0))
        by_id = {w.osm_id: w for w in net.ways}
        narrow = "/town/town_new_one_way_small.street_template"
        self.assertEqual(by_id[1].template, narrow)
        self.assertEqual(by_id[2].template, narrow)
        # Landstrasse: 2 Fahrspuren (country_new_small)
        self.assertEqual(by_id[3].template, "/country/country_new_small.street_template")
        # Autobahn bleibt unveraendert (keine Einbahn-Vorlage)
        self.assertEqual(by_id[4].template, "/highway/highway_new_large.street_template")
        # oneway=yes: Reihenfolge wie gezeichnet (x aufsteigend), -1: umgedreht
        x_first = lambda w: net.nodes[w.nodes[0] - 1][0]
        self.assertLess(x_first(by_id[1]), 100)
        self.assertGreater(x_first(by_id[2]), 100)
        self.assertEqual(net.stats["oneway"], 2)
        # abschaltbar
        net2 = ne.collect_network(
            osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0, oneway_templates=False)
        )
        self.assertTrue(all("one_way" not in w.template for w in net2.ways))

    def test_roundabout_is_oneway(self):
        osm = make_osm(
            [node(1, 0, 0), node(2, 30, 10), node(3, 60, 0)],
            [Way(1, [1, 2, 3], {"highway": "residential", "junction": "roundabout"})],
        )
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0))
        self.assertIn("one_way_small", net.ways[0].template)

    def test_junctions_close_together_are_merged(self):
        # Zwei Querstrassen (B und C) treffen die Hauptstrasse A 8 m voneinander entfernt.
        osm = make_osm(
            [node(1, 0, 0), node(2, 96, 0), node(3, 104, 0), node(4, 200, 0),
             node(5, 96, 150), node(6, 104, -150)],
            [
                Way(1, [1, 2, 3, 4], {"highway": "primary"}),
                Way(2, [5, 2], {"highway": "secondary"}),
                Way(3, [6, 3], {"highway": "secondary"}),
            ],
        )
        off = ne.collect_network(
            osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0, merge_junctions_m=0)
        )
        on = ne.collect_network(
            osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0, merge_junctions_m=10)
        )
        self.assertEqual(len(off.nodes), 6)
        self.assertEqual(on.stats["junctions_merged"], 1)
        self.assertEqual(len(on.nodes), 5)      # 2 und 3 sind ein Knoten
        # Kurzstueck 2-3 der Hauptstrasse entfaellt nicht als Weg, wird aber Teil derselben Kante
        main = [w for w in on.ways if w.osm_id == 1][0]
        self.assertEqual(len(main.nodes), 3)
        # alle Knotennummern in den Wegen sind gueltig
        for way in on.ways:
            for n in way.nodes:
                self.assertTrue(1 <= n <= len(on.nodes))
        # Die gemeinsame Einmuendung liegt zwischen den beiden alten Knoten
        junction_x = [on.nodes[n - 1][0] for n in main.nodes][1]
        self.assertAlmostEqual(junction_x, 100, delta=1.0)

    def test_merge_does_not_mix_street_and_rail(self):
        osm = make_osm(
            [node(1, 0, 0), node(2, 100, 0), node(3, 0, 5), node(4, 100, 5)],
            [
                Way(1, [1, 2], {"highway": "primary"}),
                Way(2, [3, 4], {"railway": "rail"}),
            ],
        )
        net = ne.collect_network(
            osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0, merge_junctions_m=10)
        )
        self.assertEqual(len(net.ways), 2)
        self.assertEqual(len(net.nodes), 4)

    def test_parallel_tracks_are_not_merged(self):
        """Zwei Gleise 4,5 m nebeneinander muessen zwei Wege mit eigenen Knoten bleiben."""
        osm = make_osm(
            [node(1, 0, 0), node(2, 300, 0), node(3, 0, 4.5), node(4, 300, 4.5)],
            [
                Way(1, [1, 2], {"railway": "rail"}),
                Way(2, [4, 3], {"railway": "rail"}),
            ],
        )
        net = ne.collect_network(
            osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0, merge_junctions_m=14)
        )
        self.assertEqual(len(net.ways), 2)
        self.assertEqual(len(net.nodes), 4)
        self.assertEqual(net.stats.get("junctions_merged", 0), 0)

    def test_clip_limits_the_area(self):
        osm = make_osm(
            [node(1, 0, 0), node(2, 400, 0), node(3, 3000, 0), node(4, 3400, 0)],
            [
                Way(1, [1, 2], {"highway": "primary"}),
                Way(2, [3, 4], {"highway": "primary"}),
            ],
        )
        full = ne.collect_network(osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0))
        clipped = ne.collect_network(
            osm,
            SELECTION,
            ne.NetworkOptions(max_edge_m=0, min_segment_m=0, clip_center_m=(0.0, 0.0), clip_size_m=2000.0),
        )
        moved = ne.collect_network(
            osm,
            SELECTION,
            ne.NetworkOptions(max_edge_m=0, min_segment_m=0, clip_center_m=(3200.0, 0.0), clip_size_m=1000.0),
        )
        self.assertEqual({w.osm_id for w in full.ways}, {1, 2})
        self.assertEqual({w.osm_id for w in clipped.ways}, {1})
        self.assertEqual({w.osm_id for w in moved.ways}, {2})

    def test_short_bridge_becomes_normal_edge(self):
        osm = make_osm(
            [node(1, 0, 0), node(2, 15, 0), node(3, 200, 0), node(4, 240, 0)],
            [
                Way(1, [1, 2], {"railway": "rail", "bridge": "yes"}),
                Way(2, [3, 4], {"railway": "rail", "bridge": "yes"}),
            ],
        )
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0))
        short = [w for w in net.ways if w.osm_id == 1][0]
        longer = [w for w in net.ways if w.osm_id == 2][0]
        self.assertEqual(short.kind, ne.KIND_NORMAL)
        self.assertIsNone(short.bridge_or_tunnel)
        self.assertEqual(longer.kind, ne.KIND_BRIDGE)
        self.assertEqual(net.stats["bridges"], 1)
        self.assertEqual(net.stats["bridges_short"], 1)
        # abschaltbar
        net2 = ne.collect_network(
            osm, SELECTION,
            ne.NetworkOptions(max_edge_m=0, min_segment_m=0, min_bridge_m=0, min_bridge_free_m=0),
        )
        self.assertEqual(net2.stats["bridges"], 2)

    def test_long_bridge_gets_long_span_type(self):
        osm = make_osm(
            [node(1, 0, 0), node(2, 400, 0)],
            [Way(1, [1, 2], {"highway": "primary", "bridge": "yes"})],
        )
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions())
        self.assertEqual(net.ways[0].bridge_or_tunnel, "/steel.bridge")

    def test_way_crossing_the_map_border_is_cut(self):
        # Karte 10 km breit, Rand 50 m -> Punkte ab |x| > 4950 fallen weg
        osm = make_osm(
            [node(1, 4800, 0), node(2, 4900, 0), node(3, 5200, 0), node(4, 5300, 0)],
            [Way(1, [1, 2, 3, 4], {"highway": "primary"})],
        )
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0))
        self.assertEqual(len(net.ways), 1)
        xs = [net.nodes[i - 1][0] for i in net.ways[0].nodes]
        self.assertTrue(all(abs(x) <= 4950 for x in xs))

    def test_unwanted_tags_are_skipped(self):
        osm = make_osm(
            [node(1, 0, 0), node(2, 100, 0), node(3, 0, 100)],
            [
                Way(1, [1, 2], {"highway": "footway"}),
                Way(2, [1, 3], {"highway": "service", "service": "parking_aisle"}),
                Way(3, [2, 3], {"railway": "tram"}),
                Way(4, [1, 2], {"highway": "residential", "area": "yes"}),
            ],
        )
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions())
        self.assertEqual(net.ways, [])

    def test_min_segment_removes_close_shape_points(self):
        pts = [node(1, 0, 0), node(2, 100, 0), node(3, 103, 25), node(4, 108, 0), node(5, 400, 0)]
        osm = make_osm(pts, [Way(1, [1, 2, 3, 4, 5], {"highway": "primary"})])
        # Toleranz klein, damit nur der Mindestabstand entscheidet
        net = ne.collect_network(
            osm, SELECTION, ne.NetworkOptions(simplify_tolerance_m=0.1, min_segment_m=8)
        )
        self.assertEqual(len(net.ways), 1)
        ids = net.ways[0].nodes
        coords = [net.nodes[i - 1] for i in ids]
        for a, b in zip(coords, coords[1:]):
            self.assertGreaterEqual(math.hypot(a[0] - b[0], a[1] - b[1]), 8)

    def test_lua_format_roundtrip(self):
        osm = make_osm(
            [node(1, 0, 0), node(2, 200, 0), node(3, 400, 50), node(4, 200, 300)],
            [
                Way(1, [1, 2, 3], {"highway": "primary"}),
                Way(2, [2, 4], {"highway": "motorway", "bridge": "yes"}),
            ],
        )
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0))
        text = ne.network_to_lua(net, 'Test "Gebiet"')
        nodes, ways = parse_format2(text)
        self.assertEqual(len(nodes), len(net.nodes))
        self.assertEqual(len(ways), len(net.ways))
        self.assertEqual([w["n"] for w in ways], [w.nodes for w in net.ways])
        bridge = [w for w in ways if w["t"] == ne.KIND_BRIDGE][0]
        self.assertEqual(bridge["g"], 0.08)  # Autobahn
        self.assertEqual(bridge["osm"], 2)   # OSM-Wegnummer bleibt erhalten
        self.assertEqual(sorted(w["osm"] for w in ways), [1, 2])
        self.assertIn("format = 3", text)
        self.assertNotIn("]==]]==]", text)

    def test_ways_are_sorted_rail_first_then_by_importance(self):
        osm = make_osm(
            [node(i, i * 100, 0) for i in range(1, 4)]
            + [node(i, (i - 10) * 100, 200) for i in range(11, 14)]
            + [node(i, (i - 20) * 100, 400) for i in range(21, 24)]
            + [node(i, (i - 30) * 100, 600) for i in range(31, 34)],
            [
                Way(1, [1, 2, 3], {"highway": "residential"}),
                Way(2, [11, 12, 13], {"highway": "motorway"}),
                Way(3, [21, 22, 23], {"railway": "rail"}),
                Way(4, [31, 32, 33], {"highway": "primary"}),
            ],
        )
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0))
        order = [w.osm_id for w in net.ways]
        self.assertEqual(order, [3, 2, 4, 1])  # Bahn, Autobahn, Bundesstrasse, Wohnstrasse

    def test_write_mod_creates_all_files(self):
        osm = make_osm(
            [node(1, 0, 0), node(2, 100, 0)],
            [Way(1, [1, 2], {"highway": "residential"})],
        )
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions(max_edge_m=0, min_segment_m=0))
        with tempfile.TemporaryDirectory() as tmp:
            root = ne.write_mod(tmp, net, "Test")
            for rel in [
                "mod.json", "_content.json",
                "content/mapstudio.gs.lua", "content/mapstudio.script.lua",
                "content/osmdata.lua", "_metadata/modinfo.json",
            ]:
                self.assertTrue((root / rel).is_file(), rel)

            mod = json.loads((root / "mod.json").read_text(encoding="utf-8"))
            self.assertEqual(mod["modId"], ne.MOD_ID)
            self.assertEqual(mod["preRunScript"]["fileName"], "")

            content = json.loads((root / "_content.json").read_text(encoding="utf-8"))
            for name in content["files"]:
                self.assertTrue((root / "content" / name).is_file(), name)

            script = (root / "content" / "mapstudio.script.lua").read_text(encoding="utf-8")
            self.assertNotIn("__MOD_ID__", script)
            self.assertIn(ne.MOD_ID + "::/", script)

            gs = (root / "content" / "mapstudio.gs.lua").read_text(encoding="utf-8")
            self.assertIn(f'"{ne.MOD_ID}::/mapstudio.script@update"', gs)

            # keine BOM
            raw = (root / "mod.json").read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))


class CleanupTests(unittest.TestCase):
    """Optionales Aufraeumen (network_cleanup), Standard ist aus."""

    def _dual(self, tags):
        pts = [node(1, 0, 0), node(2, 100, 0), node(3, 200, 0),
               node(4, 200, 12), node(5, 100, 12), node(6, 0, 12)]
        return make_osm(pts, [
            Way(1, [1, 2, 3], dict(tags, oneway="yes")),
            Way(2, [4, 5, 6], dict(tags, oneway="yes")),
        ])

    def test_cleanup_default_off(self):
        net = ne.collect_network(self._dual({"highway": "residential"}), SELECTION)
        self.assertEqual(len(net.ways), 2)
        self.assertNotIn("merged_pairs", net.stats)

    def test_dual_carriageways_merged(self):
        opt = ne.NetworkOptions(merge_dual_carriageways=True)
        net = ne.collect_network(self._dual({"highway": "residential"}), SELECTION, opt)
        self.assertEqual(len(net.ways), 1)
        self.assertEqual(net.stats["merged_pairs"], 1)
        self.assertEqual(net.ways[0].template, "/town/town_new_small.street_template")

    def test_motorway_not_merged(self):
        opt = ne.NetworkOptions(merge_dual_carriageways=True)
        net = ne.collect_network(self._dual({"highway": "motorway"}), SELECTION, opt)
        self.assertEqual(len(net.ways), 2)

    def test_duplicate_tracks_removed(self):
        pts = [node(1, 0, 0), node(2, 100, 0), node(3, 0, 2), node(4, 100, 2)]
        osm = make_osm(pts, [
            Way(1, [1, 2], {"railway": "rail"}),
            Way(2, [3, 4], {"railway": "rail", "service": "siding"}),
        ])
        base = ne.NetworkOptions(merge_junctions_m=0)
        self.assertEqual(len(ne.collect_network(osm, SELECTION, base).ways), 2)
        net = ne.collect_network(
            osm, SELECTION, ne.NetworkOptions(merge_junctions_m=0, dedupe_tracks=True)
        )
        self.assertEqual(len(net.ways), 1)
        self.assertEqual(net.stats["tracks_removed"], 1)



class DensifyTests(unittest.TestCase):
    """Knoten auf langen Kanten (max_edge_m)."""

    def _long_road(self, tags):
        pts = [node(1, 0, 0), node(2, 400, 0)]
        return make_osm(pts, [Way(1, [1, 2], tags)])

    def test_long_edge_gets_evenly_spaced_nodes_on_the_line(self):
        net = ne.collect_network(self._long_road({"highway": "tertiary"}), SELECTION,
                                 ne.NetworkOptions(max_edge_m=80))
        self.assertEqual(len(net.ways), 1)
        ids = net.ways[0].nodes
        self.assertEqual(len(ids), 6)  # 400 m / 80 m = 5 Kanten
        pts = [net.nodes[i - 1] for i in ids]
        ys = [p[1] for p in pts]
        self.assertLess(max(ys) - min(ys), 0.01)  # alle auf einer Linie
        for a, b in zip(pts, pts[1:]):
            self.assertLessEqual(math.hypot(b[0] - a[0], b[1] - a[1]), 80.01)
        self.assertEqual(net.stats["nodes_added"], 4)

    def test_off_when_zero(self):
        net = ne.collect_network(self._long_road({"highway": "tertiary"}), SELECTION,
                                 ne.NetworkOptions(max_edge_m=0))
        self.assertEqual(len(net.ways[0].nodes), 2)
        self.assertNotIn("nodes_added", net.stats)

    def test_default_is_on(self):
        net = ne.collect_network(self._long_road({"highway": "tertiary"}), SELECTION)
        self.assertGreater(len(net.ways[0].nodes), 2)

    def test_tracks_are_densified_too(self):
        net = ne.collect_network(self._long_road({"railway": "rail"}), SELECTION,
                                 ne.NetworkOptions(max_edge_m=100))
        self.assertEqual(len(net.ways[0].nodes), 5)

    def test_bridges_and_tunnels_are_left_alone(self):
        for tags in ({"highway": "tertiary", "bridge": "yes"},
                     {"highway": "tertiary", "tunnel": "yes"}):
            net = ne.collect_network(self._long_road(tags), SELECTION,
                                     ne.NetworkOptions(max_edge_m=80))
            self.assertEqual(len(net.ways[0].nodes), 2, tags)

    def test_shared_junction_nodes_stay_shared(self):
        pts = [node(1, 0, 0), node(2, 400, 0), node(3, 400, 300)]
        osm = make_osm(pts, [Way(1, [1, 2], {"highway": "tertiary"}),
                             Way(2, [2, 3], {"highway": "tertiary"})])
        net = ne.collect_network(osm, SELECTION, ne.NetworkOptions(max_edge_m=100, merge_junctions_m=0))
        first, second = net.ways[0].nodes, net.ways[1].nodes
        self.assertEqual(len(set(first) & set(second)), 1)  # genau der gemeinsame Knoten
        self.assertEqual(first[-1] if len(first) > len(second) else second[0],
                         (first[-1] if first[-1] in second else first[0]))

    def test_short_edges_untouched(self):
        pts = [node(1, 0, 0), node(2, 60, 0)]
        net = ne.collect_network(make_osm(pts, [Way(1, [1, 2], {"highway": "tertiary"})]), SELECTION,
                                 ne.NetworkOptions(max_edge_m=80))
        self.assertEqual(len(net.ways[0].nodes), 2)


class ParallelTrackSpacingTests(unittest.TestCase):
    """Zwei parallele Gleise in einer Kurve: Der Abstand darf nach dem Export nicht schwanken."""

    @staticmethod
    def _arc(radius, step_m, sweep_m, first_id, offset_angle=0.0, center_y=800.0):
        """Kreisbogen um den Mittelpunkt (0, center_y); beide Gleise teilen sich den Mittelpunkt."""
        pts = []
        n = int(sweep_m // step_m) + 1
        for k in range(n):
            ang = offset_angle + k * step_m / radius
            pts.append((first_id + k, radius * math.sin(ang), center_y - radius * math.cos(ang)))
        return pts

    def _spacing(self, follows, step_m=9.7, radius=800.0):
        a = self._arc(radius, step_m, 1500, 1)
        b = self._arc(radius + 4.5, step_m * (radius + 4.5) / radius * 0.93, 1500, 1000, offset_angle=0.0021)
        pts = [node(i, x, y) for i, x, y in a + b]
        ways = [Way(1, [i for i, _x, _y in a], {"railway": "rail"}),
                Way(2, [i for i, _x, _y in b], {"railway": "rail"})]
        opt = ne.NetworkOptions(merge_junctions_m=0, max_edge_m=80, max_edge_follows_osm=follows)
        net = ne.collect_network(make_osm(pts, ways), SELECTION, opt)
        first, second = net.ways[0].nodes, net.ways[1].nodes
        poly = [net.nodes[i - 1] for i in first]
        dists = []
        for i in second[1:-1]:
            p = net.nodes[i - 1]
            # nur die Mitte der Kurve (80 m bis 1360 m): an den Enden zaehlt der Abstand zum Streckenende
            ang = math.atan2(p[0], 800.0 - p[1])
            if not (0.1 < ang < 1.7):
                continue
            best = 1e9
            for u, v in zip(poly[:-1], poly[1:]):
                dx, dy = v[0] - u[0], v[1] - u[1]
                l2 = dx * dx + dy * dy
                t = max(0.0, min(1.0, ((p[0] - u[0]) * dx + (p[1] - u[1]) * dy) / l2)) if l2 else 0.0
                best = min(best, math.hypot(p[0] - u[0] - t * dx, p[1] - u[1] - t * dy))
            dists.append(best)
        edges = [math.hypot(net.nodes[b - 1][0] - net.nodes[a - 1][0], net.nodes[b - 1][1] - net.nodes[a - 1][1])
                 for w in net.ways for a, b in zip(w.nodes, w.nodes[1:])]
        return dists, max(edges)

    def test_following_the_osm_line_keeps_the_spacing_steady(self):
        steady, longest_steady = self._spacing(True)
        chord, _longest = self._spacing(False)
        self.assertLess(max(steady) - min(steady), 1.2)
        self.assertLess(max(steady) - min(steady), (max(chord) - min(chord)) * 0.7)
        self.assertLessEqual(longest_steady, 100.0)         # keine Kante laenger als ~80 m (+ Pixelraster der OSM-Punkte)

    def test_still_few_nodes_on_straight_tracks(self):
        pts = [node(i, i * 10.0, 0.0) for i in range(1, 60)]
        way = Way(1, list(range(1, 60)), {"railway": "rail"})
        net = ne.collect_network(make_osm(pts, [way]), SELECTION, ne.NetworkOptions(merge_junctions_m=0, max_edge_m=80))
        self.assertLessEqual(len(net.ways[0].nodes), 12)    # 580 m gerade: etwa alle 80 m ein Knoten
        self.assertGreaterEqual(len(net.ways[0].nodes), 7)


class RoadTrackGapTests(unittest.TestCase):
    """Mindestabstand Strasse - Gleis (min_road_track_m)."""

    def _net(self, road_pts, track_pts, **kw):
        nodes = [node(i, x, y) for i, x, y in road_pts + track_pts]
        ways = [Way(1, [i for i, _x, _y in track_pts], {"railway": "rail"}),
                Way(2, [i for i, _x, _y in road_pts], {"highway": "secondary"})]
        opt = ne.NetworkOptions(merge_junctions_m=0, max_edge_m=0, min_segment_m=0, **kw)
        return ne.collect_network(make_osm(nodes, ways), SELECTION, opt)

    @staticmethod
    def _distances(net, art_road=0):
        tracks = [w for w in net.ways if w.art == 1][0]
        roads = [w for w in net.ways if w.art == art_road][0]
        poly = [net.nodes[i - 1] for i in tracks.nodes]
        out = []
        for i in roads.nodes:
            p = net.nodes[i - 1]
            best = 1e9
            for u, v in zip(poly[:-1], poly[1:]):
                dx, dy = v[0] - u[0], v[1] - u[1]
                l2 = dx * dx + dy * dy
                t = max(0.0, min(1.0, ((p[0] - u[0]) * dx + (p[1] - u[1]) * dy) / l2))
                best = min(best, math.hypot(p[0] - u[0] - t * dx, p[1] - u[1] - t * dy))
            out.append(best)
        return out

    def test_parallel_road_too_close_is_moved_away(self):
        track = [(100 + k, k * 100.0, 0.0) for k in range(6)]
        road = [(200 + k, k * 100.0, 5.0) for k in range(6)]
        net = self._net(road, track, min_road_track_m=9.0)
        d = self._distances(net)
        self.assertGreaterEqual(min(d), 8.99)
        self.assertLessEqual(max(d), 9.5)                    # nicht weiter als noetig
        self.assertGreater(net.stats.get("roads_moved", 0), 0)
        # die Strasse liegt weiter auf derselben Seite des Gleises (y > 0)
        road_way = [w for w in net.ways if w.art == 0][0]
        self.assertTrue(all(net.nodes[i - 1][1] > 5.0 for i in road_way.nodes))

    def test_off_when_zero_and_far_roads_stay(self):
        track = [(100 + k, k * 100.0, 0.0) for k in range(6)]
        near = [(200 + k, k * 100.0, 5.0) for k in range(6)]
        net = self._net(near, track, min_road_track_m=0)
        self.assertAlmostEqual(min(self._distances(net)), 5.0, places=3)
        far = [(200 + k, k * 100.0, 25.0) for k in range(6)]
        net = self._net(far, track, min_road_track_m=9.0)
        self.assertAlmostEqual(min(self._distances(net)), 25.0, places=3)
        self.assertNotIn("roads_moved", net.stats)

    def test_crossing_road_is_not_touched(self):
        track = [(100 + k, k * 100.0, 0.0) for k in range(6)]
        road = [(200 + k, 250.0, -300.0 + k * 120.0) for k in range(6)]   # kreuzt senkrecht
        net = self._net(road, track, min_road_track_m=9.0)
        road_way = [w for w in net.ways if w.art == 0][0]
        self.assertTrue(all(abs(net.nodes[i - 1][0] - 250.0) < 1e-6 for i in road_way.nodes))

    def test_shift_is_limited(self):
        track = [(100 + k, k * 100.0, 0.0) for k in range(6)]
        road = [(200 + k, k * 100.0, 1.0) for k in range(6)]
        net = self._net(road, track, min_road_track_m=9.0, max_road_shift_m=3.0)
        road_way = [w for w in net.ways if w.art == 0][0]
        self.assertTrue(all(abs(net.nodes[i - 1][1] - 1.0) <= 3.0 + 1e-6 for i in road_way.nodes))

    def test_defaults_keep_roads_close_to_their_osm_position(self):
        self.assertEqual(ne.NetworkOptions().min_road_track_m, 9.0)
        self.assertEqual(ne.NetworkOptions().max_road_shift_m, 5.0)

    def test_larger_distance_leaves_a_free_strip(self):
        track = [(100 + k, k * 100.0, 0.0) for k in range(6)]
        road = [(200 + k, k * 100.0, 10.0) for k in range(6)]     # 10 m: beruehrt sich nicht, aber kein Streifen
        net = self._net(road, track, min_road_track_m=14.0, max_road_shift_m=8.0)
        self.assertGreaterEqual(min(self._distances(net)), 13.99)
        untouched = self._net(road, track)                         # Standard 9 m: Strasse bleibt
        self.assertAlmostEqual(min(self._distances(untouched)), 10.0, places=3)


class UnifyTrackTemplatesTests(unittest.TestCase):
    """Gleiswege, die sich Knoten teilen, bekommen dieselbe Vorlage."""

    def _net(self, ways, pts, **kw):
        opt = ne.NetworkOptions(merge_junctions_m=0, max_edge_m=0, min_road_track_m=0, min_segment_m=0, **kw)
        return ne.collect_network(make_osm(pts, ways), SELECTION, opt)

    def _templates(self, net):
        return {w.osm_id: w.template.split("/")[-1] for w in net.ways}

    def test_siding_joined_to_main_track_gets_the_main_template(self):
        pts = [node(1, 0, 0), node(2, 400, 0), node(3, 520, 30)]
        ways = [Way(10, [1, 2], {"railway": "rail"}),
                Way(11, [2, 3], {"railway": "rail", "service": "siding"})]
        off = self._templates(self._net(ways, pts, unify_track_templates=False))
        self.assertNotEqual(off[10], off[11])                  # ohne Angleichen: zwei Vorlagen
        net = self._net(ways, pts, unify_track_templates=True)
        on = self._templates(net)
        self.assertEqual(on[10], on[11])
        self.assertEqual(on[10], "standard.street_template")   # die laengere Strecke gibt vor
        self.assertEqual(net.stats.get("tracks_unified"), 1)

    def test_unconnected_siding_keeps_its_own_template(self):
        pts = [node(1, 0, 0), node(2, 400, 0), node(3, 0, 200), node(4, 100, 200)]
        ways = [Way(10, [1, 2], {"railway": "rail"}),
                Way(11, [3, 4], {"railway": "rail", "service": "siding"})]
        on = self._templates(self._net(ways, pts, unify_track_templates=True))
        self.assertEqual(on[11], "simple.street_template")
        self.assertEqual(on[10], "standard.street_template")

    def test_longest_template_wins_in_a_group(self):
        pts = [node(1, 0, 0), node(2, 100, 0), node(3, 600, 0)]
        ways = [Way(10, [1, 2], {"railway": "rail"}),
                Way(11, [2, 3], {"railway": "rail", "service": "siding"})]
        on = self._templates(self._net(ways, pts, unify_track_templates=True))
        self.assertEqual(on[10], on[11])
        self.assertEqual(on[10], "simple.street_template")     # das Nebengleis ist laenger

    def test_default_is_on_and_streets_are_untouched(self):
        self.assertTrue(ne.NetworkOptions().unify_track_templates)
        pts = [node(1, 0, 0), node(2, 300, 0), node(3, 0, 50), node(4, 300, 50)]
        ways = [Way(10, [1, 2], {"railway": "rail"}), Way(11, [3, 4], {"highway": "secondary"})]
        net = self._net(ways, pts)
        self.assertEqual(self._templates(net)[11], "country_new_small.street_template")


class BridgeNeedsCrossingTests(unittest.TestCase):
    """Kurze Bruecken nur dort, wo sie einen anderen Weg kreuzen (min_bridge_free_m)."""

    def _net(self, extra_pts, extra_ways, **kw):
        pts = [node(1, 0, 0), node(2, 12, 0)] + extra_pts
        ways = [Way(1, [1, 2], {"railway": "rail", "bridge": "yes"})] + extra_ways
        opt = ne.NetworkOptions(merge_junctions_m=0, max_edge_m=0, min_segment_m=0, min_bridge_m=5,
                                min_road_track_m=0, **kw)
        return ne.collect_network(make_osm(pts, ways), SELECTION, opt)

    def _bridge_count(self, net):
        return sum(1 for w in net.ways if w.kind == ne.KIND_BRIDGE)

    def test_short_bridge_over_nothing_becomes_a_normal_edge(self):
        net = self._net([], [])
        self.assertEqual(self._bridge_count(net), 0)
        self.assertEqual(net.stats.get("bridges_no_crossing"), 1)

    def test_short_bridge_over_a_road_stays_a_bridge(self):
        pts = [node(10, 6, -50), node(11, 6, 50)]
        net = self._net(pts, [Way(2, [10, 11], {"highway": "secondary"})])
        self.assertEqual(self._bridge_count(net), 1)
        self.assertNotIn("bridges_no_crossing", net.stats)

    def test_long_bridges_are_always_kept(self):
        pts = [node(1, 0, 0), node(2, 60, 0)]
        ways = [Way(1, [1, 2], {"railway": "rail", "bridge": "yes"})]
        opt = ne.NetworkOptions(merge_junctions_m=0, max_edge_m=0, min_segment_m=0, min_road_track_m=0)
        net = ne.collect_network(make_osm(pts, ways), SELECTION, opt)
        self.assertEqual(self._bridge_count(net), 1)

    def test_a_road_that_only_meets_the_bridge_end_is_not_a_crossing(self):
        pts = [node(10, 12, 0), node(11, 12, 80)]                  # beginnt am Brueckenende
        net = self._net(pts, [Way(2, [10, 11], {"highway": "secondary"})])
        self.assertEqual(self._bridge_count(net), 0)

    def test_off_when_zero_keeps_all_bridges(self):
        net = self._net([], [], min_bridge_free_m=0)
        self.assertEqual(self._bridge_count(net), 1)

    def test_default_is_25_m(self):
        self.assertEqual(ne.NetworkOptions().min_bridge_free_m, 25.0)


class TrackSpacingTests(unittest.TestCase):
    """Gleisabstand zweier paralleler Gleise (track_spacing_m)."""

    def _net(self, follower_y, **kw):
        main = [(100 + k, k * 100.0, 0.0) for k in range(7)]
        follower = [(200 + k, k * 100.0, follower_y) for k in range(7)]
        pts = [node(i, x, y) for i, x, y in main + follower]
        ways = [Way(1, [i for i, _x, _y in main], {"railway": "rail"}),
                Way(2, [i for i, _x, _y in follower], {"railway": "rail"})]
        opt = ne.NetworkOptions(merge_junctions_m=0, max_edge_m=0, min_segment_m=0, min_road_track_m=0, **kw)
        return ne.collect_network(make_osm(pts, ways), SELECTION, opt)

    @staticmethod
    def _distances(net):
        first, second = net.ways[0], net.ways[1]
        poly = [net.nodes[i - 1] for i in first.nodes]
        out = []
        for i in second.nodes:
            p = net.nodes[i - 1]
            best = 1e9
            for u, v in zip(poly[:-1], poly[1:]):
                dx, dy = v[0] - u[0], v[1] - u[1]
                l2 = dx * dx + dy * dy
                t = max(0.0, min(1.0, ((p[0] - u[0]) * dx + (p[1] - u[1]) * dy) / l2))
                best = min(best, math.hypot(p[0] - u[0] - t * dx, p[1] - u[1] - t * dy))
            out.append(best)
        return out

    def test_wide_pair_is_moved_to_the_target_spacing(self):
        net = self._net(4.6)
        for d in self._distances(net):
            self.assertAlmostEqual(d, 4.1, delta=0.05)
        self.assertGreater(net.stats.get("tracks_spaced", 0), 0)

    def test_narrow_pair_is_widened_a_little(self):
        for d in self._distances(self._net(3.7)):
            self.assertAlmostEqual(d, 4.1, delta=0.05)

    def test_switch_area_and_far_tracks_stay(self):
        near = self._distances(self._net(3.0))            # unter 3,4 m: Weichenbereich
        self.assertAlmostEqual(min(near), 3.0, places=3)
        far = self._distances(self._net(8.0))             # ueber 5,6 m: kein Parallelgleis
        self.assertAlmostEqual(min(far), 8.0, places=3)

    def test_off_when_zero_and_default(self):
        self.assertAlmostEqual(min(self._distances(self._net(4.6, track_spacing_m=0))), 4.6, places=3)
        self.assertEqual(ne.NetworkOptions().track_spacing_m, 4.1)

    def test_shift_is_limited(self):
        net = self._net(5.5, track_spacing_m=3.0)         # wuerde 2,5 m verlangen, erlaubt sind 1,5 m
        self.assertGreaterEqual(min(self._distances(net)), 5.5 - 1.5 - 1e-6)


class BridgeBuiltFirstTests(unittest.TestCase):

    def test_bridge_comes_before_longer_roads_of_the_same_category(self):
        pts = [node(1, 0, 0), node(2, 100, 0), node(3, 200, 5), node(4, 300, 10), node(5, 400, 20),
               node(6, 100, 3), node(7, 130, 3)]
        ways = [
            Way(1, [1, 2, 3, 4, 5], {"highway": "secondary"}),                          # lang, mehrere Knoten
            Way(2, [6, 7], {"highway": "secondary", "bridge": "yes"}),                 # Bruecke, 30 m
        ]
        net = ne.collect_network(make_osm(pts, ways), SELECTION,
                                 ne.NetworkOptions(merge_junctions_m=0, max_edge_m=0, min_segment_m=0,
                                                   min_road_track_m=0))
        kinds = [w.kind for w in net.ways if w.art == 0]
        self.assertEqual(kinds[0], ne.KIND_BRIDGE)

if __name__ == "__main__":
    unittest.main()
