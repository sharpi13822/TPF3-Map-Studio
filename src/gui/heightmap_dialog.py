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
    QSlider,
    QApplication,
    QAbstractSpinBox,
    QFrame,
    QScrollArea,
    QWidget,
)
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut
from PySide6.QtCore import QEvent, QObject, Qt

from src.i18n import tr
from src.gui.biome_dialog import BiomeMaskDialog
from src.gui.heightmap_guide import HeightmapGuideDialog
from src.gui.industries_dialog import IndustriesDialog
from src.heightmap.industries_export import Terrain
from src.gui.towns_dialog import TownsDialog
from src.gui.network_dialog import NetworkDialog
from src.gui.stations_action import save_stations_dialog
from src.gui.map_size_presets import find_by_pixels
from src.gui.dgm1_fetch_dialog import Dgm1FetchDialog
from src.heightmap.heightmap_exporter import (
    SOURCE_COPERNICUS,
    SOURCE_DGM1_DE,
    SOURCE_DGM1_FOLDER,
    SOURCE_SWISSALTI3D,
    build_heightmap_array,
    build_heightmap_array_ex,
    build_heightmap_array_preview,
    export_heightmap_png,
    pixel_size_for_selection,
)
from src.heightmap.height_hints import height_hint
from src.heightmap.height_clipping import (
    GAME_MAX_M,
    GAME_MIN_M,
    MIN_WINDOW_M,
    MODES,
    apply_height_window,
    default_window,
    describe_report,
    limit_warning,
    window_slider_range,
)
from src.heightmap.lv95 import SWISS_BOUNDS
from src.heightmap.swissalti3d_dem import SwissFetchJob
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
DEFAULT_DGM1_CACHE_DIR = Path.home() / ".tpf2_map_studio" / "dgm1_cache"
DEFAULT_SWISS_CACHE_DIR = Path.home() / ".tpf2_map_studio" / "swissalti3d_cache"
# Grober Umriss Deutschlands (Breite von/bis, Laenge von/bis): nur dafuer, die
# DGM1-Auswahl nur bei Karten in Deutschland anzubieten.
GERMANY_BOUNDS = (47.2, 55.1, 5.8, 15.1)
# Das Copernicus-Hoehenmodell hat nur etwa 30 m pro Pixel: eine Uebergangs-
# breite von 30 m ist genau ein Pixel und erzeugt steile Waende am Ufer.
DEFAULT_TRANSITION_M = 100.0

# Gewaesser, die von Natur aus hoeher als diese Grenze ueber dem gewaehlten
# Wasserspiegel liegen (Baeche und Bergseen), werden bei der Terrain-
# Anpassung nicht abgesenkt - sonst entstehen tiefe Schluchten.
DEFAULT_BLEND_MAX_RISE_M = 12.0

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

# Der Knopf "Straßen und Gleise..." (Mod, der im Spiel Straßen und Gleise baut) ist vorerst ausgeblendet:
# Der Mod wird nicht weiterverfolgt. Auf True setzen, um ihn wieder einzublenden.
SHOW_ROADS_AND_TRACKS_BUTTON = False

# Grenzen der beiden Weichzeichner-Felder (in m). Das Raster hat 4 m je Pixel: Unter etwa 4 m
# bewirkt ein Gauss-Weichzeichner praktisch nichts mehr, "aus" geht ueber den Haken.
SMOOTH_SIGMA_RANGE_M = (1.0, 500.0)
FLATTEN_SIGMA_RANGE_M = (1.0, 1000.0)

# "Empfohlen" haengt von der Hoehenquelle ab. Copernicus (30 m, rauschig) braucht Glaetten und
# die Standardwerte. Das DGM1 (1 m) ist schon genau: Glaetten veraendert dort 36 % der Karte
# (ohne 10 %) und bringt nichts; Gleise und Strassen liegen ohne Glaetten naeher am Original.
DGM1_RECOMMENDED_FLATTEN_SIGMA_M = 10.0
DGM1_RECOMMENDED_ENFORCE_TRANSITION_M = 10.0

# Schritte des Schiebereglers fuer das Hoehenfenster
CLIP_SLIDER_STEPS = 1000

DEFAULT_ENFORCE_DEPTH_M = 8.0     # Tiefe in der Flussmitte (Fahrrinne)
DEFAULT_ENFORCE_EDGE_M = 2.0      # Tiefe direkt am Ufer
DEFAULT_ENFORCE_BANK_M = 2.0
DEFAULT_ENFORCE_MAX_RISE_M = 15.0

# Als Bezug fuer den Gefaelle-Ausgleich zaehlen Seen/Wasserflaechen sowie
# diese Wasserwege - Baeche und Graeben bewusst nicht: sie liegen oft weit
# ueber dem Talfluss und wuerden ihre Umgebung sonst unnatuerlich absenken.
REFERENCE_WATERWAY_TYPES = frozenset({"river", "canal"})


