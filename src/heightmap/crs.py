"""
Koordinatensysteme fuer eigene Hoehendateien (GeoTIFF/ASC) ohne pyproj.

Unterstuetzt werden die in Europa ueblichen Abbildungen auf GRS80/WGS84 (beide
gelten hier als gleich, Unterschied unter 1 mm):
  - Transversale Mercator (UTM-Zonen und nationale TM-Systeme), Krueger-Reihen
    wie in utm.py, mit beliebigem Mittelmeridian, Massstab, Ursprungsbreite
  - Lambert-Kegelprojektion mit zwei Breitenkreisen (Frankreich, Belgien, Estland)
  - Geografisch (Laenge/Breite in Grad)

Systeme mit eigenem Datum (z. B. Grossbritannien OSGB36, Tschechien S-JTSK)
fehlen bewusst: ohne Datumsumrechnung laegen sie bis zu ~100 m daneben.
"""

from __future__ import annotations

import math

import numpy as np

from src.heightmap import utm

A_GRS80 = 6378137.0
F_GRS80 = 1.0 / 298.257222101
E_GRS80 = math.sqrt(F_GRS80 * (2.0 - F_GRS80))


class UnknownCrsError(ValueError):
    """EPSG-Code wird nicht unterstuetzt."""


class Crs:
    """latlon_to_xy(lat, lon) -> (x, y) in Metern bzw. Grad, vektorisiert."""

    def __init__(self, epsg: int, name: str, kind: str, **p):
        self.epsg = int(epsg)
        self.name = name
        self.kind = kind
        self.p = p
        if kind == "tm":
            self._xi0 = _tm_xi(p.get("lat0", 0.0))
        elif kind == "lcc":
            self._lcc_init()

    # --- Transversale Mercator -------------------------------------------------
    def _tm(self, lat, lon):
        p = self.p
        xi, eta = _tm_xi_eta(lat, np.asarray(lon, dtype=np.float64) - p["lon0"])
        k0 = p["k0"]
        x = p["fe"] + k0 * utm._A * eta
        y = p["fn"] + k0 * utm._A * (xi - self._xi0)
        return x, y

    # --- Lambert-Kegel (EPSG-Methode 9802) ---------------------------------------
    def _lcc_init(self):
        p = self.p
        e = p.get("e", E_GRS80)
        a = p.get("a", A_GRS80)
        def m(phi):
            return math.cos(phi) / math.sqrt(1.0 - e * e * math.sin(phi) ** 2)
        def t(phi):
            s = math.sin(phi)
            return math.tan(math.pi / 4.0 - phi / 2.0) / ((1.0 - e * s) / (1.0 + e * s)) ** (e / 2.0)
        p1, p2, p0 = (math.radians(p["lat1"]), math.radians(p["lat2"]), math.radians(p["lat0"]))
        m1, m2 = m(p1), m(p2)
        t1, t2, tf = t(p1), t(p2), t(p0)
        self._n = (math.log(m1) - math.log(m2)) / (math.log(t1) - math.log(t2))
        self._F = m1 / (self._n * t1 ** self._n)
        self._rf = a * self._F * tf ** self._n

    def _lcc(self, lat, lon):
        p = self.p
        e = p.get("e", E_GRS80)
        a = p.get("a", A_GRS80)
        phi = np.radians(np.asarray(lat, dtype=np.float64))
        s = np.sin(phi)
        t = np.tan(np.pi / 4.0 - phi / 2.0) / ((1.0 - e * s) / (1.0 + e * s)) ** (e / 2.0)
        r = a * self._F * t ** self._n
        theta = self._n * np.radians(np.asarray(lon, dtype=np.float64) - p["lon0"])
        x = p["fe"] + r * np.sin(theta)
        y = p["fn"] + self._rf - r * np.cos(theta)
        return x, y

    def latlon_to_xy(self, lat, lon):
        if self.kind == "geo":
            return np.asarray(lon, dtype=np.float64), np.asarray(lat, dtype=np.float64)
        if self.kind == "tm":
            return self._tm(lat, lon)
        return self._lcc(lat, lon)

    @property
    def is_geographic(self) -> bool:
        return self.kind == "geo"


def _tm_xi_eta(lat, dlon_deg):
    """Krueger-Reihe wie utm.latlon_to_utm, aber mit freiem Mittelmeridian."""

    phi = np.radians(np.asarray(lat, dtype=np.float64))
    lam = np.radians(np.asarray(dlon_deg, dtype=np.float64))
    sin_phi = np.sin(phi)
    t = np.sinh(np.arctanh(sin_phi) - utm._SQRT_N_TERM * np.arctanh(utm._SQRT_N_TERM * sin_phi))
    xi_p = np.arctan2(t, np.cos(lam))
    eta_p = np.arctanh(np.sin(lam) / np.sqrt(1.0 + t * t))
    xi, eta = xi_p.copy(), eta_p.copy()
    for j, alpha in enumerate(utm._ALPHA, start=1):
        xi = xi + alpha * np.sin(2 * j * xi_p) * np.cosh(2 * j * eta_p)
        eta = eta + alpha * np.cos(2 * j * xi_p) * np.sinh(2 * j * eta_p)
    return xi, eta


def _tm_xi(lat0: float) -> float:
    xi, _ = _tm_xi_eta(np.array([lat0]), np.array([0.0]))
    return float(xi[0])


def _utm(epsg, zone, name):
    return Crs(epsg, name, "tm", lon0=zone * 6.0 - 183.0, k0=0.9996, fe=500000.0, fn=0.0, lat0=0.0)


