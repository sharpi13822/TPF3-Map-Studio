"""
Umrechnung Breite/Laenge <-> UTM (ETRS89 / GRS80) ohne pyproj.

Das DGM1 der Bundeslaender liegt in ETRS89/UTM Zone 32 (EPSG:25832) oder
Zone 33 (EPSG:25833). Die Formeln sind die Krueger-Reihen (Karney 2011), auf
Millimeter genau; sie arbeiten vektorisiert auf numpy-Arrays.
"""

from __future__ import annotations

import math

import numpy as np

# GRS80 (fuer ETRS89 praktisch identisch mit WGS84)
A_AXIS = 6378137.0
FLATTENING = 1.0 / 298.257222101
K0 = 0.9996
FALSE_EASTING = 500000.0

_n = FLATTENING / (2.0 - FLATTENING)
_n2, _n3, _n4, _n5, _n6 = _n**2, _n**3, _n**4, _n**5, _n**6

_A = A_AXIS / (1.0 + _n) * (1.0 + _n2 / 4.0 + _n4 / 64.0 + _n6 / 256.0)

_ALPHA = (
    _n / 2.0 - 2.0 * _n2 / 3.0 + 5.0 * _n3 / 16.0 + 41.0 * _n4 / 180.0
    - 127.0 * _n5 / 288.0 + 7891.0 * _n6 / 37800.0,
    13.0 * _n2 / 48.0 - 3.0 * _n3 / 5.0 + 557.0 * _n4 / 1440.0
    + 281.0 * _n5 / 630.0 - 1983433.0 * _n6 / 1935360.0,
    61.0 * _n3 / 240.0 - 103.0 * _n4 / 140.0 + 15061.0 * _n5 / 26880.0
    + 167603.0 * _n6 / 181440.0,
    49561.0 * _n4 / 161280.0 - 179.0 * _n5 / 168.0 + 6601661.0 * _n6 / 7257600.0,
    34729.0 * _n5 / 80640.0 - 3418889.0 * _n6 / 1995840.0,
    212378941.0 * _n6 / 319334400.0,
)

_BETA = (
    _n / 2.0 - 2.0 * _n2 / 3.0 + 37.0 * _n3 / 96.0 - _n4 / 360.0
    - 81.0 * _n5 / 512.0 + 96199.0 * _n6 / 604800.0,
    _n2 / 48.0 + _n3 / 15.0 - 437.0 * _n4 / 1440.0 + 46.0 * _n5 / 105.0
    - 1118711.0 * _n6 / 3870720.0,
    17.0 * _n3 / 480.0 - 37.0 * _n4 / 840.0 - 209.0 * _n5 / 4480.0
    + 5569.0 * _n6 / 90720.0,
    4397.0 * _n4 / 161280.0 - 11.0 * _n5 / 504.0 - 830251.0 * _n6 / 7257600.0,
    4583.0 * _n5 / 161280.0 - 108847.0 * _n6 / 3991680.0,
    20648693.0 * _n6 / 638668800.0,
)

_DELTA = (
    2.0 * _n - 2.0 * _n2 / 3.0 - 2.0 * _n3 + 116.0 * _n4 / 45.0
    + 26.0 * _n5 / 45.0 - 2854.0 * _n6 / 675.0,
    7.0 * _n2 / 3.0 - 8.0 * _n3 / 5.0 - 227.0 * _n4 / 45.0
    + 2704.0 * _n5 / 315.0 + 2323.0 * _n6 / 945.0,
    56.0 * _n3 / 15.0 - 136.0 * _n4 / 35.0 - 1262.0 * _n5 / 105.0
    + 73814.0 * _n6 / 2835.0,
    4279.0 * _n4 / 630.0 - 332.0 * _n5 / 35.0 - 399572.0 * _n6 / 14175.0,
    4174.0 * _n5 / 315.0 - 144838.0 * _n6 / 6237.0,
    601676.0 * _n6 / 22275.0,
)

_SQRT_N_TERM = 2.0 * math.sqrt(_n) / (1.0 + _n)


def central_meridian_deg(zone: int) -> float:
    return zone * 6.0 - 183.0


def zone_for_lon(lon_deg: float) -> int:
    """UTM-Zone nach Laengengrad (Deutschland: 32 bis 12 Grad Ost, danach 33)."""

    return int(math.floor((lon_deg + 180.0) / 6.0)) + 1


def latlon_to_utm(lat, lon, zone: int):
    """(Breite, Laenge) in Grad -> (Ost, Nord) in Metern der angegebenen Zone."""

    phi = np.radians(np.asarray(lat, dtype=np.float64))
    lam = np.radians(np.asarray(lon, dtype=np.float64) - central_meridian_deg(zone))

    sin_phi = np.sin(phi)
    t = np.sinh(
        np.arctanh(sin_phi) - _SQRT_N_TERM * np.arctanh(_SQRT_N_TERM * sin_phi)
    )

    xi_p = np.arctan2(t, np.cos(lam))
    eta_p = np.arctanh(np.sin(lam) / np.sqrt(1.0 + t * t))

    xi = xi_p.copy()
    eta = eta_p.copy()

    for j, alpha in enumerate(_ALPHA, start=1):
        xi = xi + alpha * np.sin(2 * j * xi_p) * np.cosh(2 * j * eta_p)
        eta = eta + alpha * np.cos(2 * j * xi_p) * np.sinh(2 * j * eta_p)

    easting = FALSE_EASTING + K0 * _A * eta
    northing = K0 * _A * xi

    return easting, northing


def utm_to_latlon(easting, northing, zone: int):
    """(Ost, Nord) in Metern der Zone -> (Breite, Laenge) in Grad."""

    xi = np.asarray(northing, dtype=np.float64) / (K0 * _A)
    eta = (np.asarray(easting, dtype=np.float64) - FALSE_EASTING) / (K0 * _A)

    xi_p = xi.copy()
    eta_p = eta.copy()

    for j, beta in enumerate(_BETA, start=1):
        xi_p = xi_p - beta * np.sin(2 * j * xi) * np.cosh(2 * j * eta)
        eta_p = eta_p - beta * np.cos(2 * j * xi) * np.sinh(2 * j * eta)

    chi = np.arcsin(np.sin(xi_p) / np.cosh(eta_p))

    phi = chi.copy()
    for j, delta in enumerate(_DELTA, start=1):
        phi = phi + delta * np.sin(2 * j * chi)

    lam = np.arctan2(np.sinh(eta_p), np.cos(xi_p))

    return np.degrees(phi), np.degrees(lam) + central_meridian_deg(zone)