class _WheelGuard(QObject):
    """
    Das Mausrad soll in der Scrollflaeche die Seite scrollen und nicht
    versehentlich Zahlenfelder, Auswahllisten oder den Schieberegler
    veraendern. Nur ein Feld, das angeklickt wurde (Fokus hat), reagiert
    auf das Rad.
    """

    def eventFilter(self, obj, event):

        if event.type() == QEvent.Wheel and not obj.hasFocus():
            event.ignore()
            return True

        return False


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
        self._build_info = None
        self._dgm1_folder = None
        self.suggestion = None
        self._water_mask = None
        self._reference_mask = None
        self._flatten_mask = None
        self._processed_key = None
        self._processed_array = None
        self._processed_suggestion = None
        self._downloaded_once = False
        self._applying_preset = False
        # Hoehenfenster: Bericht der letzten Rechnung und Zwischenspeicher
        self._clip_report = None
        self._clip_key = None
        self._clip_array = None
        self._clip_window_set = False

        self.setWindowTitle(tr("Heightmap"))
        self.setMinimumWidth(420)

        # Aeusserer Rahmen: oben die Scrollflaeche mit allen Einstellungen,
        # darunter fest die Knopfleiste (auch auf kleinen Bildschirmen sichtbar).
        outer = QVBoxLayout(self)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.NoFrame)
        outer.addWidget(self._scroll_area, 1)

        self._scroll_content = QWidget()
        self._scroll_area.setWidget(self._scroll_content)

        layout = QVBoxLayout(self._scroll_content)

        # -------------------------------------------------
        # Download
        # -------------------------------------------------

        self.status_label = QLabel(
            tr("Noch nicht geladen.")
        )
        layout.addWidget(self.status_label)

        source_row = QHBoxLayout()
        source_row.addWidget(QLabel(tr("Höhenquelle:")))

        self.source_combo = QComboBox()
        self.source_combo.addItems([
            tr("Copernicus (weltweit, 30 m)"),
            tr("DGM1 Deutschland (1 m, über hoehendaten.de)"),
            tr("DGM1 aus eigenen GeoTIFF-Kacheln (Ordner)"),
            tr("swissALTI3D Schweiz (2 m, über data.geo.admin.ch)"),
        ])
        self.source_combo.setToolTip(
            tr("Copernicus: weltweit, aber nur 30 m fein und mit Baumkronen. "
            "DGM1 Deutschland: 1-m-Geländemodell der Bundesländer, die Kacheln "
            "werden über den Webdienst hoehendaten.de geladen (etwa 20 Kacheln "
            "pro Minute, danach liegen sie im Zwischenspeicher). Eigene Kacheln: "
            "GeoTIFF-Dateien (1-km-Raster), die du selbst bei einem Landesportal "
            "heruntergeladen hast. swissALTI3D Schweiz: Geländemodell von swisstopo "
            "für die Schweiz und Liechtenstein (2 m), die Kacheln werden von "
            "data.geo.admin.ch geladen und liegen danach im Zwischenspeicher. "
            "Nur bei Karten in der Schweiz wählbar.")
        )
        self.source_combo.currentIndexChanged.connect(
            self._on_source_changed
        )
        source_row.addWidget(self.source_combo, 1)

        layout.addLayout(source_row)

        self.source_label = QLabel("")
        self.source_label.setWordWrap(True)
        self.source_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )
        self.source_label.setVisible(False)
        layout.addWidget(self.source_label)

        self._update_source_availability()

        self.quick_preview_button = QPushButton(
            tr("Schnellvorschau (niedrige Auflösung, vor dem echten Download)")
        )
        self.quick_preview_button.setToolTip(
            tr("Die Schnellvorschau nutzt immer Copernicus (schnell, weltweit), "
            "auch wenn unten eine DGM1-Quelle gewählt ist.")
        )
        self.quick_preview_button.clicked.connect(
            self._quick_preview
        )
        layout.addWidget(self.quick_preview_button)

        self.download_button = QPushButton(
            tr("Höhendaten herunterladen")
        )
        self.download_button.clicked.connect(
            self._download
        )
        layout.addWidget(self.download_button)

        # -------------------------------------------------
        # Voreinstellungen (setzen die Haken mit einem Klick)
        # -------------------------------------------------

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel(tr("Voreinstellung:")))

        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            tr("Eigene Einstellungen"),
            tr("Original (1:1, unverändert)"),
            tr("Empfohlen (Glätten, Einebnen, Wasser nach OSM)"),
        ])
        self.preset_combo.setEnabled(False)
        self.preset_combo.setToolTip(
            tr("Original: alle Optionen aus, die echten Höhen. Empfohlen: "
            "hängt von der Höhenquelle ab. Copernicus: Gelände glätten, "
            "Trassen und Siedlungen einebnen und Wasser nur dort, wo "
            "OpenStreetMap Wasser hat, mit den Standardwerten. DGM1 und "
            "swissALTI3D: "
            "Glätten aus (das Modell ist schon genau), Einebnen 10 m, "
            "Wasser nach OSM mit Böschung 10 m. Optionen, die OSM-Daten "
            "brauchen, bleiben ohne geladene OSM-Daten aus.")
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
        form.addRow(tr("Höhenbereich:"), self.range_label)

        self.exclude_outliers_checkbox = QCheckBox(
            tr("Ausreißer aus Höhenbereich ausschließen (mehr Präzision "
            "fürs eigentliche Gelände)")
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
        form.addRow(tr("Wasserhöhe:"), self.water_level_input)

        self.note_label = QLabel("")
        self.note_label.setWordWrap(True)
        layout.addWidget(self.note_label)

        # Wasserhoehe aus den OSM-Gewaessern: der Vorschlag oben (7,5.
        # Perzentil der ganzen Flaeche) passt schlecht zu Fluessen mit
        # Gefaelle. Hier wird die Mitte zwischen tiefstem und hoechstem
        # Punkt des Hauptflusses vorgeschlagen.
        self.suggest_water_button = QPushButton(
            tr("Wasserhöhe aus den OSM-Gewässern vorschlagen")
        )
        self.suggest_water_button.setEnabled(False)
        self.suggest_water_button.setToolTip(
            tr("Liest die Höhen des Hauptflusses (aus OpenStreetMap) und setzt "
            "die Wasserhöhe in die Mitte zwischen tiefstem und höchstem "
            "Punkt. So wird der Fluss an beiden Enden um etwa gleich viel "
            "korrigiert. Braucht geladene OSM-Daten.")
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

        self.smooth_checkbox = QCheckBox(tr("Gelände glätten"))
        self.smooth_checkbox.setToolTip(
            tr("Gegen Treppenstufen und Kristallflächen an Hängen: das "
            "Höhenmodell hat nur etwa 30 m pro Pixel, das Spiel 4 m.")
        )
        self.smooth_checkbox.setEnabled(False)
        self.smooth_checkbox.toggled.connect(
            self._on_smooth_toggled
        )
        layout.addWidget(self.smooth_checkbox)

        smooth_row = QHBoxLayout()
        smooth_row.addWidget(QLabel(tr("Glättung:")))
        self.smooth_sigma_input = QDoubleSpinBox()
        self.smooth_sigma_input.setRange(*SMOOTH_SIGMA_RANGE_M)
        self.smooth_sigma_input.setDecimals(0)
        self.smooth_sigma_input.setSuffix(" m")
        self.smooth_sigma_input.setValue(DEFAULT_SMOOTHING_SIGMA_M)
        self.smooth_sigma_input.setEnabled(False)
        self.smooth_sigma_input.setMinimumWidth(110)
        self.smooth_sigma_input.setKeyboardTracking(False)
        self.smooth_sigma_input.setToolTip(
            tr("Breite der Glättung. 15 m entfernt die gröbsten Stufen, "
            "30 m glättet stärker, flacht aber Gipfel und Kämme leicht ab.")
        )
        self.smooth_sigma_input.valueChanged.connect(
            self._update_preview
        )
        smooth_row.addWidget(self.smooth_sigma_input)

        smooth_row.addWidget(QLabel(tr("Höhen stauchen auf:")))
        self.compress_input = QDoubleSpinBox()
        self.compress_input.setRange(20.0, 100.0)
        self.compress_input.setDecimals(0)
        self.compress_input.setSuffix(" %")
        self.compress_input.setValue(100.0)
        self.compress_input.setEnabled(False)
        self.compress_input.setMinimumWidth(110)
        self.compress_input.setKeyboardTracking(False)
        self.compress_input.setToolTip(
            tr("Staucht alle Höhen über dem Wasserspiegel auf diesen Anteil. "
            "100 % = unverändert. Hilft, wenn Hochflächen im Spiel über die "
            "Schneegrenze ragen (weiße Flächen). Die Hänge werden dabei "
            "flacher.")
        )
        self.compress_input.valueChanged.connect(
            self._update_preview
        )
        smooth_row.addWidget(self.compress_input)

        smooth_row.addStretch(1)
        layout.addLayout(smooth_row)

        self.flatten_checkbox = QCheckBox(tr("Trassen und Siedlungen einebnen"))
        self.flatten_checkbox.setToolTip(
            tr("Bahnstrecken, größere Straßen und Gebäude aus OpenStreetMap: "
            "das Gelände dort wird abgeflacht, damit im Spiel weniger "
            "Rampen nötig sind. Braucht geladene OSM-Daten.")
        )
        self.flatten_checkbox.setEnabled(False)
        self.flatten_checkbox.toggled.connect(
            self._on_flatten_toggled
        )
        layout.addWidget(self.flatten_checkbox)

        flatten_row = QHBoxLayout()
        flatten_row.addWidget(QLabel(tr("Glättung:")))
        self.flatten_sigma_input = QDoubleSpinBox()
        self.flatten_sigma_input.setRange(*FLATTEN_SIGMA_RANGE_M)
        self.flatten_sigma_input.setDecimals(0)
        self.flatten_sigma_input.setSuffix(" m")
        self.flatten_sigma_input.setValue(DEFAULT_FLATTEN_SIGMA_M)
        self.flatten_sigma_input.setEnabled(False)
        self.flatten_sigma_input.setMinimumWidth(110)
        self.flatten_sigma_input.setKeyboardTracking(False)
        self.flatten_sigma_input.setToolTip(
            tr("Je größer, desto ebener wird das Gelände entlang der Trassen "
            "und in den Ortschaften. Einschnitte und Dämme verschwinden.")
        )
        self.flatten_sigma_input.valueChanged.connect(
            self._update_preview
        )
        flatten_row.addWidget(self.flatten_sigma_input)
        flatten_row.addStretch(1)
        layout.addLayout(flatten_row)

        self.slope_checkbox = QCheckBox(tr("Gefälle ausgleichen"))
        self.slope_checkbox.setToolTip(
            tr("Legt Flüsse und Seen auf eine gemeinsame Ebene und zieht das "
            "Gelände relativ dazu mit. Das Relief über dem jeweiligen "
            "Wasserspiegel bleibt erhalten, die absoluten Höhen ü. NN "
            "stimmen danach aber nicht mehr.")
        )
        self.slope_checkbox.setEnabled(False)
        self.slope_checkbox.toggled.connect(
            self._on_slope_toggled
        )
        layout.addWidget(self.slope_checkbox)

        slope_row = QHBoxLayout()

        slope_row.addWidget(QLabel(tr("Stärke:")))
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

        slope_row.addWidget(QLabel(tr("Glättung:")))
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

        slope_row.addWidget(QLabel(tr("Bezug: Gewässer bis")))
        self.slope_max_ref_input = QDoubleSpinBox()
        self.slope_max_ref_input.setRange(1.0, 1000.0)
        self.slope_max_ref_input.setDecimals(0)
        self.slope_max_ref_input.setSuffix(tr(" m über Wasserspiegel"))
        self.slope_max_ref_input.setMinimumWidth(250)
        self.slope_max_ref_input.setValue(DEFAULT_SLOPE_MAX_REF_M)
        self.slope_max_ref_input.setEnabled(False)
        self.slope_max_ref_input.setKeyboardTracking(False)
        self.slope_max_ref_input.setToolTip(
            tr("Nur Gewässer, die höchstens so hoch über dem Wasserspiegel "
            "liegen, dienen als Bezug. Höher gelegene Nebenflüsse und "
            "Bergseen werden ignoriert, sonst würde ihr Tal überflutet.")
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
            tr("Wasser nur dort, wo OpenStreetMap Wasser hat (empfohlen)")
        )
        self.enforce_checkbox.setToolTip(
            tr("Gewässer bekommen ein festes Bett, alles andere Land liegt "
            "knapp über dem Wasserspiegel: keine überfluteten Auen und "
            "Tümpel. Ersetzt die sanfte Anpassung unten.")
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
            tr("Böschung:"), DEFAULT_ENFORCE_TRANSITION_M, 10.0, 300.0, 0, " m",
            tr("Breite der Böschung zwischen Flussbett und Land. Breiter = "
            "flacheres Ufer, aber auch etwas breiteres Wasser.")
        )
        self.enforce_edge_input = _enforce_spin(
            tr("Tiefe am Ufer:"), DEFAULT_ENFORCE_EDGE_M, 0.5, 10.0, 1, " m",
            tr("Tiefe des Flussbetts direkt am Ufer. Zur Mitte hin wird es "
            "tiefer (Fahrrinne), das ergibt einen natürlichen Querschnitt.")
        )
        self.enforce_depth_input = _enforce_spin(
            tr("Tiefe in der Mitte:"), DEFAULT_ENFORCE_DEPTH_M, 1.0, 30.0, 0, " m",
            tr("Tiefe des Flussbetts unter dem Wasserspiegel.")
        )
        self.enforce_bank_input = _enforce_spin(
            tr("Ufer über Wasser:"), DEFAULT_ENFORCE_BANK_M, 0.5, 10.0, 1, " m",
            tr("So hoch liegt Land am Ufer mindestens über dem Wasserspiegel. "
            "Alles darunter wird angehoben und kann nicht überflutet werden."),
            row=enforce_row2,
        )
        self.enforce_max_rise_input = _enforce_spin(
            tr("Nur Gewässer bis"), DEFAULT_ENFORCE_MAX_RISE_M, 1.0, 500.0, 0,
            tr(" m über Wasserspiegel"),
            tr("Gewässer, die von Natur aus höher liegen (Bäche in den "
            "Bergen, Bergseen), bleiben unverändert."),
            row=enforce_row2,
            min_width=250,
        )

        enforce_row.addStretch(1)
        enforce_row2.addStretch(1)

        layout.addLayout(enforce_row)
        layout.addLayout(enforce_row2)

        self.water_blend_checkbox = QCheckBox(
            tr("Terrain sanft ans Wasserniveau anpassen")
        )
        self.water_blend_checkbox.setToolTip(
            tr("Verhindert trockenfallende Flüsse und Seen, weicht dafür "
            "geringfügig von den echten Höhendaten ab. Sehr kleine "
            "Einzelgewässer werden ausgenommen, um Krater zu vermeiden. "
            "Das Gelände unterhalb des Wasserspiegels wird zusätzlich "
            "weichgezeichnet.")
        )
        self.water_blend_checkbox.setEnabled(False)
        self.water_blend_checkbox.toggled.connect(
            self._on_water_blend_toggled
        )
        layout.addWidget(self.water_blend_checkbox)

        transition_row = QHBoxLayout()
        transition_row.addWidget(QLabel(tr("Übergangsbreite:")))
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

        transition_row.addWidget(QLabel(tr("Nur Gewässer bis")))
        self.blend_max_rise_input = QDoubleSpinBox()
        self.blend_max_rise_input.setRange(1.0, 500.0)
        self.blend_max_rise_input.setDecimals(0)
        self.blend_max_rise_input.setSuffix(tr(" m über Wasserspiegel"))
        self.blend_max_rise_input.setMinimumWidth(250)
        self.blend_max_rise_input.setValue(DEFAULT_BLEND_MAX_RISE_M)
        self.blend_max_rise_input.setEnabled(False)
        self.blend_max_rise_input.setKeyboardTracking(False)
        self.blend_max_rise_input.setToolTip(
            tr("Gewässer, die von Natur aus höher liegen (Bäche in den Bergen, "
            "Bergseen), bleiben unverändert und werden nicht zu Schluchten.")
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
        # Höhenfenster (Grenzen des Karteneditors)
        # -------------------------------------------------

        self.clip_checkbox = QCheckBox(
            tr(
                "Höhenfenster begrenzen (Editor nimmt nur "
                "{low:.0f} bis {high:.0f} m)"
            ).format(low=GAME_MIN_M, high=GAME_MAX_M)
        )
        self.clip_checkbox.setToolTip(
            tr("Der Karteneditor von TPF3 nimmt nur Höhen in diesem Bereich an. "
            "Liegt das Gelände (zum Beispiel in den Alpen) darüber oder darunter, "
            "wird es hier in ein Fenster gelegt. Die Vorschau färbt betroffene "
            "Stellen ein: rot = tiefer gesetzt (oben gekappt oder gestaucht), "
            "hellblau = höher gesetzt (unten abgeschnitten). Das Fenster gilt "
            "in Eintragswerten, also mit dem Haken unten bezogen auf die "
            "Wasserhöhe.")
        )
        self.clip_checkbox.setEnabled(False)
        self.clip_checkbox.toggled.connect(
            self._on_clip_toggled
        )
        layout.addWidget(self.clip_checkbox)

        clip_mode_row = QHBoxLayout()
        clip_mode_row.addWidget(QLabel(tr("Werte außerhalb:")))

        self.clip_mode_combo = QComboBox()
        self.clip_mode_combo.addItems([
            tr("Oben kappen (Gipfel planieren)"),
            tr("Unten abschneiden (Tiefen planieren)"),
            tr("Stauchen (alles ins Fenster drücken)"),
        ])
        self.clip_mode_combo.setEnabled(False)
        self.clip_mode_combo.setToolTip(
            tr("Oben kappen: Alles über dem Fenster wird flach auf die Obergrenze "
            "gesetzt, das Fenster liegt zunächst an der tiefsten Stelle. "
            "Unten abschneiden: Alles unter dem Fenster wird flach auf die "
            "Untergrenze gesetzt, das Fenster liegt zunächst an der höchsten "
            "Stelle. Stauchen: das ganze Gelände wird ins Fenster gedrückt, die "
            "Wasserhöhe bleibt dabei erhalten. Die Fensterbreite bestimmen "
            "die Felder darunter, der Schieberegler verschiebt das Fenster.")
        )
        self.clip_mode_combo.currentIndexChanged.connect(
            self._on_clip_mode_changed
        )
        clip_mode_row.addWidget(self.clip_mode_combo, 1)
        layout.addLayout(clip_mode_row)

        clip_window_row = QHBoxLayout()

        clip_window_row.addWidget(QLabel(tr("Fenster von:")))
        self.clip_min_input = self._make_clip_spin()
        clip_window_row.addWidget(self.clip_min_input)

        clip_window_row.addWidget(QLabel(tr("bis:")))
        self.clip_max_input = self._make_clip_spin()
        clip_window_row.addWidget(self.clip_max_input)

        clip_window_row.addStretch(1)
        layout.addLayout(clip_window_row)

        clip_slider_row = QHBoxLayout()
        clip_slider_row.addWidget(QLabel(tr("Fenster verschieben:")))

        self.clip_slider = QSlider(Qt.Horizontal)
        self.clip_slider.setRange(0, CLIP_SLIDER_STEPS)
        # Erst beim Loslassen neu rechnen, nicht bei jedem Pixel
        self.clip_slider.setTracking(False)
        self.clip_slider.setEnabled(False)
        self.clip_slider.valueChanged.connect(
            self._on_clip_slider_changed
        )
        clip_slider_row.addWidget(self.clip_slider, 1)
        layout.addLayout(clip_slider_row)

        self.clip_report_label = QLabel("")
        self.clip_report_label.setWordWrap(True)
        layout.addWidget(self.clip_report_label)

        # -------------------------------------------------
        # Werte fuer den TPF3-Import (immer passend zum Export)
        # -------------------------------------------------

        self.relative_values_checkbox = QCheckBox(
            tr("Werte auf Wasserhöhe 0 beziehen")
        )
        self.relative_values_checkbox.setToolTip(
            tr("Empfehlung des TPF3-Wikis für Biome und Materialien. Die "
            "Mindesthöhe kann dabei negativ werden.")
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
        outer.addLayout(button_row)

        # Anleitung: Schritt fuer Schritt von der Auswahl bis zum Import
        # im Spiel (auch ueber F1 erreichbar).
        self.guide_button = QPushButton(tr("Anleitung (F1)"))
        self.guide_button.clicked.connect(self._open_guide)
        button_row.addWidget(self.guide_button)

        QShortcut(
            QKeySequence("F1"),
            self,
            activated=self._open_guide,
        )

        self._connect_custom_markers()

        self.export_button = QPushButton(
            tr("Exportieren...")
        )
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(
            self._export
        )
        button_row.addWidget(self.export_button)

        # Biome-Maske aus der geladenen OSM-Landnutzung (eigener Dialog).
        self.biome_button = QPushButton(tr("Biome-Maske aus OSM..."))
        self.biome_button.setToolTip(
            tr("Erzeugt aus der geladenen OSM-Landnutzung eine Maske für den "
            "Biome-Tab im Karteneditor. Braucht geladene OSM-Daten.")
        )
        self.biome_button.clicked.connect(self._open_biome_dialog)
        button_row.addWidget(self.biome_button)

        # Staedte aus OSM-Orten (eigener Dialog, Datei fuer towns_industries).
        self.towns_button = QPushButton(tr("Städte aus OSM..."))
        self.towns_button.setToolTip(
            tr("Erzeugt aus den geladenen OSM-Orten eine Städte-Datei für den "
            "Ordner towns_industries. Braucht geladene OSM-Daten.")
        )
        self.towns_button.clicked.connect(self._open_towns_dialog)
        button_row.addWidget(self.towns_button)

        # Industrien aus OSM-Objekten (eigener Dialog, Datei fuer
        # towns_industries).
        self.industries_button = QPushButton(tr("Industrien aus OSM..."))
        self.industries_button.setToolTip(
            tr("Erzeugt aus geladenen OSM-Objekten (Höfe, Steinbrüche, "
            "Sägewerke, ...) eine Industrien-Datei für den Ordner "
            "towns_industries. Braucht geladene OSM-Daten.")
        )
        self.industries_button.clicked.connect(self._open_industries_dialog)
        button_row.addWidget(self.industries_button)

        # Bahnhoefe aus OSM (Name, Lage, Bahnsteige, Gebaeude): schreibt eine
        # .json und eine .csv, baut nichts im Spiel.
        self.stations_button = QPushButton(tr("Bahnhöfe aus OSM..."))
        self.stations_button.setToolTip(
            tr("Liest Bahnhöfe, Haltepunkte, Bahnsteige, Bahnhofsgebäude und "
            "Haltepositionen aus den geladenen OSM-Daten und speichert sie als "
            ".json (alles) und .csv (eine Zeile je Bahnhof). Braucht geladene "
            "OSM-Daten.")
        )
        self.stations_button.clicked.connect(self._open_stations_dialog)
        button_row.addWidget(self.stations_button)

        # Strassen und Gleise fuer den Spiel-Mod (eigener Dialog, schreibt
        # den Mod in den Ordner mods). Vorerst ausgeblendet.
        self.network_button = QPushButton(tr("Straßen und Gleise..."))
        self.network_button.setToolTip(
            tr("Erzeugt aus den geladenen OSM-Wegen einen Mod, der im Spiel "
            "Straßen, Gleise, Brücken und Tunnel baut. Braucht geladene "
            "OSM-Daten.")
        )
        self.network_button.clicked.connect(self._open_network_dialog)
        button_row.addWidget(self.network_button)
        self.network_button.setVisible(SHOW_ROADS_AND_TRACKS_BUTTON)

        close_button = QPushButton(tr("Schließen"))
        close_button.clicked.connect(self.reject)
        button_row.addWidget(close_button)

        self._install_wheel_guard()
        self._fit_to_screen()

    # ---------------------------------------------------------
    # Scrollflaeche und Fenstergroesse
    # ---------------------------------------------------------

    def _install_wheel_guard(self):
        """Mausrad nur bei angeklickten Feldern, sonst scrollt die Seite."""

        self._wheel_guard = _WheelGuard(self)

        for cls in (QAbstractSpinBox, QComboBox, QSlider):

            for widget in self._scroll_content.findChildren(cls):
                widget.setFocusPolicy(Qt.StrongFocus)
                widget.installEventFilter(self._wheel_guard)

    def _fit_to_screen(self, available=None):
        """
        Startgroesse: so gross, dass moeglichst alles sichtbar ist, aber nie
        groesser als der nutzbare Bildschirm. Reicht der Platz nicht, scrollt
        die Seite (die Knopfleiste bleibt unten stehen).
        `available` (QRect) dient nur den Tests, sonst gilt der Bildschirm.
        """

        if available is None:

            screen = self.screen() or QApplication.primaryScreen()

            if screen is None:
                return

            available = screen.availableGeometry()

        content = self._scroll_content.sizeHint()
        buttons = self.export_button.sizeHint().height()

        # Platz fuer Rahmen, Titelleiste und den senkrechten Rollbalken
        want_w = content.width() + 60
        want_h = content.height() + buttons + 60

        max_w = max(480, int(available.width() * 0.95))
        max_h = max(360, int(available.height() * 0.90))

        self.resize(
            min(max(want_w, self.minimumSizeHint().width()), max_w),
            min(want_h, max_h),
        )

    # ---------------------------------------------------------
    # Anleitung
    # ---------------------------------------------------------

    def _open_guide(self):

        HeightmapGuideDialog(self).exec()

    def _open_biome_dialog(self):

        has_osm_data = (
            self.osm is not None
            and (self.osm.node_count > 0 or self.osm.way_count > 0)
        )

        if not has_osm_data:
            QMessageBox.information(
                self,
                tr("Biome-Maske"),
                tr("Keine OSM-Daten geladen. Zuerst Werkzeuge → OSM laden "
                "ausführen und die Ebenen Landnutzung/Vegetation laden."),
            )
            return

        BiomeMaskDialog(self, self.selection, self.osm).exec()

    def _open_towns_dialog(self):

        has_osm_data = (
            self.osm is not None
            and (self.osm.node_count > 0 or self.osm.way_count > 0)
        )

        if not has_osm_data:
            QMessageBox.information(
                self,
                tr("Städte aus OSM"),
                tr("Keine OSM-Daten geladen. Zuerst Werkzeuge → OSM laden "
                "ausführen."),
            )
            return

        TownsDialog(self, self.selection, self.osm).exec()

    def _open_stations_dialog(self):

        has_osm_data = (
            self.osm is not None
            and (self.osm.node_count > 0 or self.osm.way_count > 0)
        )

        if not has_osm_data:
            QMessageBox.information(
                self,
                tr("Bahnhöfe aus OSM"),
                tr("Keine OSM-Daten geladen. Zuerst Werkzeuge → OSM laden "
                "ausführen und die Ebene Eisenbahn laden."),
            )
            return

        save_stations_dialog(self, self.selection, self.osm)

    def _open_network_dialog(self):

        has_osm_data = (
            self.osm is not None
            and (self.osm.node_count > 0 or self.osm.way_count > 0)
        )

        if not has_osm_data:
            QMessageBox.information(
                self,
                tr("Straßen und Gleise"),
                tr("Keine OSM-Daten geladen. Zuerst Werkzeuge → OSM laden "
                "ausführen und die Ebenen Straßen und Eisenbahn laden."),
            )
            return

        NetworkDialog(self, self.selection, self.osm).exec()

    def _open_industries_dialog(self):

        has_osm_data = (
            self.osm is not None
            and (self.osm.node_count > 0 or self.osm.way_count > 0)
        )

        if not has_osm_data:
            QMessageBox.information(
                self,
                tr("Industrien aus OSM"),
                tr("Keine OSM-Daten geladen. Zuerst Werkzeuge → OSM laden "
                "ausführen."),
            )
            return

        # Hoehenraster (wie exportiert) und Wassermaske, damit keine
        # Industrien auf Haengen oder am Wasser landen. Ohne geladene
        # Hoehendaten bleibt die Pruefung aus.
        terrain = None

        if self.heightmap_array is not None:

            try:
                terrain = Terrain(
                    self._effective_heightmap(),
                    self._get_water_mask(),
                    self.selection.width_m,
                    self.selection.height_m,
                )
            except Exception:
                terrain = None

        IndustriesDialog(self, self.selection, self.osm, terrain).exec()

    # ---------------------------------------------------------
    # Download
    # ---------------------------------------------------------

    def _current_source(self) -> str:
        return (
            SOURCE_COPERNICUS,
            SOURCE_DGM1_DE,
            SOURCE_DGM1_FOLDER,
            SOURCE_SWISSALTI3D,
        )[self.source_combo.currentIndex()]

    def _update_source_availability(self):
        """DGM1 Deutschland nur bei Karten in Deutschland, swissALTI3D nur bei Karten in der Schweiz anbieten."""

        lat, lon = self.selection.center
        lat_min, lat_max, lon_min, lon_max = GERMANY_BOUNDS

        in_germany = lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

        item = self.source_combo.model().item(1)

        if item is not None:
            item.setEnabled(in_germany)

        if not in_germany and self.source_combo.currentIndex() == 1:
            self.source_combo.setCurrentIndex(0)

        # swissALTI3D nur bei Karten in der Schweiz (und Liechtenstein)
        s_lat_min, s_lat_max, s_lon_min, s_lon_max = SWISS_BOUNDS

        in_switzerland = s_lat_min <= lat <= s_lat_max and s_lon_min <= lon <= s_lon_max

        swiss_item = self.source_combo.model().item(3)

        if swiss_item is not None:
            swiss_item.setEnabled(in_switzerland)

        if not in_switzerland and self.source_combo.currentIndex() == 3:
            self.source_combo.setCurrentIndex(0)

    def _on_source_changed(self, index: int):

        if index != 2:
            return

        folder = QFileDialog.getExistingDirectory(
            self,
            tr("Ordner mit DGM1-GeoTIFF-Kacheln wählen"),
            str(self._dgm1_folder or Path.home()),
        )

        if not folder:
            # Abbruch: zurueck zur vorherigen Quelle
            self.source_combo.blockSignals(True)
            self.source_combo.setCurrentIndex(
                2 if self._dgm1_folder else 0
            )
            self.source_combo.blockSignals(False)
            return

        self._dgm1_folder = Path(folder)

    def _build_heightmap_for_source(self):
        """Baut das Hoehenraster aus der gewaehlten Quelle (bei DGM1 Deutschland
        erst die fehlenden Kacheln laden)."""

        source = self._current_source()

        if source == SOURCE_DGM1_DE:

            fetch_dialog = Dgm1FetchDialog(
                self,
                self.selection,
                DEFAULT_DGM1_CACHE_DIR,
            )

            if not fetch_dialog.run():
                raise RuntimeError(
                    fetch_dialog.error or tr("Abgebrochen.")
                )

            self.status_label.setText(tr("Berechne Höhenraster..."))
            self.repaint()

        elif source == SOURCE_SWISSALTI3D:

            fetch_dialog = Dgm1FetchDialog(
                self,
                self.selection,
                DEFAULT_SWISS_CACHE_DIR,
                job=SwissFetchJob(self.selection, DEFAULT_SWISS_CACHE_DIR),
                title=tr("swissALTI3D-Kacheln laden"),
                note=(
                    tr("Die Kacheln kommen von data.geo.admin.ch (swisstopo). Bereits "
                    "geladene Kacheln werden übersprungen. Du kannst jederzeit "
                    "abbrechen und später weitermachen.")
                ),
                seconds_per_tile=1.0,
            )

            if not fetch_dialog.run():
                raise RuntimeError(
                    fetch_dialog.error or tr("Abgebrochen.")
                )

            self.status_label.setText(tr("Berechne Höhenraster..."))
            self.repaint()

        array, info = build_heightmap_array_ex(
            self.selection,
            DEFAULT_CACHE_DIR,
            source,
            dgm1_cache_dir=DEFAULT_DGM1_CACHE_DIR,
            dgm1_folder=self._dgm1_folder,
            swiss_cache_dir=DEFAULT_SWISS_CACHE_DIR,
        )

        self._build_info = info

        return array

    def _source_status_suffix(self) -> str:

        info = self._build_info

        if info is None or info.source == SOURCE_COPERNICUS:
            return ""

        name = "swissALTI3D" if info.source == SOURCE_SWISSALTI3D else "DGM1"

        if info.fallback_fraction > 0.0005:
            return tr(
                " ({name}, {percent:.1f} % der Fläche aus Copernicus "
                "ergänzt)"
            ).format(
                name=name,
                percent=info.fallback_fraction * 100,
            )

        return f" ({name})"

    def _show_source_info(self):
        """Quellenvermerk und Hinweise zur Hoehenquelle unter dem Statustext."""

        info = self._build_info

        if info is None or info.source == SOURCE_COPERNICUS:
            self.source_label.setVisible(False)
            return

        lines = []

        swiss = info.source == SOURCE_SWISSALTI3D

        if info.attributions:
            lines.append(
                tr("Quelle: {sources}").format(
                    sources=" | ".join(info.attributions)
                )
            )
        elif swiss:
            lines.append(tr("Quelle: © swisstopo (Bundesamt für Landestopografie swisstopo), swissALTI3D"))
        else:
            lines.append(tr("Quelle: DGM1 der Landesvermessung (Quellenvermerk des Landes beachten)"))

        if info.missing_tiles > 0:
            lines.append(
                tr(
                    "{count} Kacheln ohne {source}-Daten im Ausschnitt "
                    "(dort Copernicus)."
                ).format(
                    count=info.missing_tiles,
                    source="swissALTI3D" if swiss else "DGM1",
                )
            )

        if info.fallback_fraction > 0.02:
            lines.append(
                tr("Achtung: Ein größerer Teil der Fläche stammt aus Copernicus. "
                "An den Nahtstellen kann es kleine Höhenstufen geben.")
            )

        self.source_label.setText("\n".join(lines))
        self.source_label.setVisible(True)

    def _download(self):

        self.status_label.setText(
            tr("Lade Höhendaten... (kann je nach Kartengröße etwas dauern)")
        )
        self.download_button.setEnabled(False)
        # Sorgt dafuer, dass der Text vor dem (blockierenden) Download
        # tatsaechlich schon sichtbar ist.
        self.repaint()

        try:
            self.heightmap_array = self._build_heightmap_for_source()
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
        self.clip_checkbox.setEnabled(True)

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
                tr("Keine OSM-Daten geladen - für die Terrain-Anpassung "
                "werden die Wasserflächen aus 'OSM laden' benötigt.")
            )
            self.slope_note_label.setText(
                tr("Keine OSM-Daten geladen - der Gefälle-Ausgleich "
                "braucht die Gewässer aus 'OSM laden'.")
            )
        else:
            self.water_blend_note_label.setText("")
            self.slope_note_label.setText("")

        if self.suggestion.outlier_count > 0:

            self.exclude_outliers_checkbox.setText(
                tr(
                    "Ausreißer aus Höhenbereich ausschließen "
                    "({count} Pixel, {percent:.2f}% der Fläche erkannt)"
                ).format(
                    count=self.suggestion.outlier_count,
                    percent=self.suggestion.outlier_fraction * 100,
                )
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
            + self._source_status_suffix()
        )
        self._show_source_info()

        self.export_button.setEnabled(True)
        self.download_button.setEnabled(True)

        # Neues Raster: das Hoehenfenster beginnt wieder bei der Voreinstellung
        self._clip_window_set = False

        if self.clip_checkbox.isChecked():
            self._reset_clip_window()

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
            tr("Lade Schnellvorschau...")
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
                tr("Schnellvorschau fehlgeschlagen: {error}").format(
                    error=exc
                )
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
            tr(
                "Schnellvorschau ({width} x {height} Pixel, niedrige "
                "Auflösung - noch nicht exportierbar). Sieht das plausibel "
                "aus? Dann jetzt 'Höhendaten herunterladen' für die volle "
                "Auflösung."
            ).format(
                width=preview_array.shape[1],
                height=preview_array.shape[0],
            )
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

        # Mit Hoehenfenster ist das Fenster selbst der Bereich: Vorschau, Zahlen
        # und Export benutzen genau diese Grenzen.
        if self.clip_checkbox.isChecked():
            return self._clip_window_real()

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
                tr("Wassermaske fehlgeschlagen"),
                str(exc),
            )
            self.slope_checkbox.setChecked(False)
            return

        if not reference_mask.any():

            self.slope_note_label.setText(
                tr("In diesem Kartenausschnitt wurden keine Seen oder "
                "größeren Flüsse als Bezug gefunden - der "
                "Gefälle-Ausgleich hat hier keine Wirkung.")
            )

        else:

            self.slope_note_label.setText(
                tr("Als Bezug dienen Seen und Wasserflächen sowie Flüsse "
                "und Kanäle bis zur eingestellten Höhe über dem "
                "Wasserspiegel; Bäche, Gräben und höher gelegene "
                "Gewässer zählen dafür nicht.")
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

        # "Höhen stauchen" gehört bewusst NICHT dazu: Wie stark ein Gelände
        # gestaucht werden muss, hängt von der Karte ab (Schneegrenze), nicht
        # von der Voreinstellung. Eine Änderung dort lässt die Voreinstellung
        # (z. B. "Empfohlen") stehen.
        spins = (
            self.smooth_sigma_input,
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

        # Quelle des GELADENEN Rasters (nicht der Auswahl in der Liste, die danach
        # geaendert worden sein kann)
        info = getattr(self, "_build_info", None)
        source = info.source if info is not None else self._current_source()
        dgm1 = source in (SOURCE_DGM1_DE, SOURCE_DGM1_FOLDER, SOURCE_SWISSALTI3D)

        wanted_on = {
            1: (),
            2: (
                (() if dgm1 else (self.smooth_checkbox,))
                + (self.flatten_checkbox, self.enforce_checkbox)
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
            self.flatten_sigma_input.setValue(
                DGM1_RECOMMENDED_FLATTEN_SIGMA_M
                if (dgm1 and index == 2)
                else DEFAULT_FLATTEN_SIGMA_M
            )
            # "Original" stellt auch die Stauchung zurück (1:1). Bei
            # "Empfohlen" bleibt der gewählte Stauchwert erhalten.
            if index == 1:
                self.compress_input.setValue(100.0)
                self.clip_checkbox.setChecked(False)

            self.enforce_transition_input.setValue(
                DGM1_RECOMMENDED_ENFORCE_TRANSITION_M
                if (dgm1 and index == 2)
                else DEFAULT_ENFORCE_TRANSITION_M
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
            QMessageBox.critical(self, tr("Wassermaske fehlgeschlagen"), str(exc))
            return

        QApplication.restoreOverrideCursor()

        if not mask.any():

            QMessageBox.information(
                self,
                tr("Keine Gewässer"),
                tr("In diesem Kartenausschnitt wurden keine Wasserflächen oder "
                "-wege gefunden. Zuerst OSM-Daten laden "
                "(Werkzeuge → OSM laden)."),
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
            tr(
                "Hauptfluss liegt zwischen {low:.0f} und {high:.0f} m. "
                "Wasserhöhe auf {middle:.0f} m gesetzt (Mitte). Die "
                "Wasseroberfläche wird am oberen Ende um bis zu "
                "{lowered:.0f} m abgesenkt und am unteren um bis zu "
                "{raised:.0f} m angehoben."
            ).format(
                low=river_low,
                high=river_high,
                middle=middle,
                lowered=lowered,
                raised=raised,
            )
        )

        if raised_threshold:
            text += (
                tr(
                    " Die Grenze „Nur Gewässer bis“ wurde auf {value} m "
                    "erhöht."
                ).format(value=needed_rise)
            )

        self.water_hint_label.setText(text)

        self._update_preview()

    def _on_relative_values_toggled(self, checked: bool):

        # Das Hoehenfenster gilt in Eintragswerten: es wandert mit der Wasserhoehe.
        if self.clip_checkbox.isChecked() and self.heightmap_array is not None:
            self._update_preview()
            return

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
                    tr("Wassermaske fehlgeschlagen"),
                    str(exc),
                )
                self.enforce_checkbox.setChecked(False)
                return

            if not water_mask.any():

                QMessageBox.information(
                    self,
                    tr("Keine Gewässer"),
                    tr("In diesem Kartenausschnitt wurden keine Wasserflächen "
                    "oder -wege gefunden - die Einstellung hat keine "
                    "Wirkung. Zuerst OSM-Daten laden (Werkzeuge → OSM laden)."),
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
                    tr("Wassermaske fehlgeschlagen"),
                    str(exc),
                )
                self.water_blend_checkbox.setChecked(False)
                return

            if not water_mask.any():

                self.water_blend_note_label.setText(
                    tr("In diesem Kartenausschnitt wurden keine "
                    "Wasserflächen/-wege gefunden - die Anpassung hat "
                    "hier keine Wirkung.")
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
        self._clip_key = None
        self._clip_array = None
        self._clip_report = None

    def _unclipped_heightmap(self):
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

    def _effective_heightmap(self):
        """
        Das Raster, das Vorschau, Zahlen im Dialog und Export tatsaechlich
        benutzen: das bearbeitete Gelaende, danach (wenn angehakt) das
        Hoehenfenster. Alles laeuft ueber apply_height_window(), damit Vorschau
        und exportierte PNG nicht auseinanderlaufen.
        """

        array = self._unclipped_heightmap()

        if not self.clip_checkbox.isChecked():
            self._clip_report = None
            return array

        window_min, window_max = self._clip_window_real()
        mode = self._clip_mode()
        water_level = self.water_level_input.value()

        key = (self._processing_key(), mode, window_min, window_max)

        if key == self._clip_key and self._clip_array is not None:
            return self._clip_array

        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            clipped, report = apply_height_window(
                array,
                window_min,
                window_max,
                mode,
                anchor=water_level,
            )
        finally:
            QApplication.restoreOverrideCursor()

        self._clip_array = clipped
        self._clip_report = report
        self._clip_key = key
        self._processed_suggestion = None

        return clipped

    # ---------------------------------------------------------
    # Hoehenfenster
    # ---------------------------------------------------------

    def _make_clip_spin(self):

        spin = QDoubleSpinBox()
        spin.setRange(GAME_MIN_M, GAME_MAX_M)
        spin.setDecimals(0)
        spin.setSuffix(" m")
        spin.setMinimumWidth(110)
        spin.setKeyboardTracking(False)
        spin.setEnabled(False)
        spin.valueChanged.connect(self._on_clip_spin_changed)

        return spin

    def _clip_mode(self) -> str:

        return MODES[self.clip_mode_combo.currentIndex()]

    def _clip_offset(self) -> float:
        """Eintragswerte -> echte Hoehen: mit dem Haken relativ zur Wasserhoehe."""

        if self.relative_values_checkbox.isChecked():
            return self.water_level_input.value()

        return 0.0

    def _clip_window_real(self) -> tuple[float, float]:

        offset = self._clip_offset()

        return (
            self.clip_min_input.value() + offset,
            self.clip_max_input.value() + offset,
        )

    def _clip_data_range(self) -> tuple[float, float]:
        """Hoehenbereich des Rasters vor dem Fenster, in Eintragswerten."""

        array = self._unclipped_heightmap()
        offset = self._clip_offset()

        return float(array.min()) - offset, float(array.max()) - offset

    def _set_clip_window(self, low: float, high: float):

        for spin, value in (
            (self.clip_min_input, low),
            (self.clip_max_input, high),
        ):
            spin.blockSignals(True)
            spin.setValue(value)
            spin.blockSignals(False)

        self._clip_window_set = True

        self._sync_clip_slider()

    def _reset_clip_window(self, width: float | None = None):
        """Fenster passend zum Modus voreinstellen (ganze Zahlen, nie knapper als das Gelaende)."""

        import math

        data_min, data_max = self._clip_data_range()

        low, high = default_window(data_min, data_max, self._clip_mode(), width)

        low = max(GAME_MIN_M, float(math.floor(low)))
        high = min(GAME_MAX_M, float(math.ceil(high)))

        if high - low < MIN_WINDOW_M:
            high = min(GAME_MAX_M, low + MIN_WINDOW_M)
            low = high - MIN_WINDOW_M

        self._set_clip_window(low, high)

    def _sync_clip_slider(self):
        """Schieberegler passend zum Fenster setzen (ohne eine Rechnung auszuloesen)."""

        if self.heightmap_array is None:
            return

        low = self.clip_min_input.value()
        width = self.clip_max_input.value() - low

        first, last = window_slider_range(width)

        self.clip_slider.blockSignals(True)

        if last - first < 1.0:

            self.clip_slider.setEnabled(False)
            self.clip_slider.setValue(0)

        else:

            self.clip_slider.setEnabled(self.clip_checkbox.isChecked())

            share = min(1.0, max(0.0, (low - first) / (last - first)))

            self.clip_slider.setValue(round(share * CLIP_SLIDER_STEPS))

        self.clip_slider.blockSignals(False)

    def _on_clip_toggled(self, checked: bool):

        self.clip_mode_combo.setEnabled(checked)
        self.clip_min_input.setEnabled(checked)
        self.clip_max_input.setEnabled(checked)

        if not checked:

            self.clip_slider.setEnabled(False)
            self._clip_report = None
            self.clip_report_label.setText("")

        elif self.heightmap_array is not None:

            if self._clip_window_set:
                self._sync_clip_slider()
            else:
                self._reset_clip_window()

        self._update_preview()

    def _on_clip_mode_changed(self, _index: int):

        if self.heightmap_array is None or not self.clip_checkbox.isChecked():
            return

        width = None

        if self._clip_window_set:
            width = self.clip_max_input.value() - self.clip_min_input.value()

        self._reset_clip_window(width)

        self._update_preview()

    def _on_clip_spin_changed(self, *_):

        low = self.clip_min_input.value()
        high = self.clip_max_input.value()

        if high - low < MIN_WINDOW_M:

            if low + MIN_WINDOW_M <= GAME_MAX_M:
                high = low + MIN_WINDOW_M
            else:
                low = high - MIN_WINDOW_M

            self._set_clip_window(low, high)

        else:

            self._clip_window_set = True
            self._sync_clip_slider()

        self._update_preview()

    def _on_clip_slider_changed(self, value: int):

        if self.heightmap_array is None:
            return

        width = self.clip_max_input.value() - self.clip_min_input.value()

        first, last = window_slider_range(width)

        low = round(first + (last - first) * value / CLIP_SLIDER_STEPS)
        low = min(max(low, GAME_MIN_M), GAME_MAX_M - width)

        self._set_clip_window(low, low + width)

        self._update_preview()

    def _update_clip_report_label(self):

        report = self._clip_report

        if report is None:
            self.clip_report_label.setText("")
            return

        text = describe_report(report)

        water_level = self.water_level_input.value()

        if not report.window_min_m <= water_level <= report.window_max_m:
            text += (
                tr("\nAchtung: Die Wasserhöhe liegt außerhalb des Fensters, "
                "die Flüsse wären im Spiel trocken oder die ganze Karte läge "
                "unter Wasser.")
            )

        self.clip_report_label.setText(text)

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
            and not self.clip_checkbox.isChecked()
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

        # Mit Hoehenfenster bestimmt das Fenster den Bereich, die Auswahl entfaellt.
        if self.clip_checkbox.isChecked():
            checkbox.setVisible(False)
            return

        checkbox.blockSignals(True)

        if suggestion.outlier_count > 0:

            checkbox.setText(
                tr(
                    "Ausreißer aus Höhenbereich ausschließen "
                    "({count} Pixel, {percent:.2f}% der Fläche erkannt)"
                ).format(
                    count=suggestion.outlier_count,
                    percent=suggestion.outlier_fraction * 100,
                )
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

        return tr(" oder ").join(size.label for size in matches)

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
                tr(
                    "Im TPF3-Import eintragen (auf Wasserhöhe 0 bezogen): "
                    "Mindesthöhe {low:.0f}, Maximalhöhe {high:.0f}, Wasserhöhe 0"
                ).format(low=range_min - water, high=range_max - water),
            ]

        else:

            lines = [
                tr(
                    "Im TPF3-Import eintragen: Mindesthöhe {low:.0f}, "
                    "Maximalhöhe {high:.0f}, Wasserhöhe {water:.0f}"
                ).format(low=range_min, high=range_max, water=water),
            ]

        size_hint = self._game_size_hint()

        if size_hint:
            lines.append(tr("Kartengröße und -format im Spiel: {size}").format(
                             size=size_hint
                         ))

        hint = height_hint(
            range_min,
            range_max,
            water,
            self.relative_values_checkbox.isChecked(),
        )

        if hint:
            lines.append(hint)

        offset = water if self.relative_values_checkbox.isChecked() else 0.0

        warning = limit_warning(range_min - offset, range_max - offset)

        if warning:
            lines.append(warning)

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

        if self.clip_checkbox.isChecked():
            self._sync_clip_slider()

        self._update_clip_report_label()

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
            original_heightmap=(
                self._unclipped_heightmap()
                if self._clip_report is not None
                else None
            ),
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
            tr("Heightmap exportieren"),
            default_name,
            tr("PNG-Bilder (*.png)")
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
                tr("Export fehlgeschlagen"),
                str(exc)
            )
            return

        if self.project is not None:
            self.project.mark_heightmap_exported(filename)

        outlier_warning = ""

        if (
            self.exclude_outliers_checkbox.isChecked()
            and not self.clip_checkbox.isChecked()
        ):

            outlier_warning = (
                tr(
                    "\n\nHinweis: Die {count} als Ausreißer erkannten Pixel "
                    "liegen außerhalb dieses Bereichs und wurden dadurch auf den "
                    "Rand geklemmt (0 bzw. 65535) - deren echte Höhe geht im "
                    "Export verloren."
                ).format(count=self._active_suggestion().outlier_count)
            )

        slope_note = ""

        if self.slope_checkbox.isChecked():

            slope_note = (
                tr(
                    "\n\nGefälle-Ausgleich aktiv (Stärke {strength:.0f} %, "
                    "Glättung {smoothing:.0f} m): Flüsse und Seen wurden auf "
                    "eine gemeinsame Ebene gelegt, das Gelände relativ dazu "
                    "angepasst - die absoluten Höhen ü. NN stimmen dadurch nicht "
                    "mehr."
                ).format(
                    strength=self.slope_strength_input.value(),
                    smoothing=self.slope_smoothing_input.value(),
                )
            )

        flatten_note = ""

        if self.flatten_checkbox.isChecked():

            flatten_note = (
                tr(
                    "\n\nTrassen und Siedlungen eingeebnet ({sigma:.0f} m)."
                ).format(sigma=self.flatten_sigma_input.value())
            )

        compress_note = ""

        if self.compress_input.value() < 100.0:

            compress_note = (
                tr(
                    "\n\nHöhen über dem Wasserspiegel auf {percent:.0f} % "
                    "gestaucht."
                ).format(percent=self.compress_input.value())
            )

        smooth_note = ""

        if self.smooth_checkbox.isChecked():

            smooth_note = (
                tr("\n\nGelände geglättet ({sigma:.0f} m).").format(
                    sigma=self.smooth_sigma_input.value()
                )
            )

        enforce_note = ""

        if self.enforce_checkbox.isChecked():

            enforce_note = (
                tr(
                    "\n\nWasser nur dort, wo OpenStreetMap Wasser hat: "
                    "Flussbett {edge:.0f} m (Ufer) bis {depth:.0f} m (Mitte) "
                    "unter dem Wasserspiegel, Land mindestens {bank:.1f} m "
                    "darüber, Böschung {transition:.0f} m."
                ).format(
                    edge=self.enforce_edge_input.value(),
                    depth=self.enforce_depth_input.value(),
                    bank=self.enforce_bank_input.value(),
                    transition=self.enforce_transition_input.value(),
                )
            )

        water_blend_note = ""

        if self.water_blend_checkbox.isChecked():

            water_blend_note = (
                tr(
                    "\n\nDas Terrain wurde um Gewässer herum (Übergang "
                    "{transition:.0f} m) sanft ans Wasserniveau angepasst - "
                    "weicht dort geringfügig von den echten Höhendaten ab."
                ).format(transition=self.transition_input.value())
            )

        clip_note = ""

        if self._clip_report is not None:

            clip_note = (
                tr(
                    "\n\nHöhenfenster {low:.0f} bis {high:.0f} m: {report}"
                ).format(
                    low=self._clip_report.window_min_m,
                    high=self._clip_report.window_max_m,
                    report=describe_report(self._clip_report),
                )
            )

        QMessageBox.information(
            self,
            tr("Export abgeschlossen"),
            tr("Heightmap gespeichert unter:\n{filename}\n\n").format(
                filename=filename
            ) + (
                self._game_values_text()
                + outlier_warning
                + smooth_note
                + flatten_note
                + compress_note
                + slope_note
                + enforce_note
                + water_blend_note
                + clip_note
            )
        )