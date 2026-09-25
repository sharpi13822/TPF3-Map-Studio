"""
Automatischer Download von Copernicus-DEM-GLO-30-Höhenkacheln fuer eine
(ggf. gedrehte) Selection.

Findet selbststaendig heraus, welche 1°x1°-Kacheln die Selection (also
auch ein gedrehtes Kartenband) berührt, laedt sie bei Bedarf vom
oeffentlichen AWS-Bucket herunter (kein Account/Key noetig) und legt sie
in einem lokalen Cache ab.

Quelle: https://copernicus-dem-30m.s3.amazonaws.com/
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import requests

from src.map.objects.selection import Selection

BASE_URL = "https://copernicus-dem-30m.s3.amazonaws.com"

# Sicherheitsrand um den eigentlichen Kartenausschnitt herum, damit beim
# Drehen/Zuschneiden immer echte Nachbarpixel zur Verfuegung stehen.
MARGIN_DEG = 0.05


def _tile_id(lat_floor: int, lon_floor: int) -> str:
    ns = "N" if lat_floor >= 0 else "S"
    ew = "E" if lon_floor >= 0 else "W"
    return f"Copernicus_DSM_COG_10_{ns}{abs(lat_floor):02d}_00_{ew}{abs(lon_floor):03d}_00_DEM"


def required_tiles(selection: Selection) -> list[str]:
    """Liste der 1°x1°-Kachel-IDs, die den (ggf. gedrehten) Selection-Bereich abdecken."""
    corners = selection.corners_latlon()
    lats = [c[0] for c in corners]
    lons = [c[1] for c in corners]
    lat_min, lat_max = min(lats) - MARGIN_DEG, max(lats) + MARGIN_DEG
    lon_min, lon_max = min(lons) - MARGIN_DEG, max(lons) + MARGIN_DEG

    tiles = []
    for lat_floor in range(math.floor(lat_min), math.ceil(lat_max)):
        for lon_floor in range(math.floor(lon_min), math.ceil(lon_max)):
            tiles.append(_tile_id(lat_floor, lon_floor))
    return tiles


def download_tile(tile_id: str, cache_dir: Path) -> Path:
    """Laedt eine Kachel herunter (falls noch nicht im Cache) und gibt den Pfad zurueck."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / f"{tile_id}.tif"
    if dest.exists():
        return dest

    url = f"{BASE_URL}/{tile_id}/{tile_id}.tif"
    tmp = dest.with_suffix(".tif.part")
    with requests.get(url, stream=True, timeout=60) as resp:
        if resp.status_code == 404:
            raise FileNotFoundError(
                f"Kachel {tile_id} existiert nicht bei Copernicus DEM "
                f"(vermutlich reines Wassergebiet ohne Landkachel: {url})"
            )
        resp.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
    tmp.rename(dest)
    return dest


def download_tiles_for_selection(selection: Selection, cache_dir: Path) -> list[Path]:
    """Bequemer Rundum-Aufruf: alle fuer die Selection noetigen Kacheln laden."""
    paths = []
    for tile_id in required_tiles(selection):
        try:
            paths.append(download_tile(tile_id, cache_dir))
        except FileNotFoundError:
            continue  # reine Wasserkachel ohne Landdaten - kein Fehler
    if not paths:
        raise RuntimeError(
            "Keine Copernicus-DEM-Kacheln fuer diesen Kartenausschnitt gefunden."
        )
    return paths


@dataclass
class DemTile:
    """Eine geladene Hoehenkachel mit ihrer Geo-Referenzierung."""

    array: np.ndarray
    lon0: float
    lat0: float
    dlon: float
    dlat: float

    @classmethod
    def load(cls, path: Path) -> "DemTile":
        from PIL import Image

        Image.MAX_IMAGE_PIXELS = None
        im = Image.open(path)
        tags = im.tag_v2
        scale = tags[33550]
        tiepoint = tags[33922]
        return cls(
            array=np.array(im, dtype=np.float32),
            lon0=tiepoint[3],
            lat0=tiepoint[4],
            dlon=scale[0],
            dlat=scale[1],
        )


class DemMosaic:
    """Mehrere Hoehenkacheln, angesprochen wie eine einzige zusammenhaengende Quelle.

    Fuer jeden angefragten Punkt wird die passende Kachel gewaehlt und
    dort bilinear interpoliert - die Kacheln muessen dafuer nicht auf ein
    gemeinsames Pixelraster gebracht werden (wichtig, weil Copernicus DEM
    noerdlich 50°N eine andere Ost-West- als Nord-Sued-Pixelbreite hat).
    """

    def __init__(self, tiles: list[DemTile]):
        self.tiles = tiles

    @classmethod
    def from_paths(cls, paths: list[Path]) -> "DemMosaic":
        return cls([DemTile.load(p) for p in paths])

    def sample_grid(self, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
        """Bilineare Hoehenabfrage fuer ganze Arrays von lat/lon-Punkten."""
        from scipy.ndimage import map_coordinates

        out = np.full(lat.shape, np.nan, dtype=np.float32)
        remaining = np.ones(lat.shape, dtype=bool)

        for tile in self.tiles:
            if not remaining.any():
                break
            row = (tile.lat0 - lat) / tile.dlat - 0.5
            col = (lon - tile.lon0) / tile.dlon - 0.5
            h, w = tile.array.shape
            in_tile = remaining & (row >= -0.5) & (row < h - 0.5) & (col >= -0.5) & (col < w - 0.5)
            if not in_tile.any():
                continue
            sampled = map_coordinates(
                tile.array, [row, col], order=1, mode="nearest"
            )
            out[in_tile] = sampled[in_tile]
            remaining &= ~in_tile

        return out