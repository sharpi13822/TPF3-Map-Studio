"""
Heightmap-Export fuer TPF2, direkt aus einer (ggf. gedrehten) Selection.

Nutzt bewusst TPF2Geometry fuer die Drehung/Projektion (statt einer
zweiten, eigenen Implementierung) - damit Gelaende und die per
TPF2Exporter exportierten Strassen/Gleise garantiert exakt zueinander
passen. Waeren das zwei unabhaengige Rechnungen, koennten sie leicht
gegeneinander verschoben sein.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from src.map.objects.selection import Selection
from src.tpf2.tpf2_geometry import TPF2Geometry
from src.heightmap.height_clipping import normalize_heights
from src.heightmap.copernicus_dem import DemMosaic, download_tiles_for_selection
from src.heightmap.dgm1_dem import Dgm1Error, Dgm1Mosaic
from src.heightmap.swissalti3d_dem import required_swiss_tiles

METERS_PER_PIXEL = 4.0

# Hoehenquellen
SOURCE_COPERNICUS = "copernicus"
SOURCE_DGM1_DE = "dgm1_de"          # Kacheln ueber hoehendaten.de (Zwischenspeicher)
SOURCE_DGM1_FOLDER = "dgm1_folder"  # selbst heruntergeladene GeoTIFF-Kacheln
SOURCE_SWISSALTI3D = "swissalti3d"  # swissALTI3D (Schweiz), Kacheln von data.geo.admin.ch


@dataclass
class HeightmapBuildInfo:
    """Woher die Hoehen eines fertigen Rasters stammen."""

    source: str = SOURCE_COPERNICUS
    # Anteil der Pixel, die statt aus DGM1 aus Copernicus ergaenzt wurden (0..1)
    fallback_fraction: float = 0.0
    # Zahl der 1-km-Kacheln ohne DGM1-Daten im Ausschnitt
    missing_tiles: int = 0
    attributions: list[str] = field(default_factory=list)


class _FallbackMosaic:
    """DGM1 mit Copernicus als Ergaenzung dort, wo keine DGM1-Daten vorliegen."""

    def __init__(self, primary, make_fallback):
        self.primary = primary
        self._make_fallback = make_fallback
        self._fallback = None
        self.total_pixels = 0
        self.fallback_pixels = 0

    def sample_grid(self, lat, lon):
        out = self.primary.sample_grid(lat, lon)

        self.total_pixels += out.size

        hole = np.isnan(out)

        if hole.any():
            if self._fallback is None:
                self._fallback = self._make_fallback()
            out[hole] = self._fallback.sample_grid(lat[hole], lon[hole])
            self.fallback_pixels += int(hole.sum())

        return out


def pixel_size_for_selection(selection: Selection) -> tuple[int, int]:
    """Pixelgroesse (Breite, Hoehe), passend zu TPF2s (meters/4)+1-Regel."""
    w_px = round(selection.width_m / METERS_PER_PIXEL) + 1
    h_px = round(selection.height_m / METERS_PER_PIXEL) + 1
    return w_px, h_px


def _sample_grid(
    selection: Selection,
    mosaic: DemMosaic,
    w_px: int,
    h_px: int,
    chunk: int = 300,
) -> np.ndarray:
    """
    Gemeinsame Kernrechnung fuer build_heightmap_array() und
    build_heightmap_array_preview(): tastet das (ggf. gedrehte) Band mit
    genau w_px x h_px Punkten ab. Bei kleinem w_px/h_px (Vorschau)
    braucht es dank chunk keine Anpassung - eine einzelne Runde durch
    die Schleife reicht dann ohnehin.
    """

    center_lat, center_lon = selection.center
    geometry = TPF2Geometry(center_lat, center_lon, selection.rotation_deg)

    hx, hy = selection.width_m / 2, selection.height_m / 2

    out = np.zeros((h_px, w_px), dtype=np.float32)
    cols = np.arange(w_px)
    x_local = -hx + (cols + 0.5) * (selection.width_m / w_px)

    for r0 in range(0, h_px, chunk):
        r1 = min(h_px, r0 + chunk)
        rows = np.arange(r0, r1)
        y_local = hy - (rows + 0.5) * (selection.height_m / h_px)
        xl, yl = np.meshgrid(x_local, y_local)

        # Vektorisiert dieselbe Rechnung wie TPF2Geometry.inverse(),
        # da diese nur einzelne Punkte kann.
        e = geometry.right_vector[0] * xl + geometry.up_vector[0] * yl
        n = geometry.right_vector[1] * xl + geometry.up_vector[1] * yl
        lat = center_lat + n / geometry.METERS_PER_DEGREE_LAT
        lon = center_lon + e / geometry.longitude_scale

        out[r0:r1, :] = mosaic.sample_grid(lat, lon)

    return out


def build_heightmap_array_ex(
    selection: Selection,
    cache_dir: Path,
    source: str = SOURCE_COPERNICUS,
    dgm1_cache_dir: Path | None = None,
    dgm1_folder: Path | None = None,
    swiss_cache_dir: Path | None = None,
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

        out = _sample_grid(selection, mosaic, w_px, h_px)

        info = HeightmapBuildInfo(source=source)

    elif source in (SOURCE_DGM1_DE, SOURCE_DGM1_FOLDER, SOURCE_SWISSALTI3D):

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
        else:
            if dgm1_folder is None:
                raise Dgm1Error("Kein Ordner mit DGM1-Kacheln angegeben.")
            dgm1 = Dgm1Mosaic.from_folder(selection, dgm1_folder, METERS_PER_PIXEL)

        if dgm1.slot_count == 0:
            if source == SOURCE_SWISSALTI3D:
                raise Dgm1Error(
                    "Keine swissALTI3D-Kacheln fuer diesen Ausschnitt gefunden. Liegt der "
                    "Ausschnitt ausserhalb der Schweiz und Liechtensteins, bitte Copernicus waehlen."
                )
            raise Dgm1Error(
                "Keine DGM1-Kacheln fuer diesen Ausschnitt gefunden. Liegt der Ausschnitt "
                "ausserhalb Deutschlands, bitte Copernicus waehlen."
            )

        def make_fallback():
            paths = download_tiles_for_selection(selection, cache_dir)
            return DemMosaic.from_paths(paths)

        mosaic = _FallbackMosaic(dgm1, make_fallback)

        out = _sample_grid(selection, mosaic, w_px, h_px)

        info = HeightmapBuildInfo(
            source=source,
            fallback_fraction=(
                mosaic.fallback_pixels / mosaic.total_pixels if mosaic.total_pixels else 0.0
            ),
            missing_tiles=dgm1.missing_slots,
            attributions=list(dgm1.attributions),
        )

    else:
        raise ValueError(f"Unbekannte Hoehenquelle: {source}")

    if np.isnan(out).any():
        raise RuntimeError(
            "Hoehendaten decken den Kartenausschnitt nicht vollstaendig ab "
            "(evtl. fehlt eine Randkachel)."
        )

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

    return out


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