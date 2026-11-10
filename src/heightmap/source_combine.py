"""
Mehrere Hoehenquellen in einer Karte kombinieren (ohne Qt, einzeln testbar).

Beispiel Mosel: DGM1 Rheinland-Pfalz, Luxemburg MNT 2024 und Copernicus.
Die Quellen stehen in einer Vorrang-Liste. Fuer jeden Pixel gilt die oberste
Quelle mit Daten; wo sie endet, uebernimmt die naechste.

Damit an der Grenze keine Stufe entsteht:
- Hoehenausgleich: Im Ueberlappungsbereich wird der mittlere Versatz
  (Median) der unteren Quelle gegenueber der oberen bestimmt und abgezogen.
  Die oberste Quelle behaelt ihre Hoehen.
- Weiche Naht: Auf einer Breite von blend_m Metern am Rand der oberen Quelle
  wird linear in die untere Quelle uebergeblendet.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

# Groessere Versaetze sind kein Bezugssystem-Unterschied, sondern Unsinn
# (z. B. falsche Kachel); dann wird nicht verschoben.
MAX_OFFSET_M = 30.0
# Mindestzahl gemeinsamer Pixel fuer einen Hoehenausgleich
MIN_OVERLAP_PIXELS = 50
DEFAULT_BLEND_M = 150.0
MAX_SOURCES = 3
# Quellen mit kleinerem Flaechenanteil (z. B. ein paar Randpixel aus Copernicus)
# werden in Anzeige und Teilen-Text nicht genannt.
MIN_SHOWN_SHARE = 0.001

# Laendergrenzen grob als (lat_min, lat_max, lon_min, lon_max); None = weltweit
_GERMANY_BOUNDS = (47.2, 55.1, 5.8, 15.1)


def source_bounds(source: str):
    """Grobe Ausdehnung einer Quelle, None = ueberall (Copernicus, eigene Dateien)."""

    from src.heightmap.heightmap_exporter import (
        SOURCE_AHN_NL,
        SOURCE_BEV_AT,
        SOURCE_DGM1_DE,
        SOURCE_LUX,
        SOURCE_SWISSALTI3D,
    )
    from src.heightmap.ahn_nl_dem import NL_BOUNDS
    from src.heightmap.bev_dem import AT_BOUNDS
    from src.heightmap.lux2169 import LU_BOUNDS
    from src.heightmap.lv95 import SWISS_BOUNDS

    return {
        SOURCE_DGM1_DE: _GERMANY_BOUNDS,
        SOURCE_SWISSALTI3D: SWISS_BOUNDS,
        SOURCE_AHN_NL: NL_BOUNDS,
        SOURCE_BEV_AT: AT_BOUNDS,
        SOURCE_LUX: LU_BOUNDS,
    }.get(source)


def touches(corners, bounds) -> bool:
    """Beruehrt das Rechteck (Eckpunkte lat/lon) die grobe Ausdehnung?"""

    if bounds is None:
        return True

    lats = [c[0] for c in corners]
    lons = [c[1] for c in corners]
    lat_min, lat_max, lon_min, lon_max = bounds

    return not (
        max(lats) < lat_min or min(lats) > lat_max
        or max(lons) < lon_min or min(lons) > lon_max
    )


def priority_order(sources) -> list[str]:
    """Reihenfolge beim Kombinieren: doppelte raus, Copernicus immer zuletzt.

    Copernicus deckt alles ab und wuerde als oberste Quelle die genaueren
    Quellen ganz verdecken; es ist nur der Lueckenfueller.
    """

    from src.heightmap.heightmap_exporter import SOURCE_COPERNICUS

    order = []

    for source in sources:
        if source and source not in order:
            order.append(source)

    if SOURCE_COPERNICUS in order:
        order.remove(SOURCE_COPERNICUS)
        order.append(SOURCE_COPERNICUS)

    return order


def source_name(source: str) -> str:
    """Kurzer Anzeigename einer Hoehenquelle."""

    from src.heightmap.heightmap_exporter import (
        SOURCE_AHN_NL,
        SOURCE_BEV_AT,
        SOURCE_COPERNICUS,
        SOURCE_DGM1_DE,
        SOURCE_DGM1_FOLDER,
        SOURCE_LUX,
        SOURCE_SWISSALTI3D,
    )
    from src.i18n import tr

    return {
        SOURCE_COPERNICUS: "Copernicus",
        SOURCE_DGM1_DE: "DGM1",
        SOURCE_DGM1_FOLDER: tr("Eigene Höhendateien"),
        SOURCE_SWISSALTI3D: "swissALTI3D",
        SOURCE_AHN_NL: "AHN",
        SOURCE_BEV_AT: "BEV",
        SOURCE_LUX: "MNT Luxemburg",
    }.get(source, source)


def combined_summary(info) -> str:
    """Z. B. "DGM1 61,8 %, MNT Luxemburg 36,9 %, Copernicus 1,3 %"."""

    from src.i18n import get_language

    parts = []

    for source, share in zip(info.combined, info.shares):
        if share < MIN_SHOWN_SHARE:
            continue
        percent = f"{share * 100:.1f}"
        if get_language() == "de":
            percent = percent.replace(".", ",")
        parts.append(f"{source_name(source)} {percent} %")

    return ", ".join(parts)


def combine_layers(
    layers,
    pixel_m: float = 4.0,
    blend_m: float = DEFAULT_BLEND_M,
    max_offset_m: float = MAX_OFFSET_M,
):
    """
    layers: Liste gleich grosser Raster (NaN = keine Daten), oberste Quelle zuerst.

    Gibt (Raster, Quellen-Index je Pixel, Hoehenausgleich je Quelle) zurueck.
    Der Index ist -1, wo keine Quelle Daten hat (dort bleibt NaN).
    """

    from scipy.ndimage import distance_transform_edt

    if not layers:
        raise ValueError("Keine Hoehenquelle zum Kombinieren.")

    shape = np.shape(layers[0])

    for layer in layers:
        if np.shape(layer) != shape:
            raise ValueError("Die Hoehenraster der Quellen sind unterschiedlich gross.")

    count = len(layers)
    result = np.array(layers[-1], dtype=np.float64)
    used = np.where(np.isnan(result), -1, count - 1).astype(np.int8)
    offsets = [0.0] * count
    blend_px = max(0.0, float(blend_m) / float(pixel_m)) if pixel_m > 0 else 0.0

    for index in range(count - 2, -1, -1):
        top = np.asarray(layers[index], dtype=np.float64)
        have = ~np.isnan(top)

        if not have.any():
            continue

        base_ok = ~np.isnan(result)
        both = have & base_ok

        shift = 0.0

        if int(both.sum()) >= MIN_OVERLAP_PIXELS:
            shift = float(np.median(top[both] - result[both]))

            if abs(shift) > max_offset_m:
                shift = 0.0

        if shift:
            result = result + shift

            for lower in range(index + 1, count):
                offsets[lower] += shift

        if blend_px >= 1.0:
            weight = np.clip(distance_transform_edt(have) / blend_px, 0.0, 1.0)
        else:
            weight = have.astype(np.float64)

        weight[~base_ok] = 1.0
        weight[~have] = 0.0

        only_top = have & ~base_ok
        result = result.copy()
        result[both] = weight[both] * top[both] + (1.0 - weight[both]) * result[both]
        result[only_top] = top[only_top]

        used = np.where(have & (~base_ok | (weight >= 0.5)), index, used).astype(np.int8)

    return result.astype(np.float32), used, offsets


def source_shares(used: np.ndarray, count: int) -> list[float]:
    """Flaechenanteil je Quelle (0..1)."""

    total = used.size

    if total == 0:
        return [0.0] * count

    return [float((used == i).sum()) / total for i in range(count)]


def build_heightmap_array_multi(
    selection,
    cache_dir: Path,
    sources,
    blend_m: float = DEFAULT_BLEND_M,
    control=None,
    **source_args,
):
    """
    Baut das Hoehenraster aus bis zu drei Quellen (oberste zuerst). Bleiben
    Luecken, wird wie gewohnt aus Copernicus ergaenzt.

    source_args: dieselben Verzeichnisse wie bei build_heightmap_array_ex
    (dgm1_cache_dir, dgm1_folder, swiss_cache_dir, ...).
    """

    from src.heightmap.heightmap_exporter import (
        METERS_PER_PIXEL,
        SOURCE_COPERNICUS,
        SOURCE_TPF2_PNG,
        HeightmapBuildInfo,
        _apply_height_scale,
        build_heightmap_array_ex,
    )
    from src.core.task_control import ScaledControl
    from src.i18n import tr

    order = priority_order(sources)

    if not order:
        raise ValueError(tr("Keine Höhenquelle gewählt."))

    if SOURCE_TPF2_PNG in order:
        raise ValueError(tr("Eine eigene TPF2-Heightmap lässt sich nicht mit anderen Quellen kombinieren."))

    if len(order) > MAX_SOURCES:
        raise ValueError(tr("Höchstens {count} Höhenquellen lassen sich kombinieren.").format(count=MAX_SOURCES))

    layers = []
    infos = []

    # Fortschritt: jede Quelle bekommt ihren Teil, der Rest fuer die Ergaenzung
    part = 0.9 / len(order)

    for number, source in enumerate(order):
        step = ScaledControl(control, number * part, (number + 1) * part) if control is not None else None
        array, info = build_heightmap_array_ex(
            selection,
            cache_dir,
            source,
            control=step,
            raw=True,
            **source_args,
        )
        layers.append(array)
        infos.append(info)

    pixel_m = METERS_PER_PIXEL * float(getattr(selection, "scale_factor", 1.0) or 1.0)
    out, used, offsets = combine_layers(layers, pixel_m=pixel_m, blend_m=blend_m)

    auto_copernicus = False

    if np.isnan(out).any() and SOURCE_COPERNICUS not in order:
        step = ScaledControl(control, 0.9, 1.0) if control is not None else None
        array, info = build_heightmap_array_ex(
            selection, cache_dir, SOURCE_COPERNICUS, control=step, raw=True,
        )
        order.append(SOURCE_COPERNICUS)
        layers.append(array)
        infos.append(info)
        auto_copernicus = True
        out, used, offsets = combine_layers(layers, pixel_m=pixel_m, blend_m=blend_m)

    if np.isnan(out).any():
        raise RuntimeError(
            tr("Hoehendaten decken den Kartenausschnitt nicht vollstaendig ab "
            "(evtl. fehlt eine Randkachel).")
        )

    shares = source_shares(used, len(order))

    attributions = []
    actualities = []
    missing = 0

    for info in infos:
        for text in info.attributions:
            if text not in attributions:
                attributions.append(text)
        for text in info.actualities:
            if text not in actualities:
                actualities.append(text)
        missing += int(info.missing_tiles)

    sea = None

    if SOURCE_COPERNICUS in order:
        cop = order.index(SOURCE_COPERNICUS)
        cop_sea = infos[cop].sea_mask

        if cop_sea is not None:
            sea = np.asarray(cop_sea) & (used == cop)

            if not sea.any():
                sea = None

    info = HeightmapBuildInfo(
        source=order[0],
        fallback_fraction=shares[-1] if auto_copernicus else 0.0,
        missing_tiles=missing,
        attributions=attributions,
        actualities=sorted(actualities),
        sea_mask=sea,
        combined=list(order),
        shares=shares,
        offsets=[float(o) for o in offsets],
    )

    return _apply_height_scale(out, selection), info
