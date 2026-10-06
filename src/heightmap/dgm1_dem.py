"""
DGM1 (1-m-Gelaendemodell der Bundeslaender) als zweite Hoehenquelle neben
Copernicus.

Zwei Wege liefern Kacheln:

1. "DGM1 Deutschland": Kacheln von 1 km x 1 km kommen ueber den Webdienst
   hoehendaten.de (Aufruf RawTIFRequest). Der Dienst fasst die Open-Data-
   Angebote aller 16 Bundeslaender zusammen. Jede Kachel wird lokal
   zwischengespeichert; der Dienst erlaubt 1200 Kacheln pro Stunde.
2. "Eigene Kacheln": ein Ordner mit GeoTIFF-Kacheln, die man selbst bei einem
   Landesportal heruntergeladen hat.

Aus den Kacheln entsteht ein Dgm1Mosaic mit derselben Schnittstelle wie
copernicus_dem.DemMosaic (sample_grid(lat, lon)). Zum Speichersparen wird jede
Kachel beim Laden auf die Zielpixelgroesse (Standard 4 m) gemittelt: 580
Kacheln mit 1 m Aufloesung waeren sonst rund 2,3 GB gross.
"""

from __future__ import annotations

import base64
import json
import math
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import requests

from src.heightmap.copernicus_dem import _bilinear
from src.heightmap.utm import latlon_to_utm, zone_for_lon

API_URL = "https://api.hoehendaten.de:14444/v1/rawtif"

TILE_M = 1000  # Kantenlaenge einer Kachel in Metern

# Der Dienst erlaubt 1200 Kacheln pro Stunde = 20 pro Minute.
MIN_REQUEST_INTERVAL_S = 3.1

# Sicherheitsrand um den Kartenausschnitt, damit am Rand echte Nachbarpixel da sind.
MARGIN_M = 100.0

# Werte ausserhalb dieses Bereichs gelten als "keine Daten".
VALID_MIN_M = -500.0
VALID_MAX_M = 5000.0


class Dgm1Error(RuntimeError):
    """Fehler beim Abruf oder Lesen von DGM1-Kacheln."""


class Dgm1Cancelled(Dgm1Error):
    """Der Abruf wurde vom Nutzer abgebrochen."""


# ---------------------------------------------------------------------------
# Welche Kacheln braucht der Kartenausschnitt?
# ---------------------------------------------------------------------------


