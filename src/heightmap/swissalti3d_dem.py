"""
swissALTI3D (Hoehenmodell von swisstopo fuer die Schweiz und Liechtenstein) als weitere
Hoehenquelle neben Copernicus und DGM1.

Die Kacheln (1 km x 1 km, GeoTIFF, LV95) kommen von data.geo.admin.ch. Welche Kacheln es
fuer einen Ausschnitt gibt und unter welcher Adresse (das Jahr der Befliegung steckt im Namen
und ist je Kachel verschieden), fragt das Studio ueber die STAC-Schnittstelle von swisstopo ab.
Geladen wird die Variante mit 2 m Aufloesung (rund 1 MB je Kachel); bei der Karte mit 4 m pro
Pixel reicht das, die 0,5-m-Variante waere 16-mal groesser.

Die Kacheln liegen danach im Zwischenspeicher und werden vom selben Mosaik gelesen wie das
DGM1 (dgm1_dem.Dgm1Mosaic mit der Kennzahl LV95_ZONE).

Nutzungsbedingungen (OGD swisstopo): freie Nutzung, auch kommerziell, die Quellenangabe
ist Pflicht (siehe ATTRIBUTION).
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import numpy as np
import requests

from src.heightmap.dgm1_dem import (
    MARGIN_M,
    TILE_M,
    Dgm1Cancelled,
    Dgm1Error,
    Dgm1FetchJob,
    FetchSummary,
    _required_tiles,
    _write_atomic,
    slot_is_cached,
)
from src.heightmap.lv95 import LV95_ZONE, latlon_to_lv95, lv95_to_latlon
from src.http_identity import USER_AGENT
from src.i18n import tr

STAC_ITEMS_URL = "https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissalti3d/items"

# Quellenangabe nach den Nutzungsbedingungen von swisstopo (OGD)
ATTRIBUTION = "© swisstopo (Bundesamt für Landestopografie swisstopo), swissALTI3D"

# Pause zwischen zwei Downloads: der Dienst soll nicht uebermaessig belastet werden.
MIN_REQUEST_INTERVAL_S = 0.2

# Anfragen an die STAC-Schnittstelle: Kachelbloecke von 10 x 10 km statt der ganzen Bounding-Box
# (ein gedrehtes, langes Band wuerde sonst tausende unbenoetigte Kacheln abfragen).
BLOCK_KM = 10
STAC_PAGE_LIMIT = 100
MAX_PAGES_PER_BLOCK = 30
BLOCK_PADDING_DEG = 0.003

_ITEM_ID = re.compile(r"^swissalti3d_(\d{4})_(\d{4})-(\d{4})$")


# ---------------------------------------------------------------------------
# Welche Kacheln braucht der Kartenausschnitt?
# ---------------------------------------------------------------------------


def required_swiss_tiles(
    selection,
    margin_m: float = MARGIN_M,
    step_m: float = 100.0,
) -> list[tuple[int, int, int]]:
    """Liste der 1-km-Kacheln (LV95_ZONE, Ost-km, Nord-km), die das Kartenband beruehren."""

    return _required_tiles(
        selection,
        margin_m,
        step_m,
        lambda lat, lon, _zone: latlon_to_lv95(lat, lon),
        lambda _lon: LV95_ZONE,
    )


def cache_file_name(ie: int, inn: int) -> str:
    """Dateiname im Zwischenspeicher, passend zu dgm1_dem.cached_files_for_slot."""

    return f"{LV95_ZONE}_{ie}_{inn}__swisstopo"


# ---------------------------------------------------------------------------
# STAC-Schnittstelle
# ---------------------------------------------------------------------------


def parse_item(item: dict) -> tuple[int, int, int, str, float] | None:
    """
    Liest einen STAC-Eintrag und liefert (Jahr, Ost-km, Nord-km, Downloadadresse, Aufloesung)
    der besten GeoTIFF-Datei: bevorzugt 2 m, sonst 0,5 m. None, wenn der Eintrag keine
    passende Kachel enthaelt.
    """

    match = _ITEM_ID.match(str(item.get("id", "")))

    if not match:
        return None

    year, ie, inn = (int(g) for g in match.groups())

    best = None

    for name, asset in (item.get("assets") or {}).items():

        href = (asset or {}).get("href")

        if not href or not str(name).lower().endswith(".tif"):
            continue

        if "_2056_" not in str(name):
            continue

        if "_2_2056_" in str(name):
            resolution = 2.0
        elif "_0.5_2056_" in str(name):
            resolution = 0.5
        else:
            continue

        # 2 m vor 0,5 m
        if best is None or (resolution == 2.0 and best[1] != 2.0):
            best = (href, resolution)

    if best is None:
        return None

    return year, ie, inn, best[0], best[1]


def pick_latest(items: list[dict]) -> dict[tuple[int, int], tuple[int, str, float]]:
    """(Ost-km, Nord-km) -> (Jahr, Adresse, Aufloesung): je Kachel die neueste Befliegung."""

    result: dict[tuple[int, int], tuple[int, str, float]] = {}

    for item in items:

        parsed = parse_item(item)

        if parsed is None:
            continue

        year, ie, inn, href, resolution = parsed

        known = result.get((ie, inn))

        if known is None or year > known[0]:
            result[(ie, inn)] = (year, href, resolution)

    return result


def tile_blocks(tiles) -> list[tuple[float, float, float, float]]:
    """
    Fasst die Kacheln zu Bloecken von BLOCK_KM x BLOCK_KM zusammen und liefert je Block den
    Umriss als (lon_min, lat_min, lon_max, lat_max) mit etwas Rand, fuer die STAC-Abfrage.
    """

    blocks = {(ie // BLOCK_KM, inn // BLOCK_KM) for _zone, ie, inn in tiles}

    result = []

    for be, bn in sorted(blocks):

        e0, e1 = be * BLOCK_KM * TILE_M, (be + 1) * BLOCK_KM * TILE_M
        n0, n1 = bn * BLOCK_KM * TILE_M, (bn + 1) * BLOCK_KM * TILE_M

        lats, lons = lv95_to_latlon(
            np.array([e0, e1, e0, e1], dtype=np.float64),
            np.array([n0, n0, n1, n1], dtype=np.float64),
        )

        result.append(
            (
                float(lons.min()) - BLOCK_PADDING_DEG,
                float(lats.min()) - BLOCK_PADDING_DEG,
                float(lons.max()) + BLOCK_PADDING_DEG,
                float(lats.max()) + BLOCK_PADDING_DEG,
            )
        )

    return result


def _get(session, url, params=None, timeout=60, retries=3, sleep=time.sleep):
    """GET mit wenigen Wiederholungen bei Netzwerk- und Dienstfehlern."""

    last_error = ""

    for attempt in range(retries):

        try:
            response = session.get(url, params=params, timeout=timeout)
        except requests.RequestException as exc:
            last_error = f"Netzwerkfehler: {exc}"
            sleep(min(20.0, 2.0 ** (attempt + 1)))
            continue

        if response.status_code == 429 or response.status_code >= 500:
            last_error = f"Dienstfehler HTTP {response.status_code}"
            sleep(min(30.0, 5.0 * (attempt + 1)))
            continue

        if response.status_code != 200:
            raise Dgm1Error(
                tr("swisstopo antwortet mit HTTP {status} ({url}).").format(
                    status=response.status_code, url=url
                )
            )

        return response

    raise Dgm1Error(tr("swisstopo nicht erreichbar ({error}).").format(error=last_error or tr("unbekannter Fehler")))


def query_items(session, bbox, sleep=time.sleep) -> list[dict]:
    """Alle STAC-Eintraege im Rechteck (lon_min, lat_min, lon_max, lat_max), Seite fuer Seite."""

    url = STAC_ITEMS_URL
    params = {
        "bbox": ",".join(f"{v:.6f}" for v in bbox),
        "limit": STAC_PAGE_LIMIT,
    }

    items: list[dict] = []

    for _page in range(MAX_PAGES_PER_BLOCK):

        response = _get(session, url, params=params, sleep=sleep)

        try:
            body = response.json()
        except ValueError as exc:
            raise Dgm1Error(tr("Unlesbare Antwort von swisstopo: {exc}").format(exc=exc)) from exc

        items.extend(body.get("features") or [])

        next_url = None

        for link in body.get("links") or []:
            if link.get("rel") == "next" and link.get("href"):
                next_url = link["href"]
                break

        if not next_url:
            break

        # Die Folgeseite enthaelt ihre Parameter schon in der Adresse
        url, params = next_url, None

    return items


# ---------------------------------------------------------------------------
# Abruf
# ---------------------------------------------------------------------------


def make_session():
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json, image/tiff, */*"})
    return session


def store_tile(cache_dir: Path, ie: int, inn: int, content: bytes, year: int, href: str) -> None:
    """Legt eine geladene Kachel samt Quellenvermerk im Zwischenspeicher ab."""

    name = cache_file_name(ie, inn)

    meta = {
        "Origin": "swisstopo",
        "Actuality": str(year),
        "Attribution": ATTRIBUTION,
        "TileIndex": f"{ie}-{inn}",
        "Source": href,
    }

    _write_atomic(cache_dir / f"{name}.tif", content)
    _write_atomic(cache_dir / f"{name}.json", json.dumps(meta, ensure_ascii=False).encode("utf-8"))


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
    Holt alle fehlenden swissALTI3D-Kacheln fuer den Ausschnitt. progress(done, total, text)
    wird laufend aufgerufen, cancelled() fragt den Abbruchwunsch ab (Dgm1Cancelled).
    Kacheln, die es bei swisstopo nicht gibt (ausserhalb der Schweiz), werden als "keine Daten"
    vermerkt und nicht erneut angefragt.
    """

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    slots = required_swiss_tiles(selection)

    summary = FetchSummary(total=len(slots))

    todo = []

    for zone, ie, inn in slots:
        if slot_is_cached(cache_dir, zone, ie, inn):
            if (cache_dir / f"{zone}_{ie}_{inn}.none").exists():
                summary.no_data += 1
            else:
                summary.already_cached += 1
        else:
            todo.append((zone, ie, inn))

    done = len(slots) - len(todo)

    def report(text):
        if progress is not None:
            progress(done, len(slots), text)

    def check_cancel():
        if cancelled is not None and cancelled():
            raise Dgm1Cancelled("Abgebrochen.")

    if not todo:
        report("Fertig")
        return summary

    session = session or make_session()

    # Welche Kacheln gibt es und wo liegen sie?
    found: dict[tuple[int, int], tuple[int, str, float]] = {}

    blocks = tile_blocks(todo)

    for index, bbox in enumerate(blocks):

        check_cancel()

        report(tr("Suche Kacheln bei swisstopo ({value} von {count})").format(value=index + 1, count=len(blocks)))

        found.update(pick_latest(query_items(session, bbox, sleep=sleep)))

    last_request = None

    for zone, ie, inn in todo:

        check_cancel()

        report(tr("Kachel {value} von {count}").format(value=done + 1, count=len(slots)))

        entry = found.get((ie, inn))

        if entry is None:
            _write_atomic(cache_dir / f"{zone}_{ie}_{inn}.none", "keine Daten bei swisstopo".encode("utf-8"))
            summary.no_data += 1
            done += 1
            continue

        year, href, _resolution = entry

        if last_request is not None:
            wait = min_interval_s - (time.monotonic() - last_request)
            if wait > 0:
                sleep(wait)

        last_request = time.monotonic()

        response = _get(session, href, timeout=180, sleep=sleep)

        if len(response.content) < 1000:
            raise Dgm1Error(tr("Kachel {ie}-{inn}: Antwort von swisstopo ist zu klein, vermutlich fehlerhaft.").format(ie=ie, inn=inn))

        store_tile(cache_dir, ie, inn, response.content, year, href)

        summary.fetched += 1
        done += 1

    report("Fertig")

    return summary


class SwissFetchJob(Dgm1FetchJob):
    """Fuehrt fetch_tiles_for_selection in einem Hintergrund-Thread aus (gleiche Schnittstelle
    wie Dgm1FetchJob, damit das Fortschrittsfenster beide nutzen kann)."""

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
