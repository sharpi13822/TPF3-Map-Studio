"""
Heightmap-Export fuer TPF2, direkt aus einer (ggf. gedrehten) Selection.

Nutzt bewusst TPF2Geometry fuer die Drehung/Projektion (statt einer
zweiten, eigenen Implementierung) - damit Gelaende und die per
TPF2Exporter exportierten Strassen/Gleise garantiert exakt zueinander
passen. Waeren das zwei unabhaengige Rechnungen, koennten sie leicht
gegeneinander verschoben sein.
"""

from __future__ import annotations

import os
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from src.map.objects.selection import Selection
from src.tpf2.tpf2_geometry import TPF2Geometry
from src.heightmap.height_clipping import normalize_heights
from src.heightmap.copernicus_dem import DemMosaic, download_tiles_for_selection
from src.heightmap.dgm1_dem import Dgm1Error, Dgm1Mosaic
from src.heightmap.swissalti3d_dem import required_swiss_tiles
from src.heightmap.bev_dem import BevMosaic
from src.heightmap.lux_dem import LuxMosaic
from src.heightmap.ahn_nl_dem import required_ahn_tiles
from src.core.task_control import TaskControl
from src.i18n import tr

METERS_PER_PIXEL = 4.0

# Hoehenquellen
SOURCE_COPERNICUS = "copernicus"
SOURCE_DGM1_DE = "dgm1_de"          # Kacheln ueber hoehendaten.de (Zwischenspeicher)
SOURCE_DGM1_FOLDER = "dgm1_folder"  # selbst heruntergeladene GeoTIFF-Kacheln
SOURCE_SWISSALTI3D = "swissalti3d"  # swissALTI3D (Schweiz), Kacheln von data.geo.admin.ch
SOURCE_AHN_NL = "ahn_nl"            # AHN (Niederlande), Kacheln von PDOK
SOURCE_BEV_AT = "bev_at"            # BEV (Oesterreich), ALS-DTM 1 m, Teilabruf per HTTP-Range
SOURCE_LUX = "lux_mnt"              # Luxemburg, MNT Lidar 2024 (0,5 m), Teilabruf per HTTP-Range
SOURCE_TPF2_PNG = "tpf2_png"        # eigene TPF2-Heightmap (16-Bit-PNG)


@dataclass
class HeightmapBuildInfo:
    """Woher die Hoehen eines fertigen Rasters stammen."""

    source: str = SOURCE_COPERNICUS
    # Anteil der Pixel, die statt aus DGM1 aus Copernicus ergaenzt wurden (0..1)
    fallback_fraction: float = 0.0
    # Zahl der 1-km-Kacheln ohne DGM1-Daten im Ausschnitt
    missing_tiles: int = 0
    attributions: list[str] = field(default_factory=list)
    # Datenstand der Kacheln (Ausgabe-/Befliegungsdatum laut Anbieter, als Text)
    actualities: list[str] = field(default_factory=list)
    # Pixel ohne Hoehendaten im offenen Meer (Copernicus), sonst None
    sea_mask: object = None


class _FallbackMosaic:
    """DGM1 mit Copernicus als Ergaenzung dort, wo keine DGM1-Daten vorliegen."""

    def __init__(self, primary, make_fallback):
        self.primary = primary
        self._make_fallback = make_fallback
        self._fallback = None
        self._lock = threading.Lock()
        self._workers = 1
        self.total_pixels = 0
        self.fallback_pixels = 0

    @property
    def parallel_safe(self) -> bool:
        # Copernicus als Ergaenzung ist thread-sicher; es kommt auf DGM1 & Co. an.
        return bool(getattr(self.primary, "parallel_safe", False))

    def prepare_parallel(self, workers: int):
        self._workers = int(workers)

        if hasattr(self.primary, "prepare_parallel"):
            self.primary.prepare_parallel(workers)

    def _get_fallback(self):
        # Nur ein Thread legt das (Download-)Ergaenzungs-Mosaik an.
        with self._lock:
            if self._fallback is None:
                self._fallback = self._make_fallback()
                if hasattr(self._fallback, "prepare_parallel"):
                    self._fallback.prepare_parallel(self._workers)
            return self._fallback

    def sample_grid(self, lat, lon):
        out = self.primary.sample_grid(lat, lon)

        hole = np.isnan(out)
        holes = int(hole.sum())

        with self._lock:
            self.total_pixels += out.size
            self.fallback_pixels += holes

        if holes:
            out[hole] = self._get_fallback().sample_grid(lat[hole], lon[hole])

        return out


