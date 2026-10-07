import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _window_source():
    return (ROOT / "src" / "window.py").read_text(encoding="utf-8")


def _main_window_methods():
    tree = ast.parse(_window_source())
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "MainWindow":
            return {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
    raise AssertionError("MainWindow nicht gefunden")


class ProjectActionsTest(unittest.TestCase):

    def test_methods_exist(self):
        methods = _main_window_methods()
        for name in ("_save_project", "_save_project_as", "_save_project_to", "_new_project", "_close_project",
                     "_reset_project", "_confirm_discard_changes", "_load_project_file"):
            self.assertIn(name, methods, name)

    def test_actions_are_connected_and_in_menu(self):
        source = _window_source()
        for action, handler in (("new_project", "_new_project"), ("save_project_as", "_save_project_as"),
                                ("close_project", "_close_project"), ("save_project", "_save_project"),
                                ("open_project", "_open_project")):
            self.assertIn(f"self.actions.{action}.triggered.connect(\n            self.{handler}\n        )".replace("\n", "\r\n" if "\r\n" in source else "\n"),
                          source, action)
        for action in ("new_project", "open_project", "save_project", "save_project_as", "close_project"):
            self.assertIn(f"self.actions.{action}\n".replace("\n", "\r\n" if "\r\n" in source else "\n"), source, action)

    def test_save_remembers_file_and_load_sets_it(self):
        source = _window_source()
        self.assertIn("_project_file = None", source)
        self.assertIn("self._project_file = filename", source)
        self.assertIn("self._project_file or", source)

    def test_reset_clears_everything_on_the_map(self):
        source = _window_source()
        reset = source[source.index("def _reset_project"):source.index("# Projekt-Dashboard")]
        for needle in ("controller.project = Project()", "UndoStack()", "clearMarkers", "clearPolylines", "clearRectangle",
                       "clearStations", "clearVegetation", "set_visible(layer, False)", "_project_file = None"):
            self.assertIn(needle, reset, needle)

    def test_map_api_has_all_functions_the_reset_calls(self):
        js = (ROOT / "src" / "map" / "web" / "js" / "map.js").read_text(encoding="utf-8")
        source = _window_source()
        reset = source[source.index("def _reset_project"):source.index("# Projekt-Dashboard")]
        import re
        names = re.findall(r"'(clear\w+)'", reset)
        self.assertGreaterEqual(len(names), 12)
        for name in names:
            self.assertRegex(js, rf"\n    {name}\(\) {{", name)

    def test_test_marker_is_gone(self):
        self.assertNotIn("test_marker", (ROOT / "src" / "gui" / "actions.py").read_text(encoding="utf-8"))
        self.assertNotIn("Testmarker", (ROOT / "src" / "gui" / "actions.py").read_text(encoding="utf-8"))

    def test_actions_have_tooltips(self):
        actions = (ROOT / "src" / "gui" / "actions.py").read_text(encoding="utf-8")
        for name in ("save_project_as", "close_project"):
            self.assertIn(f"self.{name}.setToolTip", actions, name)

    def test_preflight_dialog_no_longer_mentions_import_run(self):
        text = (ROOT / "src" / "gui" / "preflight_dialog.py").read_text(encoding="utf-8")
        self.assertNotIn("Import-Lauf", text)


if __name__ == "__main__":
    unittest.main()
