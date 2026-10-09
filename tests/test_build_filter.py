import unittest
from pathlib import Path

from tools.build_filter import soll_behalten

ROOT = Path(__file__).resolve().parent.parent


class BuildFilterTest(unittest.TestCase):

    def test_webengine_sprachen(self):
        for name in ("de.pak", "en-US.pak", "en-GB.pak"):
            self.assertTrue(soll_behalten(f"PySide6/translations/qtwebengine_locales/{name}"), name)
        for name in ("fr.pak", "ja.pak", "zh-CN.pak", "pt-BR.pak"):
            self.assertFalse(soll_behalten(f"PySide6/translations/qtwebengine_locales/{name}"), name)

    def test_backslash_pfade(self):
        self.assertFalse(soll_behalten("PySide6\\translations\\qtwebengine_locales\\fr.pak"))
        self.assertTrue(soll_behalten("PySide6\\translations\\qtwebengine_locales\\de.pak"))

    def test_webengine_ressourcen(self):
        self.assertFalse(soll_behalten("PySide6/resources/qtwebengine_devtools_resources.pak"))
        for name in ("icudtl.dat", "qtwebengine_resources.pak",
                     "qtwebengine_resources_100p.pak", "qtwebengine_resources_200p.pak"):
            self.assertTrue(soll_behalten(f"PySide6/resources/{name}"), name)

    def test_qt_uebersetzungen(self):
        for name in ("qtbase_de.qm", "qt_de.qm", "qt_help_en.qm", "qtbase_en.qm"):
            self.assertTrue(soll_behalten(f"PySide6/translations/{name}"), name)
        for name in ("qtbase_fr.qm", "qtbase_zh_CN.qm", "qt_help_fr.qm", "qtbase_pt_BR.qm"):
            self.assertFalse(soll_behalten(f"PySide6/translations/{name}"), name)

    def test_qml_ordner_entfernt_aber_dlls_bleiben(self):
        self.assertFalse(soll_behalten("PySide6/qml/QtQuick/qmldir"))
        self.assertFalse(soll_behalten("PySide6/Qt/qml/QtQuick/Controls/plugin.dll"))
        for name in ("Qt6Quick.dll", "Qt6Qml.dll", "Qt6Pdf.dll", "Qt6WebEngineCore.dll", "opengl32sw.dll"):
            self.assertTrue(soll_behalten(f"PySide6/{name}"), name)

    def test_pillow(self):
        self.assertFalse(soll_behalten("PIL/_avif.cp311-win_amd64.pyd"))
        self.assertTrue(soll_behalten("PIL/_imaging.cp311-win_amd64.pyd"))

    def test_eigene_dateien_bleiben(self):
        for pfad in ("src/map/web/index.html", "src/icons/app.ico", "src/gui/icons/x.svg",
                     "certifi/cacert.pem", "scipy/ndimage/_nd_image.pyd"):
            self.assertTrue(soll_behalten(pfad), pfad)

    def test_build_spec_nutzt_filter(self):
        text = (ROOT / "build.spec").read_text(encoding="utf-8")
        self.assertIn("from tools.build_filter import soll_behalten", text)
        self.assertIn("a.datas = [d for d in a.datas if soll_behalten(d[0])]", text)
        self.assertIn("a.binaries = [b for b in a.binaries if soll_behalten(b[0])]", text)


if __name__ == "__main__":
    unittest.main()