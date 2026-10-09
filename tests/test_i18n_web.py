"""Tests fuer die Uebersetzung der Kartenoberflaeche (src/map/web).

Wie bei den Programmtexten ist der deutsche Originaltext der Schluessel:
t("Alle") im JavaScript und der feste Text in index.html. Das Woerterbuch
steht in src/i18n_web_en.py, der lokale Server liefert es als i18n_data.js.
"""

import json
import re
import shutil
import subprocess
import tempfile
import unittest
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from src import i18n
from src.core.server import LocalServer
from src.i18n_web_en import WEB_CATALOG

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "src" / "map" / "web"
JS = WEB / "js"

# Texte, die auf Englisch genauso heissen wie auf Deutsch.
SAME_IN_BOTH = {
    "JSON Export",
    "JSON Import",
    "OpenStreetMap",
    "Layer:",
    "Polygon",
    "Multipolygon",
    "Parks",
    "Vegetation",
    "Name",
    "Tunnel",
}

STRING_START = ("'", '"', "`")


def _read_string(text, index):
    """Liest ein JS-Stringliteral ab index. Gibt (Inhalt, Ende) oder None zurueck."""
    quote = text[index]
    result = []
    i = index + 1
    while i < len(text):
        char = text[i]
        if char == "\\":
            nxt = text[i + 1]
            result.append({"n": "\n", "t": "\t"}.get(nxt, nxt))
            i += 2
            continue
        if char == quote:
            return "".join(result), i + 1
        if quote == "`" and text.startswith("${", i):
            return None
        result.append(char)
        i += 1
    return None


def _call_texts(text, name):
    """Alle Texte aus name("a" + "b", ...) mit festen Stringliteralen.

    Gibt (Liste der Texte, Liste der Stellen ohne festen Text) zurueck.
    """
    found, dynamic = [], []
    for match in re.finditer(r"(?<![\w.$])" + name + r"\(", text):
        line = text.count("\n", 0, match.start()) + 1
        i = match.end()
        parts = []
        while True:
            while text[i].isspace():
                i += 1
            if text[i] not in STRING_START:
                parts = None
                break
            piece = _read_string(text, i)
            if piece is None:
                parts = None
                break
            parts.append(piece[0])
            i = piece[1]
            while text[i].isspace():
                i += 1
            if text[i] == "+":
                i += 1
                continue
            break
        if parts is None:
            dynamic.append(line)
        else:
            found.append("".join(parts))
    return found, dynamic


def js_keys():
    """Schluessel aus t()/tf() in allen JS-Dateien (ausser i18n.js selbst)."""
    keys, dynamic = {}, []
    for path in sorted(JS.glob("*.js")):
        if path.name == "i18n.js":
            continue
        text = path.read_text(encoding="utf-8")
        for name in ("t", "tf"):
            found, bad = _call_texts(text, name)
            for key in found:
                keys.setdefault(key, set()).add(path.name)
            dynamic.extend(f"{path.name}:{line}" for line in bad)
    return keys, dynamic


class _Collector(HTMLParser):
    """Sammelt die festen Texte der Karte: Textknoten im body, title und alt."""

    VOID_TAGS = {"img", "input", "br", "hr", "link", "meta"}

    def __init__(self):
        super().__init__()
        self.texts = []
        self.overrides = []
        self._skip = 0
        self._in_body = False
        self._override_stack = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "body":
            self._in_body = True
        if tag in ("script", "style"):
            self._skip += 1
        if self._in_body:
            for name in ("title", "alt"):
                value = attributes.get(name)
                if value and value.strip():
                    self.texts.append(re.sub(r"\s+", " ", value).strip())
        if "data-i18n" in attributes:
            self.overrides.append(attributes["data-i18n"])
        if tag not in self.VOID_TAGS:
            self._override_stack.append(attributes.get("data-i18n"))

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1
        if tag not in self.VOID_TAGS and self._override_stack:
            self._override_stack.pop()

    def handle_data(self, data):
        if not self._in_body or self._skip:
            return
        text = re.sub(r"\s+", " ", data).strip()
        if not text:
            return
        override = next((o for o in reversed(self._override_stack[-1:]) if o), None)
        self.texts.append(override or text)


