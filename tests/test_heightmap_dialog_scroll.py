import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPoint, QPointF, QRect, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication, QDoubleSpinBox, QScrollArea

from src.gui.heightmap_dialog import HeightmapDialog, _WheelGuard

_APP = QApplication.instance() or QApplication([])


def _dialog():
    # Der Konstruktor braucht von der Auswahl nur den Mittelpunkt.
    return HeightmapDialog(None, SimpleNamespace(center=(50.0, 8.0)))


class HeightmapDialogScrollTest(unittest.TestCase):

    def test_einstellungen_liegen_in_scrollflaeche(self):
        dialog = _dialog()
        scroll = dialog._scroll_area
        self.assertIsInstance(scroll, QScrollArea)
        self.assertTrue(scroll.widgetResizable())

        content = scroll.widget()
        for widget in (
            dialog.status_label,
            dialog.download_button,
            dialog.clip_checkbox,
            dialog.clip_slider,
            dialog.game_values_label,
        ):
            self.assertTrue(content.isAncestorOf(widget))

    def test_knopfleiste_bleibt_ausserhalb_der_scrollflaeche(self):
        dialog = _dialog()
        content = dialog._scroll_area.widget()

        for button in (
            dialog.guide_button,
            dialog.export_button,
            dialog.biome_button,
            dialog.towns_button,
            dialog.industries_button,
            dialog.stations_button,
        ):
            self.assertFalse(content.isAncestorOf(button))
            self.assertTrue(dialog.isAncestorOf(button))

    def test_startgroesse_passt_auf_kleinen_bildschirm(self):
        dialog = _dialog()
        dialog._fit_to_screen(QRect(0, 0, 1280, 720))

        self.assertLessEqual(dialog.width(), 1280)
        self.assertLessEqual(dialog.height(), 720)

    def test_grosser_bildschirm_zeigt_moeglichst_alles(self):
        dialog = _dialog()
        dialog._fit_to_screen(QRect(0, 0, 3840, 2160))

        self.assertGreaterEqual(dialog.height(), 600)

    def test_mausrad_wird_bei_feldern_ohne_fokus_nicht_verbraucht(self):
        spin = QDoubleSpinBox()
        guard = _WheelGuard()

        event = QWheelEvent(
            QPointF(5, 5),
            QPointF(5, 5),
            QPoint(0, 0),
            QPoint(0, 120),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            False,
        )

        self.assertTrue(guard.eventFilter(spin, event))
        self.assertFalse(event.isAccepted())

    def test_andere_ereignisse_bleiben_unberuehrt(self):
        guard = _WheelGuard()
        self.assertFalse(
            guard.eventFilter(QDoubleSpinBox(), QEvent(QEvent.Type.Show))
        )

    def test_felder_sind_gegen_versehentliches_mausrad_geschuetzt(self):
        dialog = _dialog()

        for widget in (
            dialog.clip_slider,
            dialog.smooth_sigma_input,
            dialog.source_combo,
        ):
            self.assertEqual(widget.focusPolicy(), Qt.FocusPolicy.StrongFocus)


if __name__ == "__main__":
    unittest.main()