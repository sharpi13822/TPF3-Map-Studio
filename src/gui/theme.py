"""
Farben und Stilvorlage (Qt Style Sheet) fuer das ganze Studio.

Die Farben stammen aus dem Titelbild: dunkles Blaugrau fuer Flaechen, helles Blau als Akzent.
apply_theme(app) setzt die Vorlage fuer alle Fenster und Dialoge.
"""

from __future__ import annotations

from string import Template

from src.gui.icon_set import ICON_DIR

PALETTE = {
    "bg": "#11191e",        # Fensterhintergrund
    "panel": "#141e26",     # Leisten, Docks, Eingabefelder
    "raised": "#1a262e",    # Knoepfe, erhabene Flaechen
    "hover": "#22313c",     # Mauszeiger auf Knoepfen
    "border": "#2a3a46",    # Rahmen und Trenner
    "accent": "#15b9f9",    # Akzent: Ueberschriften, Fokus, Regler
    "strong": "#0a81c2",    # Auswahl und aktive Knoepfe
    "pressed": "#086aa3",   # gedrueckter Knopf
    "text": "#d5dee5",
    "dim": "#8ea1af",
    "off": "#55656f",       # deaktiviert
    "onacc": "#ffffff",     # Schrift auf Akzentflaechen
}

QSS = Template("""
QWidget {
    background-color: $bg;
    color: $text;
    selection-background-color: $strong;
    selection-color: $onacc;
}
QMainWindow, QDialog, QMessageBox {
    background-color: $bg;
}
QLabel, QCheckBox, QRadioButton {
    background-color: transparent;
}
QToolTip {
    background-color: $raised;
    color: $text;
    border: 1px solid $accent;
    padding: 4px;
}

/* ---------- Menues ---------- */
QMenuBar {
    background-color: $panel;
    border-bottom: 1px solid $border;
}
QMenuBar::item {
    background-color: transparent;
    padding: 5px 10px;
}
QMenuBar::item:selected {
    background-color: $raised;
}
QMenu {
    background-color: $panel;
    border: 1px solid $border;
    padding: 4px;
}
QMenu::item {
    padding: 6px 28px 6px 26px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: $strong;
    color: $onacc;
}
QMenu::item:disabled {
    color: $off;
}
QMenu::separator {
    height: 1px;
    background-color: $border;
    margin: 4px 8px;
}

/* ---------- Werkzeugleiste ---------- */
QToolBar {
    background-color: $panel;
    border: 0;
    border-bottom: 1px solid $border;
    spacing: 4px;
    padding: 4px;
}
QToolBar::separator {
    background-color: $border;
    width: 1px;
    margin: 4px 6px;
}
QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 4px;
}
QToolButton:hover {
    background-color: $raised;
    border-color: $border;
}
QToolButton:checked {
    background-color: $strong;
    border-color: $accent;
}
QToolButton:pressed {
    background-color: $pressed;
}

/* ---------- Docks und Statusleiste ---------- */
QDockWidget {
    color: $accent;
    font-weight: bold;
}
QDockWidget::title {
    background-color: $panel;
    padding: 6px 10px;
    border-bottom: 1px solid $border;
}
QStatusBar {
    background-color: $panel;
    color: $dim;
    border-top: 1px solid $border;
}
QSplitter::handle {
    background-color: $border;
}

/* ---------- Knoepfe ---------- */
QPushButton {
    background-color: $raised;
    color: $text;
    border: 1px solid $border;
    border-radius: 6px;
    padding: 5px 12px;
}
QPushButton:hover {
    background-color: $hover;
    border-color: $accent;
}
QPushButton:pressed {
    background-color: $pressed;
    color: $onacc;
}
QPushButton:default {
    border-color: $accent;
}
QPushButton:disabled {
    background-color: $panel;
    color: $off;
    border-color: $border;
}

/* ---------- Eingabefelder ---------- */
QLineEdit, QTextEdit, QPlainTextEdit, QTextBrowser, QAbstractSpinBox {
    background-color: $panel;
    color: $text;
    border: 1px solid $border;
    border-radius: 5px;
    padding: 3px 6px;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QAbstractSpinBox:focus {
    border: 1px solid $accent;
}
QLineEdit:disabled, QAbstractSpinBox:disabled {
    color: $off;
}
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
    subcontrol-origin: border;
    width: 18px;
    border: 0;
    background-color: $raised;
}
QAbstractSpinBox::up-button {
    subcontrol-position: top right;
    border-top-right-radius: 4px;
}
QAbstractSpinBox::down-button {
    subcontrol-position: bottom right;
    border-bottom-right-radius: 4px;
}
QAbstractSpinBox::up-button:hover, QAbstractSpinBox::down-button:hover {
    background-color: $hover;
}
QAbstractSpinBox::up-arrow {
    image: url($icons/ui_pfeil_hoch.png);
    width: 10px;
    height: 10px;
}
QAbstractSpinBox::down-arrow {
    image: url($icons/ui_pfeil_runter.png);
    width: 10px;
    height: 10px;
}
QAbstractSpinBox::up-arrow:disabled, QAbstractSpinBox::up-arrow:off {
    image: url($icons/ui_pfeil_hoch_aus.png);
}
QAbstractSpinBox::down-arrow:disabled, QAbstractSpinBox::down-arrow:off {
    image: url($icons/ui_pfeil_runter_aus.png);
}

/* ---------- Auswahlfelder ---------- */
QComboBox {
    background-color: $panel;
    color: $text;
    border: 1px solid $border;
    border-radius: 5px;
    padding: 3px 8px;
}
QComboBox:hover, QComboBox:focus {
    border-color: $accent;
}
QComboBox:disabled {
    color: $off;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 22px;
    border: 0;
}
QComboBox::down-arrow {
    image: url($icons/ui_pfeil_runter.png);
    width: 10px;
    height: 10px;
}
QComboBox QAbstractItemView {
    background-color: $panel;
    border: 1px solid $border;
    selection-background-color: $strong;
    selection-color: $onacc;
    outline: 0;
}

/* ---------- Haken und Auswahlkreise ---------- */
QCheckBox, QRadioButton {
    spacing: 8px;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
}
QCheckBox::indicator:unchecked {
    image: url($icons/ui_haken_aus.png);
}
QCheckBox::indicator:checked {
    image: url($icons/ui_haken_an.png);
}
QRadioButton::indicator:unchecked {
    image: url($icons/ui_kreis_aus.png);
}
QRadioButton::indicator:checked {
    image: url($icons/ui_kreis_an.png);
}

/* ---------- Regler ---------- */
QSlider::groove:horizontal {
    height: 4px;
    background-color: $raised;
    border-radius: 2px;
}
QSlider::sub-page:horizontal {
    background-color: $strong;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background-color: $accent;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background-color: $onacc;
}
QSlider::handle:horizontal:disabled {
    background-color: $off;
}

/* ---------- Scrollleisten ---------- */
QScrollBar:vertical {
    background-color: $bg;
    width: 12px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: $border;
    min-height: 24px;
    border-radius: 5px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover {
    background-color: $strong;
}
QScrollBar:horizontal {
    background-color: $bg;
    height: 12px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background-color: $border;
    min-width: 24px;
    border-radius: 5px;
    margin: 2px;
}
QScrollBar::handle:horizontal:hover {
    background-color: $strong;
}
QScrollBar::add-line, QScrollBar::sub-line {
    height: 0;
    width: 0;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background-color: transparent;
}

/* ---------- Gruppen, Reiter, Listen und Tabellen ---------- */
QGroupBox {
    border: 1px solid $border;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 6px;
    color: $accent;
    background-color: $bg;
}
QTabWidget::pane {
    border: 1px solid $border;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: $raised;
    border: 1px solid $border;
    padding: 5px 12px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected {
    background-color: $strong;
    color: $onacc;
}
QListWidget, QListView, QTreeWidget, QTreeView, QTableWidget, QTableView {
    background-color: $panel;
    border: 1px solid $border;
    alternate-background-color: $raised;
    outline: 0;
}
QListWidget::item:selected, QListView::item:selected, QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: $strong;
    color: $onacc;
}
QHeaderView::section {
    background-color: $raised;
    color: $accent;
    border: 0;
    border-right: 1px solid $border;
    padding: 4px 8px;
}
QProgressBar {
    background-color: $panel;
    border: 1px solid $border;
    border-radius: 5px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: $strong;
    border-radius: 4px;
}
""")


def build_stylesheet(icon_dir=None) -> str:
    """Stilvorlage als Text. Die Pfade der Bedienelement-Bilder werden mit Schraegstrichen eingesetzt (Qt-Regel)."""

    folder = str(icon_dir or ICON_DIR).replace("\\", "/")

    return QSS.substitute(PALETTE, icons=folder)


def apply_theme(app) -> None:
    """Setzt die Stilvorlage fuer die ganze Anwendung (alle Fenster und Dialoge)."""

    if app is None:
        return

    app.setStyleSheet(build_stylesheet())