def html_keys():
    collector = _Collector()
    collector.feed((WEB / "index.html").read_text(encoding="utf-8"))
    return set(collector.texts)


def placeholders(text):
    return set(re.findall(r"\{(\w+)\}", text))


class WebCatalogTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.js, cls.dynamic = js_keys()
        cls.html = html_keys()

    def test_all_calls_use_fixed_texts(self):
        self.assertEqual(self.dynamic, [], "t()/tf() nur mit festem Text aufrufen")

    def test_the_scan_finds_the_calls(self):
        self.assertGreaterEqual(len(self.js), 40)
        self.assertIn("Objekt Information", self.js)
        self.assertIn("Eckpunkte: {count}", self.js)

    def test_every_js_text_has_an_english_entry(self):
        missing = sorted(key for key in self.js if key not in WEB_CATALOG)
        self.assertEqual(missing, [])

    def test_every_html_text_has_an_english_entry(self):
        missing = sorted(key for key in self.html if key not in WEB_CATALOG)
        self.assertEqual(missing, [])

    def test_no_stale_entries(self):
        stale = sorted(key for key in WEB_CATALOG if key not in self.js and key not in self.html)
        self.assertEqual(stale, [])

    def test_placeholders_match(self):
        for german, english in WEB_CATALOG.items():
            self.assertEqual(placeholders(german), placeholders(english), german)

    def test_english_entries_are_real_translations(self):
        for german, english in WEB_CATALOG.items():
            self.assertTrue(english.strip(), german)
            if german not in SAME_IN_BOTH:
                self.assertNotEqual(german, english, f"nicht uebersetzt: {german}")

    def test_english_entries_contain_no_german_letters(self):
        for german, english in WEB_CATALOG.items():
            for letter in "äöüÄÖÜß":
                self.assertNotIn(letter, english, german)

    def test_the_building_button_has_its_own_key(self):
        # "Gebaeude" heisst im Info-Feld "Buildings", am Zeichenknopf "Building".
        self.assertEqual(WEB_CATALOG["Gebäude"], "Buildings")
        self.assertEqual(WEB_CATALOG["Gebäude (Zeichenknopf)"], "Building")
        self.assertIn('data-i18n="Gebäude (Zeichenknopf)"', (WEB / "index.html").read_text(encoding="utf-8"))