def required_dgm1_tiles(
    selection,
    margin_m: float = MARGIN_M,
    step_m: float = 100.0,
) -> list[tuple[int, int, int]]:
    """
    Liste der 1-km-Kacheln (Zone, Ost-km, Nord-km), die das (ggf. gedrehte)
    Kartenband beruehren. Nicht die Bounding-Box: ein um 45 Grad gedrehtes
    Band braeuchte sonst mehr als dreimal so viele Kacheln.
    """

    corners = list(selection.corners_latlon())

    if len(corners) != 4:
        raise Dgm1Error("Der Kartenausschnitt hat keine vier Ecken.")

    center_lon = float(np.mean([c[1] for c in corners]))
    zone = zone_for_lon(center_lon)

    pts = []
    for lat, lon in corners:
        e, n = latlon_to_utm(lat, lon, zone)
        pts.append((float(e), float(n)))

    # Ecken im Umlaufsinn ordnen (die Reihenfolge von corners_latlon ist nicht garantiert)
    cx = sum(p[0] for p in pts) / 4.0
    cy = sum(p[1] for p in pts) / 4.0
    pts.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))

    p0 = np.array(pts[0])
    pu = np.array(pts[1]) - p0
    pv = np.array(pts[3]) - p0

    len_u = float(np.hypot(*pu))
    len_v = float(np.hypot(*pv))

    if len_u <= 0 or len_v <= 0:
        raise Dgm1Error("Der Kartenausschnitt ist leer.")

    mu = margin_m / len_u
    mv = margin_m / len_v

    nu = int(math.ceil(len_u * (1 + 2 * mu) / step_m)) + 1
    nv = int(math.ceil(len_v * (1 + 2 * mv) / step_m)) + 1

    u = np.linspace(-mu, 1 + mu, nu)
    v = np.linspace(-mv, 1 + mv, nv)
    uu, vv = np.meshgrid(u, v)

    e = p0[0] + uu * pu[0] + vv * pv[0]
    n = p0[1] + uu * pu[1] + vv * pv[1]

    ie = np.floor(e / TILE_M).astype(np.int64)
    inn = np.floor(n / TILE_M).astype(np.int64)

    keys = np.unique(ie.ravel() * 100000 + inn.ravel())

    return [(zone, int(k // 100000), int(k % 100000)) for k in keys]


# ---------------------------------------------------------------------------
# Zwischenspeicher
# ---------------------------------------------------------------------------


def _slot_prefix(zone: int, ie: int, inn: int) -> str:
    return f"{zone}_{ie}_{inn}"


def cached_files_for_slot(cache_dir: Path, zone: int, ie: int, inn: int) -> list[Path]:
    """Alle zwischengespeicherten GeoTIFF-Teile einer Kachel (bei Landesgrenzen 1 bis 3)."""

    return sorted(Path(cache_dir).glob(f"{_slot_prefix(zone, ie, inn)}__*.tif"))


def slot_is_cached(cache_dir: Path, zone: int, ie: int, inn: int) -> bool:
    """True, wenn die Kachel schon geladen wurde (auch als 'keine Daten' vermerkt)."""

    cache_dir = Path(cache_dir)

    if (cache_dir / f"{_slot_prefix(zone, ie, inn)}.none").exists():
        return True

    return bool(cached_files_for_slot(cache_dir, zone, ie, inn))


def _write_atomic(path: Path, data: bytes) -> None:
    tmp = path.with_name(f"{path.name}.{os.getpid()}-{threading.get_ident()}.part")
    try:
        tmp.write_bytes(data)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Abruf ueber hoehendaten.de
# ---------------------------------------------------------------------------


def fetch_slot(
    zone: int,
    ie: int,
    inn: int,
    cache_dir: Path,
    session=None,
    max_retries: int = 4,
) -> int:
    """
    Holt eine Kachel (falls noch nicht im Zwischenspeicher). Gibt die Zahl der
    NEU geladenen Teile zurueck (0 = war schon da oder keine Daten).
    Wirft Dgm1Error bei Netzwerk- oder Dienstfehlern.
    """

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    if slot_is_cached(cache_dir, zone, ie, inn):
        return 0

    post = (session or requests).post

    # Referenzpunkt in der Kachelmitte
    payload = {
        "Type": "RawTIFRequest",
        "ID": _slot_prefix(zone, ie, inn),
        "Attributes": {
            "Zone": zone,
            "Easting": ie * TILE_M + TILE_M / 2.0,
            "Northing": inn * TILE_M + TILE_M / 2.0,
        },
    }

    last_error = ""

    for attempt in range(max_retries):

        try:
            resp = post(
                API_URL,
                json=payload,
                headers={"Accept": "application/json"},
                timeout=90,
            )
        except requests.RequestException as exc:
            last_error = f"Netzwerkfehler: {exc}"
            time.sleep(min(30.0, 2.0 ** (attempt + 1)))
            continue

        if resp.status_code == 429:
            # Abfragelimit erreicht: laenger warten
            retry_after = 0.0
            try:
                retry_after = float(resp.headers.get("Retry-After", 0))
            except (TypeError, ValueError, AttributeError):
                pass
            last_error = "Abfragelimit des Dienstes erreicht (HTTP 429)"
            time.sleep(max(retry_after, 30.0))
            continue

        if resp.status_code >= 500:
            last_error = f"Dienstfehler HTTP {resp.status_code}"
            time.sleep(min(30.0, 2.0 ** (attempt + 1)))
            continue

        if resp.status_code != 200:
            raise Dgm1Error(
                f"hoehendaten.de antwortet mit HTTP {resp.status_code} fuer Kachel "
                f"{_slot_prefix(zone, ie, inn)}."
            )

        try:
            body = resp.json()
        except ValueError as exc:
            raise Dgm1Error(f"Unlesbare Antwort von hoehendaten.de: {exc}") from exc

        return _store_response(body, zone, ie, inn, cache_dir)

    raise Dgm1Error(
        f"Kachel {_slot_prefix(zone, ie, inn)} konnte nicht geladen werden "
        f"({last_error or 'unbekannter Fehler'})."
    )


def _store_response(body: dict, zone: int, ie: int, inn: int, cache_dir: Path) -> int:

    attrs = body.get("Attributes") or {}

    if attrs.get("IsError"):
        err = attrs.get("Error") or {}
        text = " ".join(
            str(err.get(k, "")) for k in ("Title", "Details", "Detail")
        ).strip()
        # Kacheln ausserhalb Deutschlands (z. B. im Ausland oder in der Nordsee)
        # liefern einen Fehler: merken, damit sie nicht erneut angefragt werden.
        _write_atomic(
            cache_dir / f"{_slot_prefix(zone, ie, inn)}.none",
            (text or "keine Daten").encode("utf-8"),
        )
        return 0

    parts = attrs.get("RawTIFs") or []

    if not parts:
        _write_atomic(
            cache_dir / f"{_slot_prefix(zone, ie, inn)}.none",
            b"keine Daten",
        )
        return 0

    stored = 0

    for part in parts:

        origin = str(part.get("Origin") or "XX").replace("/", "-").replace(" ", "")

        try:
            raw = base64.b64decode(part["Data"])
        except (KeyError, ValueError) as exc:
            raise Dgm1Error(f"Kachel {_slot_prefix(zone, ie, inn)}: Daten nicht lesbar.") from exc

        name = f"{_slot_prefix(zone, ie, inn)}__{origin}"

        meta = {
            "Origin": part.get("Origin"),
            "Actuality": part.get("Actuality"),
            "Attribution": part.get("Attribution"),
            "TileIndex": part.get("TileIndex"),
        }

        _write_atomic(cache_dir / f"{name}.tif", raw)
        _write_atomic(
            cache_dir / f"{name}.json",
            json.dumps(meta, ensure_ascii=False).encode("utf-8"),
        )

        stored += 1

    return stored


@dataclass
class FetchSummary:
    total: int = 0
    fetched: int = 0
    already_cached: int = 0
    no_data: int = 0


def fetch_tiles_for_selection(
    selection,
    cache_dir: Path,
    progress=None,
    cancelled=None,
    min_interval_s: float = MIN_REQUEST_INTERVAL_S,
    session=None,
    sleep=time.sleep,
) -> FetchSummary:
    """
    Holt alle fehlenden Kacheln fuer den Ausschnitt, hoechstens so schnell, wie
    der Dienst es erlaubt. progress(done, total, text) wird nach jeder Kachel
    aufgerufen, cancelled() fragt den Abbruchwunsch ab (Dgm1Cancelled).
    """

    cache_dir = Path(cache_dir)
    slots = required_dgm1_tiles(selection)

    summary = FetchSummary(total=len(slots))

    last_request = None

    for done, (zone, ie, inn) in enumerate(slots):

        if cancelled is not None and cancelled():
            raise Dgm1Cancelled("Abgebrochen.")

        if progress is not None:
            progress(done, len(slots), f"Kachel {done + 1} von {len(slots)}")

        if slot_is_cached(cache_dir, zone, ie, inn):
            if (cache_dir / f"{_slot_prefix(zone, ie, inn)}.none").exists():
                summary.no_data += 1
            else:
                summary.already_cached += 1
            continue

        # Pause zwischen zwei echten Anfragen (Abfragelimit des Dienstes)
        if last_request is not None:
            wait = min_interval_s - (time.monotonic() - last_request)
            if wait > 0:
                sleep(wait)

        last_request = time.monotonic()

        stored = fetch_slot(zone, ie, inn, cache_dir, session=session)

        if stored:
            summary.fetched += 1
        else:
            summary.no_data += 1

    if progress is not None:
        progress(len(slots), len(slots), "Fertig")

    return summary


class Dgm1FetchJob:
    """Fuehrt fetch_tiles_for_selection in einem Hintergrund-Thread aus.

    Die Oberflaeche fragt nur state ab (done, total, text, finished, error,
    summary); keine Qt-Signale noetig.
    """

    def __init__(self, selection, cache_dir: Path):
        self.selection = selection
        self.cache_dir = Path(cache_dir)
        self.done = 0
        self.total = 0
        self.text = "Starte..."
        self.finished = False
        self.error: str | None = None
        self.cancelled = False
        self.summary: FetchSummary | None = None
        self._cancel_flag = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def cancel(self) -> None:
        self._cancel_flag.set()
        self.text = "Breche ab..."

    def join(self, timeout=None) -> None:
        self._thread.join(timeout)

    def _on_progress(self, done: int, total: int, text: str) -> None:
        self.done, self.total, self.text = done, total, text

    def _run(self) -> None:
        try:
            self.summary = fetch_tiles_for_selection(
                self.selection,
                self.cache_dir,
                progress=self._on_progress,
                cancelled=self._cancel_flag.is_set,
            )
        except Dgm1Cancelled:
            self.cancelled = True
            self.error = "Abgebrochen."
        except Exception as exc:  # noqa: BLE001 - jede Fehlerart soll in der Oberflaeche landen
            self.error = str(exc)
        finally:
            self.finished = True


# ---------------------------------------------------------------------------
# GeoTIFF lesen
# ---------------------------------------------------------------------------

TAG_PIXEL_SCALE = 33550
TAG_TIEPOINT = 33922
TAG_TRANSFORMATION = 34264
TAG_GEOKEYS = 34735
TAG_GDAL_NODATA = 42113

GEOKEY_RASTER_TYPE = 1025  # 1 = PixelIsArea, 2 = PixelIsPoint
GEOKEY_PROJECTED_CS = 3072


def _geokeys(tags) -> dict[int, int]:
    raw = tags.get(TAG_GEOKEYS)
    if not raw:
        return {}
    raw = list(raw)
    keys = {}
    n = int(raw[3]) if len(raw) >= 4 else 0
    for i in range(n):
        base = 4 + 4 * i
        if base + 3 >= len(raw):
            break
        key_id, location, _count, value = raw[base:base + 4]
        if location == 0:
            keys[int(key_id)] = int(value)
    return keys


@dataclass
class RasterInfo:
    """Georeferenz einer GeoTIFF-Datei (Ecke oben links, Pixelgroesse, Zone)."""

    path: Path
    zone: int
    e_ul: float
    n_ul: float
    px: float
    width: int
    height: int
    nodata: float | None


def read_raster_info(path: Path) -> RasterInfo:
    """Liest nur die Kopfdaten (schnell), ohne die Hoehen zu entschluesseln."""

    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None

    try:
        with Image.open(path) as im:
            tags = im.tag_v2
            width, height = im.size
            scale = tags.get(TAG_PIXEL_SCALE)
            tie = tags.get(TAG_TIEPOINT)
            matrix = tags.get(TAG_TRANSFORMATION)
            nodata_raw = tags.get(TAG_GDAL_NODATA)
            keys = _geokeys(tags)
    except Exception as exc:  # noqa: BLE001
        raise Dgm1Error(f"{Path(path).name}: keine lesbare GeoTIFF-Datei ({exc}).") from exc

    if scale and tie and len(tie) >= 6:
        px = float(scale[0])
        e0, n0 = float(tie[3]), float(tie[4])
    elif matrix and len(matrix) >= 16:
        # Alternative Schreibweise: 4x4-Transformationsmatrix (Pixel -> Koordinate)
        px = abs(float(matrix[0]))
        e0, n0 = float(matrix[3]), float(matrix[7])
    else:
        raise Dgm1Error(f"{Path(path).name}: keine Georeferenzierung im GeoTIFF gefunden.")

    # PixelIsPoint: der Referenzpunkt ist die Pixelmitte, nicht die Ecke
    if keys.get(GEOKEY_RASTER_TYPE) == 2:
        e0 -= px / 2.0
        n0 += px / 2.0

    epsg = keys.get(GEOKEY_PROJECTED_CS)
    zone = {25832: 32, 25833: 33}.get(epsg)

    if zone is None:
        # Kein EPSG-Code im Kopf: Zone aus dem Dateinamen ("32_497_5670..."), sonst 32
        head = Path(path).name.split("_")[0]
        zone = int(head) if head in ("32", "33") else 32

    nodata = None
    if nodata_raw not in (None, ""):
        try:
            nodata = float(str(nodata_raw).strip("\x00 "))
        except ValueError:
            nodata = None

    return RasterInfo(Path(path), zone, e0, n0, px, int(width), int(height), nodata)


def read_raster_array(info: RasterInfo) -> np.ndarray:
    """Hoehenwerte als float32, ungueltige Werte als NaN."""

    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None

    try:
        with Image.open(info.path) as im:
            arr = np.array(im, dtype=np.float32)
    except Exception as exc:  # noqa: BLE001
        raise Dgm1Error(
            f"{info.path.name}: Hoehenwerte nicht lesbar ({exc}). "
            f"Die Datei bleibt zur Pruefung im Ordner liegen."
        ) from exc

    if arr.ndim != 2:
        raise Dgm1Error(f"{info.path.name}: erwartet ein einkanaliges Hoehenraster.")

    invalid = ~np.isfinite(arr) | (arr < VALID_MIN_M) | (arr > VALID_MAX_M)

    if info.nodata is not None:
        invalid |= np.isclose(arr, info.nodata)

    arr[invalid] = np.nan

    return arr


def _block_mean(arr: np.ndarray, block: int) -> np.ndarray:
    """Mittelwert ueber block x block Pixel, NaN-Pixel werden ignoriert."""

    if block <= 1:
        return arr

    h, w = arr.shape
    nh, nw = h // block, w // block
    arr = arr[: nh * block, : nw * block]

    valid = np.isfinite(arr)
    total = np.where(valid, arr, 0.0).reshape(nh, block, nw, block).sum(axis=(1, 3))
    count = valid.reshape(nh, block, nw, block).sum(axis=(1, 3))

    with np.errstate(invalid="ignore", divide="ignore"):
        out = total / count

    out[count == 0] = np.nan

    return out.astype(np.float32)


@dataclass
class Slot:
    """Eine 1-km-Kachel, auf die Zielpixelgroesse gemittelt (cells x cells)."""

    zone: int
    ie: int
    inn: int
    cell_m: float
    cells: np.ndarray
    sources: list[str] = field(default_factory=list)


def slots_from_raster(
    info: RasterInfo,
    cell_m: float,
    wanted: set[tuple[int, int, int]] | None = None,
    attribution: str | None = None,
) -> list[Slot]:
    """
    Zerlegt ein Raster in 1-km-Kacheln auf dem Landesraster und mittelt jede auf
    cell_m. Die Kacheln muessen an ganzen Kilometern ausgerichtet sein (bis auf
    eine Pixelbreite Toleranz); eine 2-km-Kachel ergibt vier Slots.
    """

    px = info.px

    if px <= 0 or TILE_M % px > 1e-6:
        raise Dgm1Error(
            f"{info.path.name}: Pixelgroesse {px} m passt nicht in eine 1-km-Kachel."
        )

    e_km = round(info.e_ul / TILE_M) * TILE_M
    n_km = round(info.n_ul / TILE_M) * TILE_M

    if abs(info.e_ul - e_km) > px * 1.01 or abs(info.n_ul - n_km) > px * 1.01:
        raise Dgm1Error(
            f"{info.path.name}: Kachel liegt nicht auf dem 1-km-Raster "
            f"(Ecke {info.e_ul:.1f} / {info.n_ul:.1f}). Solche Dateien werden nicht unterstuetzt."
        )

    per_slot = int(round(TILE_M / px))
    block = max(1, int(round(cell_m / px)))

    if per_slot % block:
        block = 1

    n_cols = info.width // per_slot
    n_rows = info.height // per_slot

    if n_cols < 1 or n_rows < 1:
        raise Dgm1Error(f"{info.path.name}: kleiner als eine 1-km-Kachel.")

    ie0 = int(e_km // TILE_M)
    in_top = int(n_km // TILE_M)  # Oberkante der obersten Kachelreihe

    # Nur noetig, wenn das Raster Slots enthaelt, die jemand braucht
    needed = []
    for r in range(n_rows):
        for c in range(n_cols):
            key = (info.zone, ie0 + c, in_top - 1 - r)
            if wanted is None or key in wanted:
                needed.append((r, c, key))

    if not needed:
        return []

    arr = read_raster_array(info)

    slots = []

    for r, c, key in needed:
        block_px = arr[
            r * per_slot:(r + 1) * per_slot,
            c * per_slot:(c + 1) * per_slot,
        ]

        slots.append(
            Slot(
                zone=key[0],
                ie=key[1],
                inn=key[2],
                cell_m=block * px,
                cells=_block_mean(block_px, block),
                sources=[attribution] if attribution else [],
            )
        )

    return slots


def _slots_from_cache_file(path: Path, cell_m: float, wanted) -> list[Slot]:

    attribution = None
    meta_path = path.with_suffix(".json")
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            attribution = meta.get("Attribution")
        except (OSError, ValueError):
            attribution = None

    info = read_raster_info(path)

    # Der Zwischenspeicher-Name nennt die Zone, in der angefragt wurde; die Kachel
    # selbst liegt in der Zone ihres Landes (TileIndex "32_497_5670").
    return slots_from_raster(info, cell_m, wanted, attribution)


# ---------------------------------------------------------------------------
# Mosaik
# ---------------------------------------------------------------------------


class Dgm1Mosaic:
    """DGM1-Kacheln, angesprochen wie eine einzige Hoehenquelle (sample_grid)."""

    def __init__(self, slots: list[Slot], missing: int = 0):
        self.missing_slots = missing
        # Zone -> {Ost-km * 100000 + Nord-km: (aufgefuellte Zellen, Zellgroesse in m)}
        self._tiles: dict[int, dict[int, tuple[np.ndarray, float]]] = {}
        self.attributions: list[str] = []

        merged: dict[tuple[int, int, int], Slot] = {}

        for slot in slots:
            key = (slot.zone, slot.ie, slot.inn)
            if key in merged:
                # Landesgrenze: erster gueltiger Wert gewinnt
                base = merged[key]
                hole = np.isnan(base.cells)
                if hole.any() and base.cells.shape == slot.cells.shape:
                    base.cells = np.where(hole, slot.cells, base.cells)
                base.sources.extend(slot.sources)
            else:
                merged[key] = slot

        self.slot_count = len(merged)
        self._merged = merged

        seen = []
        for slot in merged.values():
            for text in slot.sources:
                if text and text not in seen:
                    seen.append(text)
        self.attributions = seen

        for (zone, ie, inn), slot in merged.items():
            self._tiles.setdefault(zone, {})[ie * 100000 + inn] = (
                self._pad(merged, slot),
                slot.cell_m,
            )

    @staticmethod
    def _pad(merged, slot: Slot) -> np.ndarray:
        """Kachel mit 1 Zellen Rand aus den Nachbarkacheln (damit an Nahtstellen
        bilinear ueber die Kachelgrenze hinweg interpoliert wird)."""

        h, w = slot.cells.shape
        out = np.pad(slot.cells, 1, mode="edge")

        def nb(de, dn):
            return merged.get((slot.zone, slot.ie + de, slot.inn + dn))

        # Nachbarn: Osten/Westen/Norden/Sueden (Zeile 0 = Norden)
        east, west = nb(1, 0), nb(-1, 0)
        north, south = nb(0, 1), nb(0, -1)

        if east is not None and east.cells.shape == slot.cells.shape:
            out[1:-1, -1] = east.cells[:, 0]
        if west is not None and west.cells.shape == slot.cells.shape:
            out[1:-1, 0] = west.cells[:, -1]
        if north is not None and north.cells.shape == slot.cells.shape:
            out[0, 1:-1] = north.cells[-1, :]
        if south is not None and south.cells.shape == slot.cells.shape:
            out[-1, 1:-1] = south.cells[0, :]

        # Ecken
        for de, dn, (ri, ci), (sr, sc) in (
            (1, 1, (0, -1), (-1, 0)),
            (-1, 1, (0, 0), (-1, -1)),
            (1, -1, (-1, -1), (0, 0)),
            (-1, -1, (-1, 0), (0, -1)),
        ):
            other = nb(de, dn)
            if other is not None and other.cells.shape == slot.cells.shape:
                out[ri, ci] = other.cells[sr, sc]

        return out

    @classmethod
    def from_cache(cls, selection, cache_dir: Path, cell_m: float = 4.0) -> "Dgm1Mosaic":
        """Baut das Mosaik aus bereits geladenen Kacheln (kein Netzwerk)."""

        slots: list[Slot] = []
        missing = 0

        for zone, ie, inn in required_dgm1_tiles(selection):
            files = cached_files_for_slot(cache_dir, zone, ie, inn)
            if not files:
                missing += 1
                continue
            for path in files:
                # Eine Datei kann in der UTM-Zone ihres Landes liegen (nicht der angefragten);
                # sie bringt ihre Zone aus dem GeoTIFF mit und wird so einsortiert.
                slots.extend(_slots_from_cache_file(path, cell_m, None))

        return cls(slots, missing)

    @classmethod
    def from_folder(cls, selection, folder: Path, cell_m: float = 4.0) -> "Dgm1Mosaic":
        """Baut das Mosaik aus selbst heruntergeladenen GeoTIFF-Kacheln eines Ordners."""

        folder = Path(folder)
        files = sorted(
            p for p in folder.rglob("*")
            if p.suffix.lower() in (".tif", ".tiff") and p.is_file()
        )

        if not files:
            raise Dgm1Error(f"Im Ordner {folder} liegen keine GeoTIFF-Dateien (.tif).")

        wanted = set(required_dgm1_tiles(selection))

        slots: list[Slot] = []

        for path in files:
            info = read_raster_info(path)
            slots.extend(slots_from_raster(info, cell_m, wanted))

        found = {(s.zone, s.ie, s.inn) for s in slots}

        return cls(slots, len(wanted - found))

    def sample_grid(self, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
        """Bilineare Hoehenabfrage; NaN dort, wo keine Kachel vorhanden ist."""

        lat = np.asarray(lat)
        lon = np.asarray(lon)

        out = np.full(lat.shape, np.nan, dtype=np.float32)

        flat_lat = lat.ravel()
        flat_lon = lon.ravel()
        flat_out = out.reshape(-1)

        for zone, tiles in self._tiles.items():

            todo = np.nonzero(np.isnan(flat_out))[0]

            if todo.size == 0:
                break

            e, n = latlon_to_utm(flat_lat[todo], flat_lon[todo], zone)

            ie = np.floor(e / TILE_M).astype(np.int64)
            inn = np.floor(n / TILE_M).astype(np.int64)
            keys = ie * 100000 + inn

            order = np.argsort(keys, kind="stable")
            sorted_keys = keys[order]

            uniq, starts = np.unique(sorted_keys, return_index=True)
            ends = np.append(starts[1:], sorted_keys.size)

            for key, a, b in zip(uniq, starts, ends):

                entry = tiles.get(int(key))

                if entry is None:
                    continue

                padded, cell = entry

                sel = order[a:b]

                e0 = (int(key) // 100000) * TILE_M
                n_top = (int(key) % 100000) * TILE_M + TILE_M

                col = (e[sel] - e0) / cell - 0.5 + 1.0
                row = (n_top - n[sel]) / cell - 0.5 + 1.0

                flat_out[todo[sel]] = _bilinear(padded, row, col)

        return out


def attribution_text(attributions: list[str]) -> str:
    """Quellenvermerk fuer veroeffentlichte Karten."""

    return "\n".join(attributions)
