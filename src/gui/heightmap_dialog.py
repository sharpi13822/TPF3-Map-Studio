import io
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QComboBox,
    QApplication,
)
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut
from PySide6.QtCore import Qt

from src.gui.heightmap_guide import HeightmapGuideDialog
from src.gui.map_size_presets import find_by_pixels
from src.heightmap.heightmap_exporter import (
    build_heightmap_array,
    build_heightmap_array_preview,
    export_heightmap_png,
    pixel_size_for_selection,
)
from src.heightmap.tpf3_paths import find_tpf3_heightmaps_folder
from src.heightmap.infrastructure_flatten import (
    build_infrastructure_mask,
    flatten_infrastructure,
)
from src.heightmap.terrain_smoothing import (
    smooth_terrain,
    compress_heights,
    DEFAULT_SMOOTHING_SIGMA_M,
)
from src.heightmap.water_level import suggest_water_level, render_preview
from src.heightmap.water_terrain_blend import (
    build_water_mask,
    blend_terrain_to_water,
    enforce_osm_water,
)
from src.heightmap.water_slope_compensation import (
    compensate_water_slope,
    DEFAULT_SMOOTHING_M,
)

DEFAULT_CACHE_DIR = Path.home() / ".tpf2_map_studio" / "dem_cache"
# Das Copernicus-Hoehenmodell hat nur etwa 30 m pro Pixel: eine Uebergangs-
# breite von 30 m ist genau ein Pixel und erzeugt steile Waende am Ufer.
DEFAULT_TRANSITION_M = 100.0

# Gewaesser, die von Natur aus hoeher als diese Grenze ueber dem gewaehlten
# Wasserspiegel liegen (Baeche und Bergseen), werden bei der Terrain-
# Anpassung nicht abgesenkt - sonst entstehen tiefe Schluchten.
DEFAULT_BLEND_MAX_RISE_M = 12.0

# Gemessen im Spiel (Terrassen-Tests, 01.10.2026): Das Spiel faerbt das
# Gelaende nach der Hoehe UEBER DEM WASSERSPIEGEL. Fels beginnt zwischen
# ca. 325 und 350 m, Schnee zwischen ca. 375 und 425 m. Im Rhein-Test war bei
# 258 m ueber Wasser alles gruen, bei 287 m gab es noch einzelne weisse
# Flaechen. Ab dieser Hoehe warnt der Dialog.
WARN_HEIGHT_ABOVE_WATER_M = 270.0

# Beim Gefaelle-Ausgleich zaehlen nur Gewaesser bis zu dieser Hoehe ueber dem
# gewaehlten Wasserspiegel als Bezug. Der Rhein hat im Mittelrhein-Abschnitt
# rund 15-20 m Gefaelle; Nebenfluesse und Bergseen (Eifel, Westerwald) liegen
# deutlich hoeher und wuerden ihre Taeler sonst unter Wasser druecken.
DEFAULT_SLOPE_MAX_REF_M = 30.0

# "Wasser nur dort, wo OSM Wasser hat": Boeschungsbreite, Wassertiefe, Hoehe des
# Ufers ueber dem Wasserspiegel und Hoehengrenze fuer Gewaesser, die angepasst
# werden (hoeher gelegene Baeche/Bergseen bleiben unangetastet).
DEFAULT_ENFORCE_TRANSITION_M = 60.0
# Trassen/Siedlungen einebnen: Breite der Glaettung (Sigma)
DEFAULT_FLATTEN_SIGMA_M = 60.0

DEFAULT_ENFORCE_DEPTH_M = 8.0     # Tiefe in der Flussmitte (Fahrrinne)
DEFAULT_ENFORCE_EDGE_M = 2.0      # Tiefe direkt am Ufer
DEFAULT_ENFORCE_BANK_M = 2.0
DEFAULT_ENFORCE_MAX_RISE_M = 15.0

# Als Bezug fuer den Gefaelle-Ausgleich zaehlen Seen/Wasserflaechen sowie
# diese Wasserwege - Baeche und Graeben bewusst nicht: sie liegen oft weit
# ueber dem Talfluss und wuerden ihre Umgebung sonst unnatuerlich absenken.
REFERENCE_WATERWAY_TYPES = frozenset({"river", "canal"})