class WebScriptOrderTest(unittest.TestCase):

    def test_translation_scripts_come_first(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        data = html.index('src="i18n_data.js"')
        helper = html.index('src="js/i18n.js"')
        self.assertLess(data, helper)
        for later in ("js/layer_styles.js", "js/info_panel.js", "js/draw_manager.js", "js/map.js"):
            self.assertLess(helper, html.index(later), later)


class WebScriptTest(unittest.TestCase):

    def tearDown(self):
        i18n.set_language("de")

    @staticmethod
    def _parse(script):
        match = re.fullmatch(
            r'window\.TPF_LANG = ("\w+");\nwindow\.TPF_I18N = (\{.*\});\n',
            script,
            re.S,
        )
        assert match, script[:80]
        return json.loads(match.group(1)), json.loads(match.group(2))

    def test_german_has_an_empty_dictionary(self):
        i18n.set_language("de")
        language, dictionary = self._parse(i18n.web_script())
        self.assertEqual(language, "de")
        self.assertEqual(dictionary, {})

    def test_english_carries_the_catalog(self):
        i18n.set_language("en")
        language, dictionary = self._parse(i18n.web_script())
        self.assertEqual(language, "en")
        self.assertEqual(dictionary, WEB_CATALOG)

    def test_language_can_be_given_explicitly(self):
        language, dictionary = self._parse(i18n.web_script("en"))
        self.assertEqual((language, dictionary["Alle"]), ("en", "All"))


class ServerRouteTest(unittest.TestCase):

    def setUp(self):
        self.server = LocalServer(port=0)
        self.server.start()
        self.addCleanup(self.server.stop)
        self.addCleanup(i18n.set_language, "de")

    def _get(self, path):
        with urllib.request.urlopen(self.server.url + path, timeout=10) as response:
            return response.status, response.headers.get("Content-Type"), response.read().decode("utf-8")

    def test_dictionary_follows_the_language(self):
        i18n.set_language("de")
        status, kind, body = self._get("/i18n_data.js")
        self.assertEqual(status, 200)
        self.assertIn("javascript", kind)
        self.assertIn('TPF_LANG = "de"', body)
        i18n.set_language("en")
        _status, _kind, body = self._get("/i18n_data.js?v=1")
        self.assertIn('TPF_LANG = "en"', body)
        self.assertIn('"Alle": "All"', body)

    def test_normal_files_are_still_served(self):
        status, _kind, body = self._get("/index.html")
        self.assertEqual(status, 200)
        self.assertIn("i18n_data.js", body)


NODE_HARNESS = r"""
const fs = require('fs');
const out = {};
const source = fs.readFileSync(process.argv[2], 'utf8');
const dictionary = {'Alle': 'All', 'Gebäude (Zeichenknopf)': 'Building', 'Eckpunkte: {count}': 'Vertices: {count}',
                    'Hinweis': 'Note'};
const nodes = [
  {nodeValue: '\n   Alle  \n', parentElement: {getAttribute: () => null}},
  {nodeValue: '\n   ', parentElement: {getAttribute: k => k === 'data-i18n' ? 'Gebäude (Zeichenknopf)' : null}},
  {nodeValue: ' Gebäude ', parentElement: {getAttribute: k => k === 'data-i18n' ? 'Gebäude (Zeichenknopf)' : null}},
  {nodeValue: 'Unbekannt', parentElement: {getAttribute: () => null}},
];
const attr = {title: 'Hinweis'};
const element = {getAttribute: k => attr[k] ?? null, setAttribute: (k, v) => { attr[k] = v; }};
const root = {nodeType: 1, querySelectorAll: () => [element], getAttribute: () => null, setAttribute(){}};
global.NodeFilter = {SHOW_TEXT: 4};
global.document = {
  documentElement: {}, body: root,
  createTreeWalker: () => { let i = -1; return {currentNode: null, nextNode() { i++; this.currentNode = nodes[i]; return i < nodes.length; }}; },
};
global.window = {TPF_I18N: dictionary, TPF_LANG: 'en'};
new Function('window', 'document', 'NodeFilter', source)(global.window, global.document, global.NodeFilter);
const w = global.window;
out.t_known = w.t('Alle') === 'All';
out.t_unknown = w.t('Gibt es nicht') === 'Gibt es nicht';
out.t_prototype_key = w.t('constructor') === 'constructor';
out.tf = w.tf('Eckpunkte: {count}', {count: 5}) === 'Vertices: 5';
out.tf_missing_value = w.tf('Eckpunkte: {count}', {}) === 'Vertices: {count}';
out.lang = global.document.documentElement.lang === 'en';
out.text_keeps_whitespace = nodes[0].nodeValue === '\n   All  \n';
out.whitespace_node_untouched = nodes[1].nodeValue === '\n   ';
out.override_key = nodes[2].nodeValue === ' Building ';
out.unknown_text_untouched = nodes[3].nodeValue === 'Unbekannt';
out.title_attribute = attr.title === 'Note';
console.log(JSON.stringify(out));
"""


@unittest.skipUnless(shutil.which("node"), "Node.js nicht installiert")
class I18nScriptTest(unittest.TestCase):

    def test_helper_with_node(self):
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / "harness.js"
            script.write_text(NODE_HARNESS, encoding="utf-8")
            result = subprocess.run(
                ["node", str(script), str(JS / "i18n.js")],
                capture_output=True, text=True, timeout=60,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        out = json.loads(result.stdout.strip().splitlines()[-1])
        for key, value in out.items():
            self.assertTrue(value, key)

    def test_helper_without_node_has_the_public_functions(self):
        text = (JS / "i18n.js").read_text(encoding="utf-8")
        for name in ("window.t = t;", "window.tf = tf;", "window.translateDom = translateDom;"):
            self.assertIn(name, text)


if __name__ == "__main__":
    unittest.main()