def _build_table() -> dict:
    table = {}
    for zone in range(26, 39):
        table[25800 + zone] = _utm(25800 + zone, zone, f"ETRS89 / UTM {zone}N")
        table[32600 + zone] = _utm(32600 + zone, zone, f"WGS 84 / UTM {zone}N")
    for epsg, zone in ((6707, 32), (6708, 33), (6709, 34), (7791, 32), (7792, 33), (7793, 34)):
        table[epsg] = _utm(epsg, zone, f"RDN2008 / UTM {zone}N (Italien)")
    table[4083] = _utm(4083, 28, "REGCAN95 / UTM 28N (Kanaren)")
    table[3067] = _utm(3067, 35, "ETRS89 / TM35FIN (Finnland)")
    table[3006] = Crs(3006, "SWEREF99 TM (Schweden)", "tm", lon0=15.0, k0=0.9996, fe=500000.0, fn=0.0)
    table[2157] = Crs(2157, "IRENET95 / ITM (Irland)", "tm", lon0=-8.0, k0=0.99982, fe=600000.0, fn=750000.0, lat0=53.5)
    table[3763] = Crs(3763, "ETRS89 / PT-TM06 (Portugal)", "tm", lon0=-8.133108333333333, k0=1.0,
                      fe=0.0, fn=0.0, lat0=39.66825833333333)
    table[2180] = Crs(2180, "ETRS89 / Poland CS92", "tm", lon0=19.0, k0=0.9993, fe=500000.0, fn=-5300000.0)
    table[3794] = Crs(3794, "Slovenia 1996 / TM", "tm", lon0=15.0, k0=0.9999, fe=500000.0, fn=-5000000.0)
    table[3765] = Crs(3765, "HTRS96 / Croatia TM", "tm", lon0=16.5, k0=0.9999, fe=500000.0, fn=0.0)
    table[3346] = Crs(3346, "LKS94 / Lithuania TM", "tm", lon0=24.0, k0=0.9998, fe=500000.0, fn=0.0)
    table[3059] = Crs(3059, "LKS92 / Latvia TM", "tm", lon0=24.0, k0=0.9996, fe=500000.0, fn=-6000000.0)
    table[2154] = Crs(2154, "RGF93 / Lambert-93 (Frankreich)", "lcc", lat1=49.0, lat2=44.0, lat0=46.5,
                      lon0=3.0, fe=700000.0, fn=6600000.0)
    table[3812] = Crs(3812, "ETRS89 / Belgian Lambert 2008", "lcc", lat1=49.833333333333336,
                      lat2=51.166666666666664, lat0=50.797815, lon0=4.359215833333333,
                      fe=649328.0, fn=665262.0)
    table[3301] = Crs(3301, "Estonian Coordinate System of 1997", "lcc", lat1=58.0, lat2=59.333333333333336,
                      lat0=57.51755393055556, lon0=24.0, fe=500000.0, fn=6375000.0)
    for epsg, name in ((4326, "WGS 84 (Laenge/Breite)"), (4258, "ETRS89 (Laenge/Breite)"),
                       (4937, "ETRS89 (Laenge/Breite)"), (4979, "WGS 84 (Laenge/Breite)")):
        table[epsg] = Crs(epsg, name, "geo")
    return table


CRS_TABLE = _build_table()


def get_crs(epsg: int) -> Crs:
    try:
        return CRS_TABLE[int(epsg)]
    except (KeyError, TypeError, ValueError):
        raise UnknownCrsError(f"EPSG:{epsg}") from None


def supported_codes() -> list[int]:
    return sorted(CRS_TABLE)


# --- Koordinatensystem aus Text erkennen (.prj, Dateiname) -------------------------

_PRJ_HINTS = (
    ("lambert-93", 2154), ("lambert_93", 2154), ("lambert 93", 2154), ("rgf93", 2154), ("lamb93", 2154),
    ("belgian lambert 2008", 3812), ("belgian_lambert_2008", 3812),
    ("pt-tm06", 3763), ("pt_tm06", 3763), ("cs92", 2180), ("irenet95", 2157), ("sweref99", 3006),
    ("tm35fin", 3067), ("htrs96", 3765), ("lks94", 3346), ("lks92", 3059),
    ("regcan95", 4083),
)


def epsg_from_text(text: str) -> int | None:
    """EPSG-Code aus einem .prj-Text (WKT) oder Dateinamen raten. None = unbekannt."""

    low = (text or "").lower()
    import re

    m = re.search(r'authority\s*\[\s*"epsg"\s*,\s*"?(\d{4,5})"?\s*\]\s*\]\s*$', low.strip())
    if m and int(m.group(1)) in CRS_TABLE:
        return int(m.group(1))
    m = re.search(r'id\s*\[\s*"epsg"\s*,\s*(\d{4,5})\s*\]\s*\]\s*$', low.strip())
    if m and int(m.group(1)) in CRS_TABLE:
        return int(m.group(1))
    for hint, code in _PRJ_HINTS:
        if hint in low:
            return code
    m = re.search(r"utm[ _]*zone[ _]*(\d{2})\s*n", low) or re.search(r"utm(\d{2})n?\b", low)
    if m:
        zone = int(m.group(1))
        if 26 <= zone <= 38:
            if "wgs" in low and "etrs" not in low:
                return 32600 + zone
            if "rdn2008" in low and zone in (32, 33, 34):
                return 6675 + zone
            return 25800 + zone
    m = re.search(r"epsg[:_ ]?(\d{4,5})", low)
    if m and int(m.group(1)) in CRS_TABLE:
        return int(m.group(1))
    if "gcs_wgs_1984" in low or 'geogcs["wgs 84"' in low and "projcs" not in low:
        return 4326
    return None