def open_sea_mask(heights: np.ndarray, min_pixels: int = 100000) -> np.ndarray:
    """Grosse Flaechen mit exakt 0 m: offenes Meer (Copernicus setzt das Meer auf 0)."""

    from scipy.ndimage import label

    zero = heights == 0.0
    if not zero.any():
        return np.zeros(heights.shape, dtype=bool)

    labels, count = label(zero)
    if count == 0:
        return np.zeros(heights.shape, dtype=bool)

    sizes = np.bincount(labels.ravel())
    big = sizes >= min_pixels
    big[0] = False
    return big[labels]


def pixel_size_for_selection(selection: Selection) -> tuple[int, int]:
    """Pixelgroesse (Breite, Hoehe), passend zu TPF2s (meters/4)+1-Regel."""
    w_px = round(selection.width_m / METERS_PER_PIXEL) + 1
    h_px = round(selection.height_m / METERS_PER_PIXEL) + 1
    return w_px, h_px


# Hoehenmodelle sind etwa 30 m fein. Bei gestauchter Karte liegt zwischen
# zwei Rasterpunkten ein Vielfaches davon; ohne Mittelung wuerden Haenge
# ausfransen.
DEM_RESOLUTION_M = 30.0
# Hoechstzahl Abfragepunkte je Abruf (Speicher je Arbeits-Thread, grob 100 Byte/Punkt)
MAX_POINTS_PER_CALL = 6_000_000
MAX_OVERSAMPLE = 3


def oversample_for_selection(selection: Selection) -> int:
    """Teilpunkte je Achse und Rasterpixel (1 = keine Mittelung)."""

    scale = float(getattr(selection, "scale_factor", 1.0) or 1.0)
    pitch_real_m = METERS_PER_PIXEL * scale

    if pitch_real_m <= DEM_RESOLUTION_M:
        return 1

    return int(min(MAX_OVERSAMPLE, np.ceil(pitch_real_m / DEM_RESOLUTION_M)))


def _apply_height_scale(heights: np.ndarray, selection: Selection) -> np.ndarray:
    """Skaliert alle Hoehen mit selection.height_scale (1.0 = unveraendert)."""

    factor = float(getattr(selection, "height_scale", 1.0) or 1.0)

    if abs(factor - 1.0) < 1e-9:
        return heights

    return (heights * np.float32(factor)).astype(np.float32, copy=False)


def _worker_count_for(mosaic) -> int:
    """Arbeits-Threads fuer das Abtasten: nur, wenn die Quelle das vertraegt."""

    if not getattr(mosaic, "parallel_safe", False):
        return 1

    return max(1, min(4, os.cpu_count() or 1))