class HeightmapDialog(QDialog):
    """
    Laedt automatisch die Copernicus-Hoehendaten fuer die aktuelle
    (ggf. gedrehte) Selection, zeigt eine Vorschau mit Wasserflaeche wie
    im TPF2-Importfenster, und exportiert die fertige 16-Bit-PNG.
    """

    def __init__(self, parent, selection, project=None, osm=None):
        super().__init__(parent)

        self.selection = selection
        self.project = project
        self.osm = osm
        self.heightmap_array = None
        self.suggestion = None
        self._water_mask = None
        self._reference_mask = None
        self._flatten_mask = None
        self._processed_key = None
        self._processed_array = None
        self._processed_suggestion = None
        self._downloaded_once = False
        self._applying_preset = False

        self.setWindowTitle("Heightmap")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # Download
        # -------------------------------------------------

        self.status_label = QLabel(
            "Noch nicht geladen."
        )
        layout.addWidget(self.status_label)

        self.quick_preview_button = QPushButton(
            "Schnellvorschau (niedrige Auflösung, vor dem echten Download)"
        )
        self.quick_preview_button.clicked.connect(
            self._quick_preview
        )
        layout.addWidget(self.quick_preview_button)

        self.download_button = QPushButton(
            "Höhendaten herunterladen"
        )
        self.download_button.clicked.connect(
            self._download
        )
        layout.addWidget(self.download_button)

        # -------------------------------------------------
        # Voreinstellungen (setzen die Haken mit einem Klick)
        # -------------------------------------------------

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Voreinstellung:"))

        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Eigene Einstellungen",
            "Original (1:1, unverändert)",
            "Empfohlen (Glätten, Einebnen, Wasser nach OSM)",
        ])
        self.preset_combo.setEnabled(False)
        self.preset_combo.setToolTip(
            "Original: alle Optionen aus, die echten Höhen. Empfohlen: "
            "Gelände glätten, Trassen und Siedlungen einebnen und Wasser "
            "nur dort, wo OpenStreetMap Wasser hat, jeweils mit den "
            "Standardwerten. Optionen, die OSM-Daten brauchen, bleiben "
            "ohne geladene OSM-Daten aus."
        )
        self.preset_combo.currentIndexChanged.connect(
            self._on_preset_changed
        )
        preset_row.addWidget(self.preset_combo, 1)

        layout.addLayout(preset_row)

        # -------------------------------------------------
        # Vorschau
        # -------------------------------------------------

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        layout.addWidget(self.preview_label)

        # -------------------------------------------------
        # Höhenbereich / Wasserhöhe
        # -------------------------------------------------

        form = QFormLayout()
        layout.addLayout(form)

        self.range_label = QLabel("–")
        form.addRow("Höhenbereich:", self.range_label)

        self.exclude_outliers_checkbox = QCheckBox(
            "Ausreißer aus Höhenbereich ausschließen (mehr Präzision "
            "fürs eigentliche Gelände)"
        )
        self.exclude_outliers_checkbox.setVisible(False)
        self.exclude_outliers_checkbox.toggled.connect(
            self._on_exclude_outliers_toggled
        )
        layout.addWidget(self.exclude_outliers_checkbox)

        self.water_level_input = QDoubleSpinBox()
        self.water_level_input.setRange(-500.0, 9000.0)
        self.water_level_input.setDecimals(0)
        self.water_level_input.setSuffix(" m")
        self.water_level_input.setEnabled(False)
        self.water_level_input.valueChanged.connect(
            self._update_preview
        )
        form.addRow("Wasserhöhe:", self.water_level_input)

        self.note_label = QLabel("")
        self.note_label.setWordWrap(True)
        layout.addWidget(self.note_label)

        # Wasserhoehe aus den OSM-Gewaessern: der Vorschlag oben (7,5.
        # Perzentil der ganzen Flaeche) passt schlecht zu Fluessen mit
        # Gefaelle. Hier wird die Mitte zwischen tiefstem und hoechstem
        # Punkt des Hauptflusses vorgeschlagen.
        self.suggest_water_button = QPushButton(
            "Wasserhöhe aus den OSM-Gewässern vorschlagen"
        )
        self.suggest_water_button.setEnabled(False)
        self.suggest_water_button.setToolTip(
            "Liest die Höhen des Hauptflusses (aus OpenStreetMap) und setzt "
            "die Wasserhöhe in die Mitte zwischen tiefstem und höchstem "
            "Punkt. So wird der Fluss an beiden Enden um etwa gleich viel "
            "korrigiert. Braucht geladene OSM-Daten."
        )
        self.suggest_water_button.clicked.connect(
            self._suggest_water_from_osm
        )
        layout.addWidget(self.suggest_water_button)

        self.water_hint_label = QLabel("")
        self.water_hint_label.setWordWrap(True)
        layout.addWidget(self.water_hint_label)

        # -------------------------------------------------
        # Gefaelle ausgleichen (Idee eines Community-Mitglieds: die
        # Karte "vertikal gerade richten", statt nur die Hoehe ue. NN
        # zu uebernehmen - siehe water_slope_compensation.py).
        # -------------------------------------------------

        self.smooth_checkbox = QCheckBox("Gelände glätten")
        self.smooth_checkbox.setToolTip(
            "Gegen Treppenstufen und Kristallflächen an Hängen: das "
            "Höhenmodell hat nur etwa 30 m pro Pixel, das Spiel 4 m."
        )
        self.smooth_checkbox.setEnabled(False)
        self.smooth_checkbox.toggled.connect(
            self._on_smooth_toggled
        )
        layout.addWidget(self.smooth_checkbox)

        smooth_row = QHBoxLayout()
        smooth_row.addWidget(QLabel("Glättung:"))
        self.smooth_sigma_input = QDoubleSpinBox()
        self.smooth_sigma_input.setRange(3.0, 200.0)
        self.smooth_sigma_input.setDecimals(0)
        self.smooth_sigma_input.setSuffix(" m")
        self.smooth_sigma_input.setValue(DEFAULT_SMOOTHING_SIGMA_M)
        self.smooth_sigma_input.setEnabled(False)
        self.smooth_sigma_input.setMinimumWidth(110)
        self.smooth_sigma_input.setKeyboardTracking(False)
        self.smooth_sigma_input.setToolTip(
            "Breite der Glättung. 15 m entfernt die gröbsten Stufen, "
            "30 m glättet stärker, flacht aber Gipfel und Kämme leicht ab."
        )
        self.smooth_sigma_input.valueChanged.connect(
            self._update_preview
        )
        smooth_row.addWidget(self.smooth_sigma_input)

        smooth_row.addWidget(QLabel("Höhen stauchen auf:"))
        self.compress_input = QDoubleSpinBox()
        self.compress_input.setRange(20.0, 100.0)
        self.compress_input.setDecimals(0)
        self.compress_input.setSuffix(" %")
        self.compress_input.setValue(100.0)
        self.compress_input.setEnabled(False)
        self.compress_input.setMinimumWidth(110)
        self.compress_input.setKeyboardTracking(False)
        self.compress_input.setToolTip(
            "Die höchste Stelle landet auf diesem Anteil ihrer Höhe über dem "
            "Wasserspiegel. 100 % = unverändert. Der untere Teil des "
            "Geländes bleibt unverändert (Talhänge behalten ihre Steilheit), "
            "erst darüber wird weich gestaucht. Hilft gegen weiße und graue "
            "Flächen auf Hochflächen: Das Spiel färbt nach der Höhe über "
            "dem Wasser."
        )
        self.compress_input.valueChanged.connect(
            self._update_preview
        )
        smooth_row.addWidget(self.compress_input)

        smooth_row.addStretch(1)
        layout.addLayout(smooth_row)

        self.flatten_checkbox = QCheckBox("Trassen und Siedlungen einebnen")
        self.flatten_checkbox.setToolTip(
            "Bahnstrecken, größere Straßen und Gebäude aus OpenStreetMap: "
            "das Gelände dort wird abgeflacht, damit im Spiel weniger "
            "Rampen nötig sind. Braucht geladene OSM-Daten."
        )
        self.flatten_checkbox.setEnabled(False)
        self.flatten_checkbox.toggled.connect(
            self._on_flatten_toggled
        )
        layout.addWidget(self.flatten_checkbox)

        flatten_row = QHBoxLayout()
        flatten_row.addWidget(QLabel("Glättung:"))
        self.flatten_sigma_input = QDoubleSpinBox()
        self.flatten_sigma_input.setRange(10.0, 300.0)
        self.flatten_sigma_input.setDecimals(0)
        self.flatten_sigma_input.setSuffix(" m")
        self.flatten_sigma_input.setValue(DEFAULT_FLATTEN_SIGMA_M)
        self.flatten_sigma_input.setEnabled(False)
        self.flatten_sigma_input.setMinimumWidth(110)
        self.flatten_sigma_input.setKeyboardTracking(False)
        self.flatten_sigma_input.setToolTip(
            "Je größer, desto ebener wird das Gelände entlang der Trassen "
            "und in den Ortschaften. Einschnitte und Dämme verschwinden."
        )
        self.flatten_sigma_input.valueChanged.connect(
            self._update_preview
        )
        flatten_row.addWidget(self.flatten_sigma_input)
        flatten_row.addStretch(1)
        layout.addLayout(flatten_row)

        self.slope_checkbox = QCheckBox("Gefälle ausgleichen")
        self.slope_checkbox.setToolTip(
            "Legt Flüsse und Seen auf eine gemeinsame Ebene und zieht das "
            "Gelände relativ dazu mit. Das Relief über dem jeweiligen "
            "Wasserspiegel bleibt erhalten, die absoluten Höhen ü. NN "
            "stimmen danach aber nicht mehr."
        )
        self.slope_checkbox.setEnabled(False)
        self.slope_checkbox.toggled.connect(
            self._on_slope_toggled
        )
        layout.addWidget(self.slope_checkbox)

        slope_row = QHBoxLayout()

        slope_row.addWidget(QLabel("Stärke:"))
        self.slope_strength_input = QDoubleSpinBox()
        self.slope_strength_input.setMinimumWidth(100)
        self.slope_strength_input.setRange(0.0, 100.0)
        self.slope_strength_input.setDecimals(0)
        self.slope_strength_input.setSuffix(" %")
        self.slope_strength_input.setValue(100.0)
        self.slope_strength_input.setEnabled(False)
        # Erst nach Enter/Fokuswechsel neu rechnen, nicht bei jeder Ziffer.
        self.slope_strength_input.setKeyboardTracking(False)
        self.slope_strength_input.valueChanged.connect(
            self._update_preview
        )
        slope_row.addWidget(self.slope_strength_input)

        slope_row.addWidget(QLabel("Glättung:"))
        self.slope_smoothing_input = QDoubleSpinBox()
        self.slope_smoothing_input.setMinimumWidth(110)
        self.slope_smoothing_input.setRange(50.0, 5000.0)
        self.slope_smoothing_input.setDecimals(0)
        self.slope_smoothing_input.setSuffix(" m")
        self.slope_smoothing_input.setValue(DEFAULT_SMOOTHING_M)
        self.slope_smoothing_input.setEnabled(False)
        self.slope_smoothing_input.setKeyboardTracking(False)
        self.slope_smoothing_input.valueChanged.connect(
            self._update_preview
        )
        slope_row.addWidget(self.slope_smoothing_input)

        slope_row.addWidget(QLabel("Bezug: Gewässer bis"))
        self.slope_max_ref_input = QDoubleSpinBox()
        self.slope_max_ref_input.setRange(1.0, 1000.0)
        self.slope_max_ref_input.setDecimals(0)
        self.slope_max_ref_input.setSuffix(" m über Wasserspiegel")
        self.slope_max_ref_input.setMinimumWidth(250)
        self.slope_max_ref_input.setValue(DEFAULT_SLOPE_MAX_REF_M)
        self.slope_max_ref_input.setEnabled(False)
        self.slope_max_ref_input.setKeyboardTracking(False)
        self.slope_max_ref_input.setToolTip(
            "Nur Gewässer, die höchstens so hoch über dem Wasserspiegel "
            "liegen, dienen als Bezug. Höher gelegene Nebenflüsse und "
            "Bergseen werden ignoriert, sonst würde ihr Tal überflutet."
        )
        self.slope_max_ref_input.valueChanged.connect(
            self._update_preview
        )
        slope_row.addWidget(self.slope_max_ref_input)

        layout.addLayout(slope_row)

        self.slope_note_label = QLabel("")
        self.slope_note_label.setWordWrap(True)
        layout.addWidget(self.slope_note_label)

        # -------------------------------------------------
        # Terrain ans Wasserniveau anpassen (Idee eines
        # Community-Mitglieds: TPF2/TPF3 kennen kein Wassergefaelle,
        # ohne Anpassung fallen Fluesse/Seen bei echten Hoehendaten
        # sonst oft "trocken").
        # -------------------------------------------------

        self.enforce_checkbox = QCheckBox(
            "Wasser nur dort, wo OpenStreetMap Wasser hat (empfohlen)"
        )
        self.enforce_checkbox.setToolTip(
            "Gewässer bekommen ein festes Bett, alles andere Land liegt "
            "knapp über dem Wasserspiegel: keine überfluteten Auen und "
            "Tümpel. Ersetzt die sanfte Anpassung unten."
        )
        self.enforce_checkbox.setEnabled(False)
        self.enforce_checkbox.toggled.connect(
            self._on_enforce_toggled
        )
        layout.addWidget(self.enforce_checkbox)

        # Zwei Zeilen, damit die Felder auch in einem schmalen Fenster
        # vollstaendig lesbar bleiben.
        enforce_row = QHBoxLayout()
        enforce_row2 = QHBoxLayout()

        def _enforce_spin(
            label, value, low, high, decimals, suffix, tip,
            row=None, min_width=100,
        ):
            target = row if row is not None else enforce_row
            target.addWidget(QLabel(label))
            spin = QDoubleSpinBox()
            spin.setMinimumWidth(min_width)
            spin.setRange(low, high)
            spin.setDecimals(decimals)
            spin.setSuffix(suffix)
            spin.setValue(value)
            spin.setEnabled(False)
            spin.setKeyboardTracking(False)
            spin.setToolTip(tip)
            spin.valueChanged.connect(self._update_preview)
            target.addWidget(spin)
            return spin

        self.enforce_transition_input = _enforce_spin(
            "Böschung:", DEFAULT_ENFORCE_TRANSITION_M, 10.0, 300.0, 0, " m",
            "Breite der Böschung zwischen Flussbett und Land. Breiter = "
            "flacheres Ufer, aber auch etwas breiteres Wasser."
        )
        self.enforce_edge_input = _enforce_spin(
            "Tiefe am Ufer:", DEFAULT_ENFORCE_EDGE_M, 0.5, 10.0, 1, " m",
            "Tiefe des Flussbetts direkt am Ufer. Zur Mitte hin wird es "
            "tiefer (Fahrrinne), das ergibt einen natürlichen Querschnitt."
        )
        self.enforce_depth_input = _enforce_spin(
            "Tiefe in der Mitte:", DEFAULT_ENFORCE_DEPTH_M, 1.0, 30.0, 0, " m",
            "Tiefe des Flussbetts unter dem Wasserspiegel."
        )
        self.enforce_bank_input = _enforce_spin(
            "Ufer über Wasser:", DEFAULT_ENFORCE_BANK_M, 0.5, 10.0, 1, " m",
            "So hoch liegt Land am Ufer mindestens über dem Wasserspiegel. "
            "Alles darunter wird angehoben und kann nicht überflutet werden.",
            row=enforce_row2,
        )
        self.enforce_max_rise_input = _enforce_spin(
            "Nur Gewässer bis", DEFAULT_ENFORCE_MAX_RISE_M, 1.0, 500.0, 0,
            " m über Wasserspiegel",
            "Gewässer, die von Natur aus höher liegen (Bäche in den "
            "Bergen, Bergseen), bleiben unverändert.",
            row=enforce_row2,
            min_width=250,
        )

        enforce_row.addStretch(1)
        enforce_row2.addStretch(1)

        layout.addLayout(enforce_row)
        layout.addLayout(enforce_row2)

        self.water_blend_checkbox = QCheckBox(
            "Terrain sanft ans Wasserniveau anpassen"
        )
        self.water_blend_checkbox.setToolTip(
            "Verhindert trockenfallende Flüsse und Seen, weicht dafür "
            "geringfügig von den echten Höhendaten ab. Sehr kleine "
            "Einzelgewässer werden ausgenommen, um Krater zu vermeiden. "
            "Das Gelände unterhalb des Wasserspiegels wird zusätzlich "
            "weichgezeichnet."
        )
        self.water_blend_checkbox.setEnabled(False)
        self.water_blend_checkbox.toggled.connect(
            self._on_water_blend_toggled
        )
        layout.addWidget(self.water_blend_checkbox)

        transition_row = QHBoxLayout()
        transition_row.addWidget(QLabel("Übergangsbreite:"))
        self.transition_input = QDoubleSpinBox()
        self.transition_input.setRange(4.0, 500.0)
        self.transition_input.setDecimals(0)
        self.transition_input.setSuffix(" m")
        self.transition_input.setValue(DEFAULT_TRANSITION_M)
        self.transition_input.setEnabled(False)
        self.transition_input.valueChanged.connect(
            self._update_preview
        )
        transition_row.addWidget(self.transition_input)

        transition_row.addWidget(QLabel("Nur Gewässer bis"))
        self.blend_max_rise_input = QDoubleSpinBox()
        self.blend_max_rise_input.setRange(1.0, 500.0)
        self.blend_max_rise_input.setDecimals(0)
        self.blend_max_rise_input.setSuffix(" m über Wasserspiegel")
        self.blend_max_rise_input.setMinimumWidth(250)
        self.blend_max_rise_input.setValue(DEFAULT_BLEND_MAX_RISE_M)
        self.blend_max_rise_input.setEnabled(False)
        self.blend_max_rise_input.setKeyboardTracking(False)
        self.blend_max_rise_input.setToolTip(
            "Gewässer, die von Natur aus höher liegen (Bäche in den Bergen, "
            "Bergseen), bleiben unverändert und werden nicht zu Schluchten."
        )
        self.blend_max_rise_input.valueChanged.connect(
            self._update_preview
        )
        transition_row.addWidget(self.blend_max_rise_input)

        layout.addLayout(transition_row)

        self.water_blend_note_label = QLabel("")
        self.water_blend_note_label.setWordWrap(True)
        layout.addWidget(self.water_blend_note_label)

        # -------------------------------------------------
        # Werte fuer den TPF3-Import (immer passend zum Export)
        # -------------------------------------------------

        self.relative_values_checkbox = QCheckBox(
            "Werte auf Wasserhöhe 0 beziehen"
        )
        self.relative_values_checkbox.setToolTip(
            "Empfehlung des TPF3-Wikis für Biome und Materialien. Die "
            "Mindesthöhe kann dabei negativ werden."
        )
        self.relative_values_checkbox.toggled.connect(
            self._on_relative_values_toggled
        )
        layout.addWidget(self.relative_values_checkbox)

        self.game_values_label = QLabel("")
        self.game_values_label.setWordWrap(True)
        self.game_values_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )
        layout.addWidget(self.game_values_label)

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        button_row = QHBoxLayout()
        layout.addLayout(button_row)

        # Anleitung: Schritt fuer Schritt von der Auswahl bis zum Import
        # im Spiel (auch ueber F1 erreichbar).
        self.guide_button = QPushButton("Anleitung (F1)")
        self.guide_button.clicked.connect(self._open_guide)
        button_row.addWidget(self.guide_button)

        QShortcut(
            QKeySequence("F1"),
            self,
            activated=self._open_guide,
        )

        self._connect_custom_markers()

        self.export_button = QPushButton(
            "Exportieren..."
        )
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(
            self._export
        )
        button_row.addWidget(self.export_button)

        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.reject)
        button_row.addWidget(close_button)

    # ---------------------------------------------------------
    # Anleitung
    # ---------------------------------------------------------

    def _open_guide(self):

        HeightmapGuideDialog(self).exec()

    # ---------------------------------------------------------
    # Download
    # ---------------------------------------------------------

    def _download(self):

        self.status_label.setText(
            "Lade Höhendaten... (kann je nach Kartengröße etwas dauern)"
        )
        self.download_button.setEnabled(False)
        # Sorgt dafuer, dass der Text vor dem (blockierenden) Download
        # tatsaechlich schon sichtbar ist.
        self.repaint()

        try:
            self.heightmap_array = build_heightmap_array(
                self.selection,
                DEFAULT_CACHE_DIR,
            )
        except Exception as exc:
            self.status_label.setText(
                f"Fehlgeschlagen: {exc}"
            )
            self.download_button.setEnabled(True)
            return

        self.suggestion = suggest_water_level(
            self.heightmap_array
        )

        self._water_mask = None  # neuer Download -> alte Maske verwerfen
        self._reference_mask = None
        self._flatten_mask = None
        self._reset_processed_cache()

        has_water_data = (
            self.osm is not None
            and (self.osm.node_count > 0 or self.osm.way_count > 0)
        )

        # Die Einstellungen (Haken, Staerke, Glaettung, Uebergangsbreite)
        # bleiben nach dem Download erhalten - sie wurden frueher hier
        # zurueckgesetzt, dadurch zeigte der volle Download wieder das
        # unbearbeitete Original.
        self.water_blend_checkbox.blockSignals(True)
        self.slope_checkbox.blockSignals(True)

        self.water_blend_checkbox.setEnabled(has_water_data)
        self.slope_checkbox.setEnabled(has_water_data)

        if not has_water_data:
            self.water_blend_checkbox.setChecked(False)
            self.slope_checkbox.setChecked(False)

        self.water_blend_checkbox.blockSignals(False)
        self.slope_checkbox.blockSignals(False)

        self.flatten_checkbox.blockSignals(True)
        self.flatten_checkbox.setEnabled(has_water_data)

        if not has_water_data:
            self.flatten_checkbox.setChecked(False)

        self.flatten_checkbox.blockSignals(False)

        self.flatten_sigma_input.setEnabled(self.flatten_checkbox.isChecked())

        self.preset_combo.setEnabled(True)
        self.suggest_water_button.setEnabled(has_water_data)

        self.smooth_checkbox.setEnabled(True)
        self.smooth_sigma_input.setEnabled(self.smooth_checkbox.isChecked())
        self.compress_input.setEnabled(True)

        self.enforce_checkbox.blockSignals(True)
        self.enforce_checkbox.setEnabled(has_water_data)

        if not has_water_data:
            self.enforce_checkbox.setChecked(False)

        self.enforce_checkbox.blockSignals(False)

        enforce_on = self.enforce_checkbox.isChecked()

        for widget in self._enforce_inputs():
            widget.setEnabled(enforce_on)

        # Die sanfte Anpassung ist nicht zusammen mit "Wasser nur dort, wo
        # OSM Wasser hat" verwendbar.
        if enforce_on:
            self.water_blend_checkbox.blockSignals(True)
            self.water_blend_checkbox.setChecked(False)
            self.water_blend_checkbox.setEnabled(False)
            self.water_blend_checkbox.blockSignals(False)

        blend_on = self.water_blend_checkbox.isChecked()
        slope_on = self.slope_checkbox.isChecked()

        self.transition_input.setEnabled(blend_on)
        self.blend_max_rise_input.setEnabled(blend_on)
        self.slope_strength_input.setEnabled(slope_on)
        self.slope_smoothing_input.setEnabled(slope_on)
        self.slope_max_ref_input.setEnabled(slope_on)

        if not has_water_data:
            self.water_blend_note_label.setText(
                "Keine OSM-Daten geladen - für die Terrain-Anpassung "
                "werden die Wasserflächen aus 'OSM laden' benötigt."
            )
            self.slope_note_label.setText(
                "Keine OSM-Daten geladen - der Gefälle-Ausgleich "
                "braucht die Gewässer aus 'OSM laden'."
            )
        else:
            self.water_blend_note_label.setText("")
            self.slope_note_label.setText("")

        if self.suggestion.outlier_count > 0:

            self.exclude_outliers_checkbox.setText(
                f"Ausreißer aus Höhenbereich ausschließen "
                f"({self.suggestion.outlier_count} Pixel, "
                f"{self.suggestion.outlier_fraction * 100:.2f}% der Fläche "
                f"erkannt)"
            )
            self.exclude_outliers_checkbox.setVisible(True)
            self.exclude_outliers_checkbox.setChecked(False)

        else:

            self.exclude_outliers_checkbox.setVisible(False)
            self.exclude_outliers_checkbox.setChecked(False)

        self._update_range_label()

        self.water_level_input.setEnabled(True)

        # Den Vorschlag nur beim ersten Download uebernehmen - eine vom
        # Nutzer angepasste Wasserhoehe bleibt bei erneutem Laden erhalten.
        if not self._downloaded_once:

            self.water_level_input.blockSignals(True)
            self.water_level_input.setValue(
                self.suggestion.suggested_m
            )
            self.water_level_input.blockSignals(False)

        self._downloaded_once = True

        self.note_label.setText(
            self.suggestion.note
        )

        self.status_label.setText(
            f"Geladen: {self.heightmap_array.shape[1]} x "
            f"{self.heightmap_array.shape[0]} Pixel"
        )

        self.export_button.setEnabled(True)
        self.download_button.setEnabled(True)

        self._update_preview()

    # ---------------------------------------------------------
    # Schnellvorschau (vor dem eigentlichen Download)
    # ---------------------------------------------------------

    def _quick_preview(self):
        """
        Laedt dieselben Copernicus-Kacheln wie der echte Download, tastet
        das Band aber nur grob ab (siehe build_heightmap_array_preview) -
        damit laesst sich sofort pruefen, ob Mittelpunkt/Drehung/Form
        stimmen, ohne auf die volle Aufloesung zu warten. Die Kacheln
        landen dabei im Cache, der anschliessende echte Download laedt
        dann nichts mehr neu herunter.

        Beeinflusst bewusst NICHT self.heightmap_array/self.suggestion -
        die Schnellvorschau ersetzt nicht den fuer den Export noetigen
        vollaufloesenden Download.
        """

        self.status_label.setText(
            "Lade Schnellvorschau..."
        )
        self.quick_preview_button.setEnabled(False)
        self.download_button.setEnabled(False)
        self.repaint()

        try:
            preview_array = build_heightmap_array_preview(
                self.selection,
                DEFAULT_CACHE_DIR,
            )
        except Exception as exc:
            self.status_label.setText(
                f"Schnellvorschau fehlgeschlagen: {exc}"
            )
            self.quick_preview_button.setEnabled(True)
            self.download_button.setEnabled(True)
            return

        quick_suggestion = suggest_water_level(preview_array)

        image = render_preview(
            preview_array,
            water_level_m=quick_suggestion.suggested_m,
            range_min_m=quick_suggestion.range_min_m,
            range_max_m=quick_suggestion.range_max_m,
            pixel_size_m=(
                self.selection.width_m / preview_array.shape[1]
            ),
        )

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())

        self.preview_label.setPixmap(
            pixmap.scaledToHeight(400, Qt.SmoothTransformation)
        )

        self.status_label.setText(
            f"Schnellvorschau ({preview_array.shape[1]} x "
            f"{preview_array.shape[0]} Pixel, niedrige Auflösung - "
            f"noch nicht exportierbar). Sieht das plausibel aus? Dann "
            f"jetzt 'Höhendaten herunterladen' für die volle Auflösung."
        )

        self.quick_preview_button.setEnabled(True)
        self.download_button.setEnabled(True)

    # ---------------------------------------------------------
    # Höhenbereich (mit/ohne Ausreißer)
    # ---------------------------------------------------------

    def _effective_range(self) -> tuple[float, float]:
        """
        Der tatsaechlich fuer Vorschau/Export verwendete Hoehenbereich -
        voller Bereich (Standard, nichts geht verloren) oder die engere,
        ausreisserbereinigte Spanne, falls der Nutzer das explizit
        angehakt hat.
        """

        # Bei aktivem Gefaelle-Ausgleich verschieben sich die Hoehen
        # (Gelaende wird relativ zum Wasser abgesenkt/angehoben) - der
        # Bereich muss dann aus dem tatsaechlich exportierten Raster
        # stammen, sonst wuerde beim Export abgeschnitten.
        suggestion = self._active_suggestion()

        if (
            suggestion is not None
            and self.exclude_outliers_checkbox.isChecked()
        ):
            return (
                suggestion.robust_range_min_m,
                suggestion.robust_range_max_m,
            )

        return suggestion.range_min_m, suggestion.range_max_m

    def _update_range_label(self):

        range_min, range_max = self._effective_range()

        self.range_label.setText(
            f"{range_min:.0f} – {range_max:.0f} m"
        )

    def _on_exclude_outliers_toggled(self):

        self._update_range_label()
        self._update_preview()

    # ---------------------------------------------------------
    # Gefälle ausgleichen
    # ---------------------------------------------------------

    def _on_slope_toggled(self, checked: bool):

        self.slope_strength_input.setEnabled(checked)
        self.slope_smoothing_input.setEnabled(checked)
        self.slope_max_ref_input.setEnabled(checked)

        if not checked:

            self.slope_note_label.setText("")
            self._update_preview()
            return

        try:
            reference_mask = self._get_reference_mask()
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Wassermaske fehlgeschlagen",
                str(exc),
            )
            self.slope_checkbox.setChecked(False)
            return

        if not reference_mask.any():

            self.slope_note_label.setText(
                "In diesem Kartenausschnitt wurden keine Seen oder "
                "größeren Flüsse als Bezug gefunden - der "
                "Gefälle-Ausgleich hat hier keine Wirkung."
            )

        else:

            self.slope_note_label.setText(
                "Als Bezug dienen Seen und Wasserflächen sowie Flüsse "
                "und Kanäle bis zur eingestellten Höhe über dem "
                "Wasserspiegel; Bäche, Gräben und höher gelegene "
                "Gewässer zählen dafür nicht."
            )

        self._update_preview()

    def _get_reference_mask(self):
        """
        Wassermaske nur aus Bezugsgewaessern (Seen/Wasserflaechen, Fluesse,
        Kanaele) - gecacht, bei neuem Download verworfen.
        """

        if self._reference_mask is None:

            QApplication.setOverrideCursor(Qt.WaitCursor)

            try:

                h_px, w_px = self.heightmap_array.shape

                self._reference_mask = build_water_mask(
                    self.osm,
                    self.selection,
                    w_px,
                    h_px,
                    waterway_types=REFERENCE_WATERWAY_TYPES,
                )

            finally:
                QApplication.restoreOverrideCursor()

        return self._reference_mask

    # ---------------------------------------------------------
    # Terrain-Wasser-Anpassung
    # ---------------------------------------------------------

    def _on_flatten_toggled(self, checked: bool):

        self.flatten_sigma_input.setEnabled(checked)

        self._update_preview()

    def _get_flatten_mask(self):
        """
        Maske der Flaechen, die eingeebnet werden (Bahn, groessere Strassen,
        Gebaeude mit Umgriff). Gecacht, bei neuem Download verworfen.
        """

        if self._flatten_mask is None:

            h_px, w_px = self.heightmap_array.shape

            self._flatten_mask = build_infrastructure_mask(
                self.osm,
                self.selection,
                w_px,
                h_px,
                self._pixel_size_m(),
            )

        return self._flatten_mask

    # ---------------------------------------------------------
    # Voreinstellungen
    # ---------------------------------------------------------

    def _connect_custom_markers(self):
        """
        Jede manuelle Aenderung setzt die Voreinstellung auf "Eigene
        Einstellungen" zurueck.
        """

        boxes = (
            self.smooth_checkbox,
            self.flatten_checkbox,
            self.slope_checkbox,
            self.enforce_checkbox,
            self.water_blend_checkbox,
        )

        spins = (
            self.smooth_sigma_input,
            self.compress_input,
            self.flatten_sigma_input,
            self.slope_strength_input,
            self.slope_smoothing_input,
            self.slope_max_ref_input,
            self.enforce_transition_input,
            self.enforce_edge_input,
            self.enforce_depth_input,
            self.enforce_bank_input,
            self.enforce_max_rise_input,
            self.transition_input,
            self.blend_max_rise_input,
        )

        for box in boxes:
            box.toggled.connect(self._on_manual_change)

        for spin in spins:
            spin.valueChanged.connect(self._on_manual_change)

    def _on_manual_change(self, *_):

        if self._applying_preset:
            return

        if self.preset_combo.currentIndex() != 0:

            self.preset_combo.blockSignals(True)
            self.preset_combo.setCurrentIndex(0)
            self.preset_combo.blockSignals(False)

    def _on_preset_changed(self, index: int):

        if index > 0:
            self._apply_preset(index)

    def _apply_preset(self, index: int):
        """
        1 = Original (alles aus), 2 = Empfohlen. Haken, die OSM-Daten
        brauchen, werden nur gesetzt, wenn sie verfuegbar sind.
        """

        if self.heightmap_array is None:
            return

        wanted_on = {
            1: (),
            2: (
                self.smooth_checkbox,
                self.flatten_checkbox,
                self.enforce_checkbox,
            ),
        }[index]

        boxes = (
            self.smooth_checkbox,
            self.flatten_checkbox,
            self.slope_checkbox,
            self.enforce_checkbox,
            self.water_blend_checkbox,
        )

        self._applying_preset = True

        try:

            # Standardwerte, damit eine Voreinstellung reproduzierbar ist
            self.smooth_sigma_input.setValue(DEFAULT_SMOOTHING_SIGMA_M)
            self.flatten_sigma_input.setValue(DEFAULT_FLATTEN_SIGMA_M)
            self.compress_input.setValue(100.0)
            self.enforce_transition_input.setValue(
                DEFAULT_ENFORCE_TRANSITION_M
            )
            self.enforce_edge_input.setValue(DEFAULT_ENFORCE_EDGE_M)
            self.enforce_depth_input.setValue(DEFAULT_ENFORCE_DEPTH_M)
            self.enforce_bank_input.setValue(DEFAULT_ENFORCE_BANK_M)
            self.enforce_max_rise_input.setValue(DEFAULT_ENFORCE_MAX_RISE_M)

            # erst alles aus, dann die gewuenschten an
            for box in boxes:
                box.setChecked(False)

            for box in wanted_on:
                if box.isEnabled():
                    box.setChecked(True)

        finally:

            self._applying_preset = False

        self._update_preview()

    def _suggest_water_from_osm(self):
        """
        Setzt die Wasserhoehe in die Mitte zwischen tiefstem und hoechstem
        Punkt des Hauptflusses (Gewaesser aus OSM). Hoch gelegene Nebenfluesse
        und Bergseen bleiben aussen vor (mehr als 40 m ueber dem tiefsten
        Gewaesser). Passt bei Bedarf die Grenze "Nur Gewaesser bis" an, damit
        auch das obere Ende des Flusses noch erfasst wird.
        """

        import math

        import numpy as np

        if self.heightmap_array is None or self.osm is None:
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            mask = self._get_water_mask()
        except Exception as exc:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Wassermaske fehlgeschlagen", str(exc))
            return

        QApplication.restoreOverrideCursor()

        if not mask.any():

            QMessageBox.information(
                self,
                "Keine Gewässer",
                "In diesem Kartenausschnitt wurden keine Wasserflächen oder "
                "-wege gefunden. Zuerst OSM-Daten laden "
                "(Werkzeuge → OSM laden).",
            )

            return

        heights = self.heightmap_array[mask]

        low = float(np.percentile(heights, 2))

        main = heights[heights <= low + 40.0]

        river_low, river_high = (
            float(value) for value in np.percentile(main, [2, 98])
        )

        middle = float(round((river_low + river_high) / 2))

        # Die Hoehen aus dem Hoehenmodell sind die Wasseroberflaeche des
        # Flusses. Sie wird auf die Wasserhoehe gelegt: das obere Ende sinkt,
        # das untere steigt.
        lowered = max(0.0, river_high - middle)
        raised = max(0.0, middle - river_low)

        needed_rise = math.ceil(max(0.0, river_high - middle)) + 3

        raised_threshold = False

        self._applying_preset = True

        try:

            self.water_level_input.setValue(middle)

            if self.enforce_max_rise_input.value() < needed_rise:
                self.enforce_max_rise_input.setValue(needed_rise)
                raised_threshold = True

        finally:

            self._applying_preset = False

        text = (
            f"Hauptfluss liegt zwischen {river_low:.0f} und "
            f"{river_high:.0f} m. Wasserhöhe auf {middle:.0f} m gesetzt "
            f"(Mitte). Die Wasseroberfläche wird am oberen Ende um bis zu "
            f"{lowered:.0f} m abgesenkt und am unteren um bis zu "
            f"{raised:.0f} m angehoben."
        )

        if raised_threshold:
            text += (
                f" Die Grenze „Nur Gewässer bis“ wurde auf "
                f"{needed_rise} m erhöht."
            )

        self.water_hint_label.setText(text)

        self._update_preview()

    def _on_relative_values_toggled(self, checked: bool):

        # Nur den Text neu schreiben, nichts neu berechnen.
        if self.heightmap_array is not None:
            self.game_values_label.setText(self._game_values_text())

    def _on_smooth_toggled(self, checked: bool):

        self.smooth_sigma_input.setEnabled(checked)

        self._update_preview()

    def _enforce_inputs(self):

        return (
            self.enforce_transition_input,
            self.enforce_edge_input,
            self.enforce_depth_input,
            self.enforce_bank_input,
            self.enforce_max_rise_input,
        )

    def _on_enforce_toggled(self, checked: bool):

        for widget in self._enforce_inputs():
            widget.setEnabled(checked)

        # Sanfte Anpassung und "Wasser nur dort, wo OSM Wasser hat" schliessen
        # sich aus - beide veraendern das Gelaende um Gewaesser herum.
        if checked:

            self.water_blend_checkbox.blockSignals(True)
            self.water_blend_checkbox.setChecked(False)
            self.water_blend_checkbox.blockSignals(False)

            self.transition_input.setEnabled(False)
            self.blend_max_rise_input.setEnabled(False)

        self.water_blend_checkbox.setEnabled(
            not checked and self.enforce_checkbox.isEnabled()
        )

        if checked:

            try:
                water_mask = self._get_water_mask()
            except Exception as exc:
                QMessageBox.critical(
                    self,
                    "Wassermaske fehlgeschlagen",
                    str(exc),
                )
                self.enforce_checkbox.setChecked(False)
                return

            if not water_mask.any():

                QMessageBox.information(
                    self,
                    "Keine Gewässer",
                    "In diesem Kartenausschnitt wurden keine Wasserflächen "
                    "oder -wege gefunden - die Einstellung hat keine "
                    "Wirkung. Zuerst OSM-Daten laden (Werkzeuge → OSM laden).",
                )

        self._update_preview()

    def _on_water_blend_toggled(self, checked: bool):

        self.transition_input.setEnabled(checked)
        self.blend_max_rise_input.setEnabled(checked)

        if checked:

            try:
                water_mask = self._get_water_mask()
            except Exception as exc:
                QMessageBox.critical(
                    self,
                    "Wassermaske fehlgeschlagen",
                    str(exc),
                )
                self.water_blend_checkbox.setChecked(False)
                return

            if not water_mask.any():

                self.water_blend_note_label.setText(
                    "In diesem Kartenausschnitt wurden keine "
                    "Wasserflächen/-wege gefunden - die Anpassung hat "
                    "hier keine Wirkung."
                )

            else:

                self.water_blend_note_label.setText("")

        self._update_preview()

    def _get_water_mask(self):
        """
        Wassermaske fuer die Terrain-Anpassung. Es zaehlen dieselben
        Bezugsgewaesser wie beim Gefaelle-Ausgleich (Seen/Wasserflaechen,
        Fluesse, Kanaele). Baeche und Graeben sind bewusst NICHT dabei:
        mit ihnen wurde jedes Seitental zu einer Schlucht abgesenkt.
        Gecacht, bei neuem Download verworfen (siehe _download()).
        """

        if self._water_mask is None:
            self._water_mask = self._get_reference_mask()

        return self._water_mask

    def _pixel_size_m(self) -> float:

        return self.selection.width_m / (self.heightmap_array.shape[1] - 1)

    def _processing_key(self):
        """
        Alle Einstellungen, die das verarbeitete Raster beeinflussen -
        aendert sich nichts davon, wird das bereits berechnete Ergebnis
        wiederverwendet (Vorschau UND Export rechnen sonst jeweils neu).
        """

        return (
            self.smooth_checkbox.isChecked(),
            self.smooth_sigma_input.value(),
            self.flatten_checkbox.isChecked(),
            self.flatten_sigma_input.value(),
            self.compress_input.value(),
            self.slope_checkbox.isChecked(),
            self.slope_strength_input.value(),
            self.slope_smoothing_input.value(),
            self.slope_max_ref_input.value(),
            self.water_blend_checkbox.isChecked(),
            self.transition_input.value(),
            self.blend_max_rise_input.value(),
            self.enforce_checkbox.isChecked(),
            self.enforce_transition_input.value(),
            self.enforce_edge_input.value(),
            self.enforce_depth_input.value(),
            self.enforce_bank_input.value(),
            self.enforce_max_rise_input.value(),
            self.water_level_input.value(),
        )

    def _reset_processed_cache(self):

        self._processed_key = None
        self._processed_array = None
        self._processed_suggestion = None

    def _effective_heightmap(self):
        """
        Liefert das Hoehenraster, das fuer Vorschau/Export tatsaechlich
        verwendet wird. Reihenfolge, wenn angehakt:

        1. Gefaelle ausgleichen (Gewaesser auf eine gemeinsame Ebene,
           Gelaende relativ dazu mit)
        2. Terrain sanft ans Wasserniveau anpassen (Ufer glaetten, raeumt
           kleine Restunterschiede aus Schritt 1 auf)

        Ohne Haekchen: das unveraenderte Original.
        """

        slope_on = self.slope_checkbox.isChecked()
        blend_on = self.water_blend_checkbox.isChecked()
        enforce_on = self.enforce_checkbox.isChecked()
        smooth_on = self.smooth_checkbox.isChecked()
        flatten_on = self.flatten_checkbox.isChecked()
        compress_on = self.compress_input.value() < 100.0

        if (
            not slope_on
            and not blend_on
            and not enforce_on
            and not smooth_on
            and not flatten_on
            and not compress_on
        ):
            return self.heightmap_array

        key = self._processing_key()

        if key == self._processed_key and self._processed_array is not None:
            return self._processed_array

        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:

            array = self.heightmap_array
            water_level = self.water_level_input.value()
            pixel_size = self._pixel_size_m()

            # 1. Glaetten (vor allen Wasserschritten, damit Flussbett und
            #    Ufer danach scharf bleiben)
            if smooth_on:

                array = smooth_terrain(
                    array,
                    self.smooth_sigma_input.value(),
                    pixel_size,
                )

            # 2. Trassen und Siedlungen einebnen (vor den Wasserschritten,
            #    damit Gewaesser anschliessend wieder ihr festes Bett bekommen)
            if flatten_on:

                array = flatten_infrastructure(
                    array,
                    self._get_flatten_mask(),
                    pixel_size,
                    sigma_m=self.flatten_sigma_input.value(),
                )

            if slope_on:

                array = compensate_water_slope(
                    array,
                    self._get_reference_mask(),
                    water_level_m=water_level,
                    pixel_size_m=pixel_size,
                    strength=self.slope_strength_input.value() / 100.0,
                    smoothing_m=self.slope_smoothing_input.value(),
                    max_reference_height_above_water_m=(
                        self.slope_max_ref_input.value()
                    ),
                )

            if enforce_on:

                array = enforce_osm_water(
                    array,
                    self._get_water_mask(),
                    water_level_m=water_level,
                    pixel_size_m=pixel_size,
                    transition_m=self.enforce_transition_input.value(),
                    bed_depth_m=self.enforce_depth_input.value(),
                    edge_depth_m=self.enforce_edge_input.value(),
                    bank_height_m=self.enforce_bank_input.value(),
                    max_height_above_water_m=(
                        self.enforce_max_rise_input.value()
                    ),
                )

            elif blend_on:

                array = blend_terrain_to_water(
                    array,
                    self._get_water_mask(),
                    water_level_m=water_level,
                    transition_m=self.transition_input.value(),
                    pixel_size_m=pixel_size,
                    max_height_above_water_m=(
                        self.blend_max_rise_input.value()
                    ),
                    # Gelaende unterhalb des Wasserspiegels wird mit der
                    # halben Uebergangsbreite weichgezeichnet.
                    underwater_smoothing_m=(
                        self.transition_input.value() / 2.0
                    ),
                )

            # Letzter Schritt: Hoehen ueber dem Wasserspiegel stauchen
            if compress_on:

                array = compress_heights(
                    array,
                    water_level,
                    self.compress_input.value() / 100.0,
                )

        finally:
            QApplication.restoreOverrideCursor()

        self._processed_array = array
        self._processed_key = key
        self._processed_suggestion = None

        return array

    def _active_suggestion(self):
        """
        Die Hoehenbereichs-/Ausreisser-Angaben passend zum tatsaechlich
        verwendeten Raster: das Original beim Normalfall, bei aktivem
        Gefaelle-Ausgleich eine frische Analyse des angepassten Rasters.
        """

        if (
            not self.slope_checkbox.isChecked()
            and not self.enforce_checkbox.isChecked()
            and not self.smooth_checkbox.isChecked()
            and not self.flatten_checkbox.isChecked()
            and self.compress_input.value() >= 100.0
        ):
            return self.suggestion

        array = self._effective_heightmap()

        if self._processed_suggestion is None:
            self._processed_suggestion = suggest_water_level(array)

        return self._processed_suggestion

    def _sync_outlier_checkbox(self, suggestion):
        """
        Haelt Text/Sichtbarkeit der Ausreisser-Checkbox passend zum
        gerade verwendeten Raster (blockSignals, damit das Umstellen
        keine weitere Neuberechnung ausloest).
        """

        checkbox = self.exclude_outliers_checkbox

        checkbox.blockSignals(True)

        if suggestion.outlier_count > 0:

            checkbox.setText(
                f"Ausreißer aus Höhenbereich ausschließen "
                f"({suggestion.outlier_count} Pixel, "
                f"{suggestion.outlier_fraction * 100:.2f}% der Fläche "
                f"erkannt)"
            )
            checkbox.setVisible(True)

        else:

            checkbox.setVisible(False)
            checkbox.setChecked(False)

        checkbox.blockSignals(False)

    # ---------------------------------------------------------
    # Werte fuer den TPF3-Import
    # ---------------------------------------------------------

    def _game_size_hint(self) -> str | None:
        """Kartengroesse/-format im Spiel, passend zur Pixelgroesse."""

        w_px, h_px = pixel_size_for_selection(self.selection)

        matches = find_by_pixels(w_px, h_px)

        if not matches:
            return None

        return " oder ".join(size.label for size in matches)

    def _game_values_text(self) -> str:
        """
        Was im TPF3-Heightmap-Import einzutragen ist. Das Spiel verteilt
        Schwarz..Weiss auf Mindest- bis Maximalhoehe.

        Standard: die echten Hoehen (positive Werte ueber NN), dazu die
        Wasserhoehe aus dem Dialog. Nur wenn der Haken "Werte auf
        Wasserhoehe 0 beziehen" gesetzt ist, werden alle Werte um die
        Wasserhoehe nach unten verschoben (laut TPF3-Wiki beste Ergebnisse
        bei Biomen und Materialien, kann aber negative Mindesthoehen geben).
        """

        range_min, range_max = self._effective_range()

        water = self.water_level_input.value()

        if self.relative_values_checkbox.isChecked():

            lines = [
                "Im TPF3-Import eintragen (auf Wasserhöhe 0 bezogen): "
                f"Mindesthöhe {range_min - water:.0f}, "
                f"Maximalhöhe {range_max - water:.0f}, Wasserhöhe 0",
            ]

        else:

            lines = [
                "Im TPF3-Import eintragen: "
                f"Mindesthöhe {range_min:.0f}, "
                f"Maximalhöhe {range_max:.0f}, "
                f"Wasserhöhe {water:.0f}",
            ]

        above_water = range_max - water

        if above_water > WARN_HEIGHT_ABOVE_WATER_M:

            lines.append(
                f"Achtung: Die höchste Stelle liegt {above_water:.0f} m über "
                f"dem Wasser. Im Spiel gibt es ab etwa 325-350 m Fels und ab "
                f"etwa 375-425 m Schnee (graue/weiße Flächen). Getestet: bei "
                f"258 m keine Flecken, bei 287 m einzelne weiße Flecken. "
                f"Abhilfe: \"Höhen stauchen auf\" verkleinern."
            )

        size_hint = self._game_size_hint()

        if size_hint:
            lines.append(f"Kartengröße und -format im Spiel: {size_hint}")

        return "\n".join(lines)

    # ---------------------------------------------------------
    # Vorschau
    # ---------------------------------------------------------

    def _update_preview(self):

        # Waehrend eine Voreinstellung die Haken setzt, nicht nach jedem
        # einzelnen Haken neu rechnen - am Ende einmal.
        if self._applying_preset:
            return

        if self.heightmap_array is None or self.suggestion is None:
            return

        array = self._effective_heightmap()

        self._sync_outlier_checkbox(self._active_suggestion())

        range_min, range_max = self._effective_range()

        self.range_label.setText(
            f"{range_min:.0f} – {range_max:.0f} m"
        )

        self.game_values_label.setText(self._game_values_text())

        image = render_preview(
            array,
            water_level_m=self.water_level_input.value(),
            range_min_m=range_min,
            range_max_m=range_max,
            pixel_size_m=self._pixel_size_m(),
        )

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())

        self.preview_label.setPixmap(
            pixmap.scaledToHeight(
                400,
                Qt.SmoothTransformation
            )
        )

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def _export(self):

        # Vorschlag: der heightmaps-Ordner von TPF3 (falls gefunden), damit
        # die Datei im Spiel sofort in der Liste erscheint.
        game_folder = find_tpf3_heightmaps_folder()

        default_name = (
            str(game_folder / "heightmap.png")
            if game_folder is not None
            else "heightmap.png"
        )

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Heightmap exportieren",
            default_name,
            "PNG-Bilder (*.png)"
        )

        if not filename:
            return

        range_min, range_max = self._effective_range()

        try:
            export_heightmap_png(
                self._effective_heightmap(),
                Path(filename),
                range_min_m=range_min,
                range_max_m=range_max,
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Export fehlgeschlagen",
                str(exc)
            )
            return

        if self.project is not None:
            self.project.mark_heightmap_exported(filename)

        outlier_warning = ""

        if self.exclude_outliers_checkbox.isChecked():

            outlier_warning = (
                f"\n\nHinweis: Die {self._active_suggestion().outlier_count} als "
                f"Ausreißer erkannten Pixel liegen außerhalb dieses "
                f"Bereichs und wurden dadurch auf den Rand geklemmt "
                f"(0 bzw. 65535) - deren echte Höhe geht im Export verloren."
            )

        slope_note = ""

        if self.slope_checkbox.isChecked():

            slope_note = (
                f"\n\nGefälle-Ausgleich aktiv (Stärke "
                f"{self.slope_strength_input.value():.0f} %, Glättung "
                f"{self.slope_smoothing_input.value():.0f} m): Flüsse und "
                f"Seen wurden auf eine gemeinsame Ebene gelegt, das "
                f"Gelände relativ dazu angepasst - die absoluten Höhen "
                f"ü. NN stimmen dadurch nicht mehr."
            )

        flatten_note = ""

        if self.flatten_checkbox.isChecked():

            flatten_note = (
                f"\n\nTrassen und Siedlungen eingeebnet "
                f"({self.flatten_sigma_input.value():.0f} m)."
            )

        compress_note = ""

        if self.compress_input.value() < 100.0:

            compress_note = (
                f"\n\nHöhen über dem Wasserspiegel auf "
                f"{self.compress_input.value():.0f} % gestaucht."
            )

        smooth_note = ""

        if self.smooth_checkbox.isChecked():

            smooth_note = (
                f"\n\nGelände geglättet ({self.smooth_sigma_input.value():.0f} m)."
            )

        enforce_note = ""

        if self.enforce_checkbox.isChecked():

            enforce_note = (
                f"\n\nWasser nur dort, wo OpenStreetMap Wasser hat: "
                f"Flussbett {self.enforce_edge_input.value():.0f} m (Ufer) bis "
                f"{self.enforce_depth_input.value():.0f} m (Mitte) unter "
                f"dem Wasserspiegel, Land mindestens "
                f"{self.enforce_bank_input.value():.1f} m darüber, Böschung "
                f"{self.enforce_transition_input.value():.0f} m."
            )

        water_blend_note = ""

        if self.water_blend_checkbox.isChecked():

            water_blend_note = (
                f"\n\nDas Terrain wurde um Gewässer herum (Übergang "
                f"{self.transition_input.value():.0f} m) sanft ans "
                f"Wasserniveau angepasst - weicht dort geringfügig von "
                f"den echten Höhendaten ab."
            )

        QMessageBox.information(
            self,
            "Export abgeschlossen",
            f"Heightmap gespeichert unter:\n{filename}\n\n"
            f"{self._game_values_text()}"
            f"{outlier_warning}"
            f"{smooth_note}"
            f"{flatten_note}"
            f"{compress_note}"
            f"{slope_note}"
            f"{enforce_note}"
            f"{water_blend_note}"
        )