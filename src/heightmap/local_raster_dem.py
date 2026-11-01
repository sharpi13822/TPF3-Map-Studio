"""
Eigene Hoehendateien (GeoTIFF und ASC) aus beliebigen Laendern als Hoehenquelle.

Liest alle .tif/.tiff/.asc-Dateien eines Ordners (auch Unterordner), erkennt das
Koordinatensystem (GeoTIFF-Schluessel, .prj-Datei, Dateiname oder eine Datei
epsg.txt im Ordner), laedt nur Dateien, die das Rechteck beruehren, und
verkleinert sehr feine Daten (1 m) auf etwa 2 m, damit der Speicher reicht.
Die Kacheln duerfen beliebig gross und gegeneinander verschoben sein.

sample_grid(lat, lon) liefert Hoehen (NaN ausserhalb), wie die anderen Mosaike.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from src.heightmap import asc_import
from src.heightmap.crs import UnknownCrsError, epsg_from_text, get_crs

RASTER_SUFFIXES = (".tif", ".tiff", ".asc")
TARGET_CELL_M = 2.0       # feinere Daten werden auf etwa diese Zellgroesse gemittelt
MARGIN_M = 500.0
VALID_MIN_M = -500.0
VALID_MAX_M = 9000.0
DGM1_EPSG = (25832, 25833)

Image.MAX_IMAGE_PIXELS = None  # grosse Hoehenmodelle sind erwuenscht


class LocalRasterError(RuntimeError):
    """Eigene Hoehendateien konnten nicht gelesen werden."""


@dataclass
class _Header:
    path: Path
    kind: str            # "tif" oder "asc"
    epsg: int | None
    left: float
    top: float
    cell_x: float
    cell_y: float
    cols: int
    rows: int

    @property
    def right(self):
        return self.left + self.cols * self.cell_x

    @property
    def bottom(self):
        return self.top - self.rows * self.cell_y


@dataclass
class _Raster:
    h: np.ndarray
    crs: object
    left: float
    top: float
    cell_x: float
    cell_y: float
    path: Path = None


# ---------------------------------------------------------------------------
# Kopfdaten
# ---------------------------------------------------------------------------

def raster_files(folder) -> list[Path]:
    return sorted(
        p for p in Path(folder).rglob("*")
        if p.is_file() and p.suffix.lower() in RASTER_SUFFIXES and not p.name.endswith(".tmp")
    )


def _folder_epsg(folder) -> int | None:
    for name in ("epsg.txt", "EPSG.txt", "epsg.TXT"):
        f = Path(folder) / name
        if f.is_file():
            text = f.read_text(encoding="utf-8", errors="replace")
            digits = "".join(ch for ch in text if ch.isdigit())
            return int(digits) if digits else None
    return None


def _geokeys(tags) -> dict:
    raw = tags.get(34735)
    if not raw:
        return {}
    raw = list(raw)
    keys = {}
    try:
        count = int(raw[3])
        for i in range(count):
            key, loc, _cnt, val = raw[4 + 4 * i: 8 + 4 * i]
            if loc == 0:
                keys[int(key)] = int(val)
    except (IndexError, ValueError, TypeError):
        pass
    return keys


def _tif_header(path: Path) -> _Header:
    try:
        with Image.open(path) as img:
            tags = dict(img.tag_v2)
            cols, rows = img.size
    except Exception as exc:  # noqa: BLE001
        raise LocalRasterError(f"{path.name}: keine lesbare TIFF-Datei ({exc})") from exc

    scale = tags.get(33550)
    tie = tags.get(33922)
    matrix = tags.get(34264)

    if scale and tie:
        sx, sy = float(scale[0]), float(scale[1])
        i, j, x, y = float(tie[0]), float(tie[1]), float(tie[3]), float(tie[4])
        left, top = x - i * sx, y + j * sy
    elif matrix and len(matrix) >= 8:
        sx, sy = float(matrix[0]), -float(matrix[5])
        left, top = float(matrix[3]), float(matrix[7])
    else:
        raise LocalRasterError(f"{path.name}: die TIFF-Datei hat keine Geo-Angaben (keine GeoTIFF).")

    keys = _geokeys(tags)
    if keys.get(1025) == 2:          # PixelIsPoint: Wert gilt fuer die Pixelmitte
        left -= sx / 2.0
        top += sy / 2.0

    epsg = keys.get(3072) or None
    if epsg in (None, 32767):
        epsg = keys.get(2048) if keys.get(1024) == 2 else None
        if epsg == 32767:
            epsg = None
    if epsg is None:
        epsg = _epsg_from_side_files(path)

    return _Header(path, "tif", epsg, left, top, sx, sy, cols, rows)


def _epsg_from_side_files(path: Path) -> int | None:
    prj = path.with_suffix(".prj")
    if prj.is_file():
        found = epsg_from_text(prj.read_text(encoding="utf-8", errors="replace"))
        if found:
            return found
    return epsg_from_text(path.name) or epsg_from_text(path.parent.name)


def _asc_header(path: Path) -> _Header:
    with open(path, "r", encoding="ascii", errors="replace") as handle:
        head, _ = asc_import._read_header(handle)
    try:
        cols, rows, cell, x0, y0 = asc_import._geometry(head, path.name)
    except asc_import.AscImportError as exc:
        raise LocalRasterError(str(exc)) from exc
    return _Header(path, "asc", _epsg_from_side_files(path), x0, y0 + rows * cell, cell, cell, cols, rows)


def read_header(path) -> _Header:
    path = Path(path)
    return _asc_header(path) if path.suffix.lower() == ".asc" else _tif_header(path)


# ---------------------------------------------------------------------------
# Pixel lesen
# ---------------------------------------------------------------------------

def _tif_pixels(path: Path) -> np.ndarray:
    try:
        with Image.open(path) as img:
            tags = dict(img.tag_v2)
            arr = np.array(img, dtype=np.float32)
    except Exception as exc:  # noqa: BLE001
        raise LocalRasterError(
            f"{path.name}: Pixel nicht lesbar ({exc}). Bitte die Datei ohne Kompression oder mit "
            f"LZW/Deflate speichern."
        ) from exc
    if arr.ndim == 3:
        arr = arr[:, :, 0]
    nodata = tags.get(42113)
    if nodata not in (None, ""):
        try:
            arr[np.isclose(arr, float(str(nodata).strip("\x00 ")))] = np.nan
        except ValueError:
            pass
    return arr


def _downsample(arr: np.ndarray, cell: float, target: float):
    block = int(target // cell) if cell > 0 else 1
    if block < 2:
        return arr, 1
    total, count = asc_import._block_sums(arr, block)
    out = np.full(total.shape, np.nan, dtype=np.float32)
    ok = count > 0
    out[ok] = (total[ok] / count[ok]).astype(np.float32)
    return out, block


def load_raster(header: _Header, crs, target_cell: float = TARGET_CELL_M) -> _Raster:
    if header.kind == "asc":
        arr, _x0, _y0, _cell = asc_import.read_asc(header.path)
        arr = arr.astype(np.float32)
    else:
        arr = _tif_pixels(header.path)

    arr[(arr < VALID_MIN_M) | (arr > VALID_MAX_M)] = np.nan

    if crs.is_geographic:
        block = 1
    else:
        arr, block = _downsample(arr, min(header.cell_x, header.cell_y), target_cell)

    return _Raster(arr, crs, header.left, header.top, header.cell_x * block, header.cell_y * block, header.path)


# ---------------------------------------------------------------------------
# Mosaik
# ---------------------------------------------------------------------------

def _selection_latlon_box(selection, margin_m: float = MARGIN_M):
    lat, lon = selection.center
    scale = float(getattr(selection, "scale_factor", 1.0) or 1.0)
    radius = math.hypot(selection.width_m, selection.height_m) / 2.0 * scale + margin_m
    dlat = radius / 111320.0
    dlon = radius / (111320.0 * max(0.1, math.cos(math.radians(lat))))
    return lat - dlat, lat + dlat, lon - dlon, lon + dlon


def _box_in_crs(crs, box):
    lat0, lat1, lon0, lon1 = box
    lats = np.array([lat0, lat0, lat1, lat1, (lat0 + lat1) / 2, (lat0 + lat1) / 2, lat0, lat1])
    lons = np.array([lon0, lon1, lon0, lon1, lon0, lon1, (lon0 + lon1) / 2, (lon0 + lon1) / 2])
    x, y = crs.latlon_to_xy(lats, lons)
    return float(np.min(x)), float(np.max(x)), float(np.min(y)), float(np.max(y))


@dataclass
class LocalRasterMosaic:
    rasters: list
    parallel_safe: bool = True
    missing_slots: int = 0
    attributions: list = field(default_factory=list)
    actualities: list = field(default_factory=list)
    epsg_codes: tuple = ()
    skipped_files: int = 0

    @property
    def slot_count(self) -> int:
        return len(self.rasters)

    @classmethod
    def from_folder(cls, folder, selection=None, epsg=None, target_cell: float = TARGET_CELL_M):
        folder = Path(folder)
        files = raster_files(folder)
        if not files:
            raise LocalRasterError(f"Im Ordner {folder} liegen keine GeoTIFF- oder ASC-Dateien.")

        override = epsg or _folder_epsg(folder)
        box = _selection_latlon_box(selection) if selection is not None else None
        rasters, codes, skipped, unknown = [], set(), 0, []

        for path in files:
            header = read_header(path)
            code = override or header.epsg
            if code is None:
                unknown.append(path.name)
                continue
            try:
                crs = get_crs(code)
            except UnknownCrsError:
                raise LocalRasterError(
                    f"{path.name}: Koordinatensystem EPSG:{code} wird nicht unterstuetzt."
                ) from None
            if box is not None:
                x0, x1, y0, y1 = _box_in_crs(crs, box)
                if header.right < x0 or header.left > x1 or header.top < y0 or header.bottom > y1:
                    skipped += 1
                    continue
            rasters.append(load_raster(header, crs, target_cell))
            codes.add(code)

        if unknown and not rasters:
            raise LocalRasterError(
                "Koordinatensystem unbekannt fuer: " + ", ".join(unknown[:5])
                + ". Lege eine Datei epsg.txt mit der EPSG-Nummer (z. B. 2154 fuer Frankreich) in den Ordner."
            )

        return cls(rasters, epsg_codes=tuple(sorted(codes)), skipped_files=skipped)

    def sample_grid(self, lat, lon):
        lat = np.asarray(lat, dtype=np.float64)
        lon = np.asarray(lon, dtype=np.float64)
        out = np.full(lat.shape, np.nan, dtype=np.float32)
        cache = {}

        for r in self.rasters:
            key = id(r.crs)
            if key not in cache:
                cache[key] = r.crs.latlon_to_xy(lat, lon)
            x, y = cache[key]
            col = (x - r.left) / r.cell_x - 0.5
            row = (r.top - y) / r.cell_y - 0.5
            rows, cols = r.h.shape
            need = (np.isnan(out) & (col >= -0.5) & (col <= cols - 0.5)
                    & (row >= -0.5) & (row <= rows - 0.5))
            if not need.any():
                continue
            c = np.clip(col[need], 0, cols - 1)
            rr = np.clip(row[need], 0, rows - 1)
            ci = np.minimum(np.floor(c).astype(int), max(cols - 2, 0))
            ri = np.minimum(np.floor(rr).astype(int), max(rows - 2, 0))
            c1, r1 = np.minimum(ci + 1, cols - 1), np.minimum(ri + 1, rows - 1)
            fc, fr = (c - ci).astype(np.float32), (rr - ri).astype(np.float32)
            h = r.h
            v = ((h[ri, ci] * (1 - fc) + h[ri, c1] * fc) * (1 - fr)
                 + (h[r1, ci] * (1 - fc) + h[r1, c1] * fc) * fr)
            # Am Rand von Datenluecken: naechster gueltiger Nachbar statt NaN
            bad = np.isnan(v)
            if bad.any():
                near = h[np.rint(rr[bad]).astype(int), np.rint(c[bad]).astype(int)]
                v[bad] = near
            out[need] = v
        return out


def folder_needs_generic(folder) -> bool:
    """True, wenn der Ordner nicht nur DGM1-taugliche GeoTIFF (UTM 32/33) enthaelt."""

    files = raster_files(folder)
    if not files:
        return False
    override = _folder_epsg(folder)
    for path in files:
        if path.suffix.lower() == ".asc":
            return True
        try:
            header = read_header(path)
        except LocalRasterError:
            return True
        code = override or header.epsg
        if code not in DGM1_EPSG:
            return True
    return False


def folder_epsg_known(folder) -> bool:
    """True, wenn fuer jede Datei im Ordner das Koordinatensystem erkannt wird."""

    files = raster_files(folder)
    if not files:
        return False
    if _folder_epsg(folder):
        return True
    for path in files:
        try:
            if read_header(path).epsg is None:
                return False
        except LocalRasterError:
            return False
    return True
