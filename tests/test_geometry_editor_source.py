"""Prueft den Kopf und bekannte Fehler in geometry_editor.js (Textpruefung)."""

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "src" / "map" / "web" / "js" / "geometry_editor.js"


def _source():
    return PATH.read_text(encoding="utf-8")


class HeaderTest(unittest.TestCase):

    def test_no_template_leftovers(self):
        text = _source()
        for needle in ("ChatGPT", "<dein Projekt>", "V9 TEST", "TPF2 MAP STUDIO"):
            self.assertNotIn(needle, text, needle)

    def test_names_the_project(self):
        self.assertIn("TPF3 Map Studio", _source()[:400])


class DebugOutputTest(unittest.TestCase):

    def test_console_output_only_inside_debug_helpers(self):
        text = _source()
        self.assertEqual(text.count("console.log("), 1)
        log_body = text[text.index("    log(...args) {"):text.index("    table(data) {")]
        self.assertIn("console.log(...args)", log_body)


class StateTest(unittest.TestCase):

    def test_active_vertex_starts_empty(self):
        text = _source()
        constructor = text[text.index("constructor("):text.index("START EDIT MODE")]
        self.assertIn("this.activeVertex = null;", constructor)

    def test_delete_key_needs_a_selection(self):
        text = _source()
        self.assertNotIn("this.activeVertex === null", text)
        self.assertNotIn("this.activeVertex !== null", text)
        self.assertIn("if (this.activeVertex == null) return;", text)

    def test_history_belongs_to_one_object(self):
        text = _source()
        start = text[text.index("    start(object) {"):text.index("STOP EDIT MODE")]
        self.assertIn("this.historyObject !== object", start)
        self.assertIn("this.undoStack = [];", start)
        self.assertIn("this.activeVertex = null;", start)

    def test_segment_handle_is_registered_once(self):
        self.assertEqual(len(re.findall(r"this\.segmentHandles\.push\(marker\)", _source())), 1)


class HistoryRulesTest(unittest.TestCase):

    def test_history_is_blocked_for_osm_objects(self):
        text = _source()
        self.assertIn("canUseHistory()", text)
        self.assertIn('typeof this.object.tpf2?.id === "number"', text)
        undo = text[text.index("    undo() {"):text.index("    redo() {")]
        redo = text[text.index("    redo() {"):text.index("INSERT NEW VERTEX")]
        for body in (undo, redo):
            self.assertIn("if (!this.canUseHistory()) return;", body)
            self.assertIn("this.syncHistoryToPython();", body)

    def test_history_is_reported_to_python(self):
        text = _source()
        body = text[text.index("    syncHistoryToPython() {"):text.index("UNDO\n")]
        self.assertIn("bridges.adapter.polylineMoved(", body)
        self.assertIn("String(this.object.tpf2.id)", body)


HARNESS = r"""
const fs = require('fs');
global.document = {addEventListener(){}, removeEventListener(){}};
global.L = {};
const calls = [], toasts = [];
global.bridges = {adapter: {polylineMoved: (id, g) => calls.push([id, JSON.stringify(g)])}};
global.showToast = msg => toasts.push(msg);
global.t = text => text;  // Uebersetzung (js/i18n.js): hier unveraendert
const src = fs.readFileSync(process.argv[2], 'utf8') + '\nmodule.exports = GeometryEditor;';
const m = {exports: {}};
new Function('module', 'exports', src)(m, m.exports);
const GE = m.exports;
const mk = (id, g) => ({_map: {}, tpf2: {id, type: 'polyline', geometry: g}, setLatLngs(){}, redraw(){}});
const e = new GE({});
for (const k of ['prepareHandleLayer','enableEditMode','refresh','bindEvents','unbindEvents','clear','disableEditMode','restoreStyle']) e[k] = () => {};
const out = {};
const own = mk('l1', [[0,0],[0,1],[0,2]]), osm = mk(42, [[5,5],[5,6],[5,7]]);
e.start(own); e.saveHistory(); own.tpf2.geometry = [[0,0],[9,9],[0,2]];
e.undo();
out.ownRestored = JSON.stringify(own.tpf2.geometry) === '[[0,0],[0,1],[0,2]]';
out.ownSynced = calls.length === 1 && calls[0][0] === 'l1';
e.start(osm); e.saveHistory(); osm.tpf2.geometry = [[5,5],[8,8],[5,7]];
const before = JSON.stringify(osm.tpf2.geometry), n = calls.length;
e.undo(); e.redo();
out.osmUntouched = JSON.stringify(osm.tpf2.geometry) === before && calls.length === n && toasts.length === 2;
const a = mk(1, [[0,0],[0,1],[0,2]]), b = mk('l2', [[5,5],[5,6],[5,7]]);
e.start(a); e.saveHistory(); a.tpf2.geometry = [[0,0],[3,3],[0,2]];
e.start(b); e.undo();
out.otherObjectSafe = JSON.stringify(b.tpf2.geometry) === '[[5,5],[5,6],[5,7]]';
let removed = false; e.removeVertex = () => { removed = true; };
e.onKeyDown({key: 'Delete', preventDefault(){}});
out.deleteNeedsSelection = !removed;
console.log(JSON.stringify(out));
"""


@unittest.skipUnless(shutil.which("node"), "Node.js nicht installiert")
class BehaviourTest(unittest.TestCase):

    def test_editor_behaviour_with_node(self):
        import json

        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / "harness.js"
            script.write_text(HARNESS, encoding="utf-8")
            result = subprocess.run(
                ["node", str(script), str(PATH)],
                capture_output=True, text=True, timeout=60,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        out = json.loads(result.stdout.strip().splitlines()[-1])
        for key, value in out.items():
            self.assertTrue(value, key)


if __name__ == "__main__":
    unittest.main()