def _sample_grid(
    selection: Selection,
    mosaic: DemMosaic,
    w_px: int,
    h_px: int,
    chunk: int = 300,
    oversample: int = 1,
    control: TaskControl | None = None,
    workers: int | None = None,
) -> np.ndarray:
    """
    Gemeinsame Kernrechnung fuer build_heightmap_array() und
    build_heightmap_array_preview(): tastet das (ggf. gedrehte) Band mit
    genau w_px x h_px Punkten ab. Bei kleinem w_px/h_px (Vorschau)
    braucht es dank chunk keine Anpassung - eine einzelne Runde durch
    die Schleife reicht dann ohnehin.

    Je Zeilenstreifen werden ALLE Teilpunkte der Mittelung (oversample^2)
    in einem einzigen Abruf abgefragt: so wird jede Hoehenkachel pro Streifen
    nur einmal geladen (frueher bis zu neun Mal, weil der Kachel-Speicher
    nur wenige Kacheln fasst). Die Streifen laufen, wenn die Quelle es
    erlaubt (parallel_safe), auf mehreren Kernen. control (optional) meldet
    den Fortschritt und kann abbrechen (TaskCancelled).
    """

    center_lat, center_lon = selection.center
    scale = float(getattr(selection, "scale_factor", 1.0) or 1.0)
    geometry = TPF2Geometry(
        center_lat, center_lon, selection.rotation_deg, scale
    )

    # Das Raster ist in Spielkarten-Metern definiert; abgetastet wird die
    # reale Flaeche (scale mal groesser). Bei scale == 1 wie bisher.
    hx, hy = selection.width_m / 2, selection.height_m / 2
    pitch_x = selection.width_m / w_px
    pitch_y = selection.height_m / h_px

    n_sub = max(1, int(oversample))
    offsets = [(k + 0.5) / n_sub - 0.5 for k in range(n_sub)]

    out = np.zeros((h_px, w_px), dtype=np.float32)
    cols = np.arange(w_px)

    n_workers = workers if workers is not None else _worker_count_for(mosaic)
    n_workers = max(1, int(n_workers))

    if n_workers > 1 and hasattr(mosaic, "prepare_parallel"):
        mosaic.prepare_parallel(n_workers)

    # Streifenhoehe so waehlen, dass ein Abruf (alle Teilpunkte) nicht zu viel
    # Arbeitsspeicher braucht: bei neunfacher Mittelung entsprechend flacher.
    chunk = max(32, min(chunk, MAX_POINTS_PER_CALL // max(1, w_px * n_sub * n_sub)))

    starts = list(range(0, h_px, chunk))
    finished = [0]

    def do_chunk(r0):

        if control is not None:
            control.check()

        r1 = min(h_px, r0 + chunk)
        rows = np.arange(r0, r1)

        lats = []
        lons = []

        for oy in offsets:
            y_local = (hy - (rows + 0.5 + oy) * pitch_y) * scale

            for ox in offsets:
                x_local = (-hx + (cols + 0.5 + ox) * pitch_x) * scale
                xl, yl = np.meshgrid(x_local, y_local)

                # Vektorisiert dieselbe Rechnung wie TPF2Geometry.inverse(),
                # da diese nur einzelne Punkte kann.
                e = geometry.right_vector[0] * xl + geometry.up_vector[0] * yl
                n = geometry.right_vector[1] * xl + geometry.up_vector[1] * yl
                lats.append(center_lat + n / geometry.METERS_PER_DEGREE_LAT)
                lons.append(center_lon + e / geometry.longitude_scale)

        # Ein Abruf fuer alle Teilpunkte: (n_sub^2, Zeilen, Spalten)
        values = np.asarray(
            mosaic.sample_grid(np.stack(lats), np.stack(lons)), dtype=np.float32
        )

        acc = values[0].copy()

        for k in range(1, values.shape[0]):
            acc += values[k]

        if n_sub > 1:
            acc /= np.float32(n_sub * n_sub)

        out[r0:r1, :] = acc

        finished[0] += 1

        if control is not None:
            control.report(finished[0] / len(starts))

    if n_workers <= 1 or len(starts) == 1:
        for r0 in starts:
            do_chunk(r0)
    else:
        with ThreadPoolExecutor(max_workers=n_workers) as pool:
            futures = [pool.submit(do_chunk, r0) for r0 in starts]
            try:
                for f in futures:
                    f.result()
            except BaseException:
                for f in futures:
                    f.cancel()
                raise

    return out


def build_heightmap_array_ex(
    selection: Selection,
    cache_dir: Path,
    source: str = SOURCE_COPERNICUS,
    dgm1_cache_dir: Path | None = None,
    dgm1_folder: Path | None = None,
    swiss_cache_dir: Path | None = None,
    ahn_cache_dir: Path | None = None,
    tpf2_png: Path | None = None,
    tpf2_low_m: float = 0.0,
    tpf2_high_m: float = 0.0,
    bev_cache_dir: Path | None = None,
    lux_cache_dir: Path | None = None,
    control: TaskControl | None = None,
) -> tuple[np.ndarray, HeightmapBuildInfo]:
    """
    Wie build_heightmap_array(), waehlt aber die Hoehenquelle und liefert
    zusaetzlich eine Info, woher die Hoehen stammen.

    SOURCE_DGM1_DE liest nur bereits geladene Kacheln aus dgm1_cache_dir (der
    Abruf laeuft vorher ueber dgm1_dem.fetch_tiles_for_selection bzw.
    Dgm1FetchJob); SOURCE_DGM1_FOLDER liest die GeoTIFF-Dateien aus dgm1_folder.
    SOURCE_SWISSALTI3D liest die bereits geladenen swissALTI3D-Kacheln aus swiss_cache_dir
    (Abruf vorher ueber swissalti3d_dem.SwissFetchJob).
    Wo DGM1- oder swissALTI3D-Daten fehlen, wird aus Copernicus ergaenzt.
    """

    w_px, h_px = pixel_size_for_selection(selection)

    if source == SOURCE_COPERNICUS:

        tile_paths = download_tiles_for_selection(selection, cache_dir)
        mosaic = DemMosaic.from_paths(tile_paths)

        out = _sample_grid(
            selection, mosaic, w_px, h_px,
            oversample=oversample_for_selection(selection),
            control=control,
        )

        # Copernicus hat fuer offenes Meer keine Kacheln (404). Solche
        # Luecken sind Wasser auf Meereshoehe, kein Fehler.
        sea = np.isnan(out)
        out = np.nan_to_num(out, nan=0.0)
        sea |= open_sea_mask(out)

        info = HeightmapBuildInfo(
            source=source,
            sea_mask=sea if sea.any() else None,
        )

    elif source == SOURCE_TPF2_PNG:

        from src.heightmap.tpf2_heightmap_import import load_tpf2_heightmap
        from src.heightmap.tpf2_png_dem import Tpf2PngMosaic, Tpf2PngSizeError

        if tpf2_png is None:
            raise Dgm1Error(tr("Keine TPF2-Heightmap angegeben."))

        png = load_tpf2_heightmap(tpf2_png)

        if png.raw.shape != (h_px, w_px):
            raise Tpf2PngSizeError(
                tr("Die PNG ({w} x {h} Pixel) passt nicht zum Rechteck ({bw} x {bh} Pixel).").format(
                    w=png.raw.shape[1], h=png.raw.shape[0], bw=w_px, bh=h_px
                )
            )

        c_lat, c_lon = selection.center
        scale = float(getattr(selection, "scale_factor", 1.0) or 1.0)
        mosaic = Tpf2PngMosaic(
            png.raw, tpf2_low_m, tpf2_high_m,
            TPF2Geometry(c_lat, c_lon, selection.rotation_deg, scale),
            (c_lat, c_lon), selection.width_m, selection.height_m, scale,
        )

        out = _sample_grid(selection, mosaic, w_px, h_px, control=control)

        info = HeightmapBuildInfo(source=source)

    elif source in (SOURCE_DGM1_DE, SOURCE_DGM1_FOLDER, SOURCE_SWISSALTI3D, SOURCE_AHN_NL, SOURCE_BEV_AT, SOURCE_LUX):

        if source == SOURCE_DGM1_DE:
            if dgm1_cache_dir is None:
                raise Dgm1Error("Kein Zwischenspeicher fuer DGM1-Kacheln angegeben.")
            dgm1 = Dgm1Mosaic.from_cache(selection, dgm1_cache_dir, METERS_PER_PIXEL)
        elif source == SOURCE_SWISSALTI3D:
            if swiss_cache_dir is None:
                raise Dgm1Error("Kein Zwischenspeicher fuer swissALTI3D-Kacheln angegeben.")
            dgm1 = Dgm1Mosaic.from_cache(
                selection,
                swiss_cache_dir,
                METERS_PER_PIXEL,
                tiles=required_swiss_tiles(selection),
            )
        elif source == SOURCE_BEV_AT:
            if bev_cache_dir is None:
                raise Dgm1Error("Kein Zwischenspeicher fuer BEV-Kacheln angegeben.")
            dgm1 = BevMosaic.from_cache(selection, bev_cache_dir)
        elif source == SOURCE_LUX:
            if lux_cache_dir is None:
                raise Dgm1Error("Kein Zwischenspeicher fuer Luxemburg-Kacheln angegeben.")
            dgm1 = LuxMosaic.from_cache(selection, lux_cache_dir)
        elif source == SOURCE_AHN_NL:
            if ahn_cache_dir is None:
                raise Dgm1Error("Kein Zwischenspeicher fuer AHN-Kacheln angegeben.")
            dgm1 = Dgm1Mosaic.from_cache(
                selection,
                ahn_cache_dir,
                METERS_PER_PIXEL,
                tiles=required_ahn_tiles(selection),
            )
        else:
            if dgm1_folder is None:
                raise Dgm1Error(tr("Kein Ordner mit DGM1-Kacheln angegeben."))
            dgm1 = Dgm1Mosaic.from_folder(selection, dgm1_folder, METERS_PER_PIXEL)

        if dgm1.slot_count == 0:
            if source == SOURCE_BEV_AT:
                raise Dgm1Error(
                    tr("Keine BEV-Kacheln fuer diesen Ausschnitt gefunden. Liegt der "
                    "Ausschnitt ausserhalb Oesterreichs, bitte Copernicus waehlen.")
                )
            if source == SOURCE_LUX:
                raise Dgm1Error(
                    tr("Keine Luxemburg-Kacheln fuer diesen Ausschnitt gefunden. Liegt der "
                    "Ausschnitt ausserhalb Luxemburgs, bitte Copernicus waehlen.")
                )
            if source == SOURCE_AHN_NL:
                raise Dgm1Error(tr("Keine AHN-Kacheln fuer diesen Ausschnitt gefunden. Liegt der Ausschnitt ausserhalb der Niederlande, bitte Copernicus waehlen."))
            if source == SOURCE_SWISSALTI3D:
                raise Dgm1Error(
                    tr("Keine swissALTI3D-Kacheln fuer diesen Ausschnitt gefunden. Liegt der "
                    "Ausschnitt ausserhalb der Schweiz und Liechtensteins, bitte Copernicus waehlen.")
                )
            raise Dgm1Error(
                tr("Keine DGM1-Kacheln fuer diesen Ausschnitt gefunden. Liegt der Ausschnitt "
                "ausserhalb Deutschlands, bitte Copernicus waehlen.")
            )

        def make_fallback():
            paths = download_tiles_for_selection(selection, cache_dir)
            return DemMosaic.from_paths(paths)

        mosaic = _FallbackMosaic(dgm1, make_fallback)

        out = _sample_grid(
            selection, mosaic, w_px, h_px,
            oversample=oversample_for_selection(selection),
            control=control,
        )

        info = HeightmapBuildInfo(
            source=source,
            fallback_fraction=(
                mosaic.fallback_pixels / mosaic.total_pixels if mosaic.total_pixels else 0.0
            ),
            missing_tiles=dgm1.missing_slots,
            attributions=list(dgm1.attributions),
            actualities=list(dgm1.actualities),
        )

    else:
        raise ValueError(f"Unbekannte Hoehenquelle: {source}")

    if np.isnan(out).any():
        raise RuntimeError(
            tr("Hoehendaten decken den Kartenausschnitt nicht vollstaendig ab "
            "(evtl. fehlt eine Randkachel).")
        )

    out = _apply_height_scale(out, selection)

    return out, info


def build_heightmap_array(
    selection: Selection,
    cache_dir: Path,
) -> np.ndarray:
    """Laedt die noetigen Copernicus-DEM-Kacheln und liefert das fertige,
    gedrehte/zugeschnittene Hoehenraster als 2D-numpy-Array (Meter), in
    voller Export-Aufloesung (4 m/Pixel)."""

    out, _info = build_heightmap_array_ex(selection, cache_dir, SOURCE_COPERNICUS)

    return out


def build_heightmap_array_preview(
    selection: Selection,
    cache_dir: Path,
    max_dimension_px: int = 300,
) -> np.ndarray:
    """
    Schnelle Vorschau VOR dem eigentlichen (oft langsamen) vollaufloesenden
    Download: laedt dieselben Copernicus-Kacheln wie build_heightmap_array()
    (das ist der unvermeidliche Netzwerk-Anteil - der laesst sich nicht
    verkleinern, ohne die Daten zu verlieren), tastet das Band aber nur mit
    max_dimension_px Punkten auf der laengeren Seite ab statt in voller
    4m/Pixel-Aufloesung. Dadurch faellt die aufwendige Abtast-Rechnung
    (bei "Groessenwahnsinnig"-Baendern sonst zig Millionen Punkte) auf ein
    paar Zehntausend Punkte - praktisch sofort fertig.

    Netter Nebeneffekt: die hier geladenen Kacheln liegen danach im Cache,
    ein anschliessender echter Download (build_heightmap_array) laedt dann
    nichts mehr neu herunter.
    """

    tile_paths = download_tiles_for_selection(selection, cache_dir)
    mosaic = DemMosaic.from_paths(tile_paths)

    aspect = selection.height_m / selection.width_m if selection.width_m else 1.0

    if selection.width_m >= selection.height_m:
        w_px = max_dimension_px
        h_px = max(1, round(max_dimension_px * aspect))
    else:
        h_px = max_dimension_px
        w_px = max(1, round(max_dimension_px / aspect)) if aspect else max_dimension_px

    out = _sample_grid(selection, mosaic, w_px, h_px, chunk=max(h_px, 1))

    return _apply_height_scale(out, selection)


def export_heightmap_png(
    heightmap: np.ndarray,
    output_path: Path,
    range_min_m: float,
    range_max_m: float,
) -> None:
    """Exportiert das Hoehenraster als 16-Bit-Graustufen-PNG, wie es der
    TPF2-Karteneditor erwartet."""

    from PIL import Image

    norm = normalize_heights(heightmap, range_min_m, range_max_m)
    img16 = (norm * 65535).astype(np.uint16)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img16).save(output_path)