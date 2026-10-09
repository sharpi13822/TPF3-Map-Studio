"""
Automatischer Wasserhoehen-Vorschlag und Vorschau-Bild fuer den
Heightmap-Export.

Reine Minimum-Suche ist unzuverlaessig: am aeussersten Kartenrand koennen
einzelne Pixel durch Interpolation leicht zu niedrig ausfallen, und
einzelne sehr tiefe Bergbau-Restloecher sind kein sinnvoller Bezugspunkt
fuer den globalen Wasserstand der ganzen Karte. Deshalb: robuste
Perzentil-Schaetzung statt Minimum, mit den Randpixeln ausgeschlossen.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.heightmap.height_clipping import CHANGE_TOLERANCE_M, normalize_heights
from src.i18n import tr

EDGE_MARGIN_PX = 3
SUGGESTION_PERCENTILE = 7.5

# Fuer die Ausreisser-Erkennung im Hoehenbereich (nicht fuer den
# Wasserhoehen-Vorschlag, der ist bereits ueber die Perzentil-Methode
# robust): Tukeys "extreme Ausreisser"-Faustregel (3x statt der ueblichen
# 1.5x IQR) - bewusst konservativ, damit normale, glatte Gelaende-
# Verteilungen KEINEN Fehlalarm ausloesen (reine Perzentil-Grenzen wie
# z.B. 0.5/99.5 wuerden das tun, da per Definition immer ~1% der Flaeche
# ausserhalb liegt, auch ohne jede Anomalie).
OUTLIER_IQR_FACTOR = 3.0


# Einfaerbung der vom Hoehenfenster veraenderten Stellen in der Vorschau
CLIP_LOWERED_RGB = (220, 50, 50)    # tiefer gesetzt: oben gekappt oder gestaucht
CLIP_RAISED_RGB = (60, 220, 240)    # hoeher gesetzt: unten abgeschnitten
CLIP_BLEND = 0.7


def _blend(rgb: np.ndarray, mask: np.ndarray, color) -> np.ndarray:
    if not mask.any():
        return rgb

    out = rgb.copy()
    mixed = rgb[mask].astype(np.float32) * (1.0 - CLIP_BLEND) + np.array(color, dtype=np.float32) * CLIP_BLEND
    out[mask] = np.clip(mixed, 0, 255).astype(np.uint8)
    return out


@dataclass
class WaterLevelSuggestion:
    suggested_m: float
    p5: float
    p10: float
    range_min_m: float  # "Höhenbereich" Minimum, wie im TPF2-Importfenster
    range_max_m: float  # "Höhenbereich" Maximum, wie im TPF2-Importfenster
    note: str
    # Ausreisser-Erkennung (rein informativ - range_min_m/range_max_m
    # bleiben bewusst das echte Minimum/Maximum, damit sich am
    # Exportverhalten nichts aendert, ohne dass der Nutzer das explizit
    # waehlt; siehe robust_range_min_m/robust_range_max_m fuer die
    # Alternative ohne Ausreisser):
    outlier_count: int = 0
    outlier_fraction: float = 0.0
    robust_range_min_m: float = 0.0
    robust_range_max_m: float = 0.0


def suggest_water_level(heightmap: np.ndarray) -> WaterLevelSuggestion:
    core = heightmap[EDGE_MARGIN_PX:-EDGE_MARGIN_PX, EDGE_MARGIN_PX:-EDGE_MARGIN_PX]
    if core.size == 0:
        core = heightmap

    p5, p10 = np.percentile(core, [5, 10])
    suggested = float(np.percentile(core, SUGGESTION_PERCENTILE))

    range_min = float(np.floor(heightmap.min()))
    range_max = float(np.ceil(heightmap.max()))

    # Ausreisser-Erkennung: Pixel weit ausserhalb von Tukeys "extreme
    # Ausreisser"-Grenze (Q1 - 3xIQR / Q3 + 3xIQR) der Kernflaeche (ohne
    # Rand) - typischerweise einzelne sehr tiefe Bergbau-Restloecher oder
    # Rand-Artefakte, nicht die normale Streuung des Gelaendes.
    q1, q3 = np.percentile(core, [25, 75])
    iqr = q3 - q1
    robust_low = q1 - OUTLIER_IQR_FACTOR * iqr
    robust_high = q3 + OUTLIER_IQR_FACTOR * iqr

    outlier_mask = (heightmap < robust_low) | (heightmap > robust_high)
    outlier_count = int(outlier_mask.sum())
    outlier_fraction = outlier_count / heightmap.size if heightmap.size else 0.0

    # Die robuste Alternativ-Spanne soll trotzdem am tatsaechlichen
    # Datenbereich anliegen (nicht an der theoretischen Fence), falls
    # kein Pixel so weit draussen liegt:
    if outlier_count > 0:
        robust_range_min = float(np.floor(heightmap[~outlier_mask].min()))
        robust_range_max = float(np.ceil(heightmap[~outlier_mask].max()))
    else:
        robust_range_min = range_min
        robust_range_max = range_max

    note = (
        tr("Vorschlag basiert auf dem {SUGGESTION_PERCENTILE}. Perzentil der Fläche (ohne die äußersten {EDGE_MARGIN_PX} Pixel Rand), das erfahrungsgemäß dem natürlichen Flussniveau entspricht. Bleiben nach dem Import Flüsse trocken, einen höheren Wert probieren; steht zu viel Fläche unter Wasser, einen niedrigeren.").format(SUGGESTION_PERCENTILE=SUGGESTION_PERCENTILE, EDGE_MARGIN_PX=EDGE_MARGIN_PX)
    )

    if outlier_count > 0:

        note += (
            tr("\n\nHinweis: {outlier_count} Pixel ({value:.2f}% der Fläche) liegen deutlich außerhalb des üblichen Höhenbereichs der restlichen Fläche (z.B. einzelne Bergbau-Restlöcher oder Rand-Artefakte) - Höhenbereich {range_min:.0f}–{range_max:.0f} m. Ohne diese Ausreißer läge er bei {robust_range_min:.0f}–{robust_range_max:.0f} m, was mehr 16-Bit-Präzision für das eigentliche Gelände übrig lässt. Der Export nutzt weiterhin den vollen Bereich (nichts geht verloren), außer du wählst im Dialog explizit die engere Spanne.").format(outlier_count=outlier_count, value=outlier_fraction * 100, range_min=range_min, range_max=range_max, robust_range_min=robust_range_min, robust_range_max=robust_range_max)
        )

    return WaterLevelSuggestion(
        suggested_m=round(suggested),
        p5=float(p5),
        p10=float(p10),
        range_min_m=range_min,
        range_max_m=range_max,
        note=note,
        outlier_count=outlier_count,
        outlier_fraction=outlier_fraction,
        robust_range_min_m=robust_range_min,
        robust_range_max_m=robust_range_max,
    )


def hillshade(
    heights: np.ndarray,
    cell_size_m: float,
    azimuth_deg: float = 315.0,
    altitude_deg: float = 45.0,
    z_factor: float = 2.0,
) -> np.ndarray:
    """
    Schattenrelief. Liefert pro Pixel k = Helligkeit relativ zur ebenen
    Flaeche (1.0 = eben, < 1 Schattenseite, > 1 Lichtseite).

    Das Raster laeuft wie ein Bild: Zeilen nach unten, Spalten nach rechts.
    Licht kommt aus azimuth_deg (0 = oben/Norden, 90 = rechts/Osten,
    315 = oben links) in altitude_deg Grad Hoehe. Bei einem gedrehten
    Kartenband gilt "oben" relativ zum Band, nicht zum echten Norden.
    """

    z = np.nan_to_num(heights.astype(np.float64), nan=0.0)

    dz_dr, dz_dc = np.gradient(z, cell_size_m, cell_size_m)

    # Flaechennormale (x = rechts, y = oben): Zeilen laufen nach unten,
    # daher +dz/dr fuer die Komponente nach oben.
    nx = -dz_dc * z_factor
    ny = dz_dr * z_factor

    az = np.radians(azimuth_deg)
    alt = np.radians(altitude_deg)

    lx = np.sin(az) * np.cos(alt)
    ly = np.cos(az) * np.cos(alt)
    lz = np.sin(alt)

    shade = (nx * lx + ny * ly + lz) / np.sqrt(nx * nx + ny * ny + 1.0)

    return shade / lz


def render_preview(
    heightmap: np.ndarray,
    water_level_m: float,
    range_min_m: float,
    range_max_m: float,
    output_path: Path | None = None,
    max_size_px: int = 900,
    pixel_size_m: float | None = None,
    original_heightmap: np.ndarray | None = None,
):
    """Vorschau wie im TPF2-Importfenster: graues Gelaende-Relief,
    Wasserflaeche blau eingefaerbt, mit Min/Max und Wasserhoehe als
    Beschriftung. Gibt ein PIL.Image zurueck.

    Mit original_heightmap (das Raster VOR dem Hoehenfenster, gleiche Form wie
    heightmap) werden die vom Hoehenfenster veraenderten Stellen eingefaerbt:
    Rot = tiefer gesetzt (oben gekappt oder gestaucht), Hellblau = hoeher gesetzt
    (unten abgeschnitten)."""

    from PIL import Image, ImageDraw

    h, w = heightmap.shape
    step = max(1, max(h, w) // max_size_px)
    small = heightmap[::step, ::step]

    norm = normalize_heights(small, range_min_m, range_max_m)
    gray = norm * 200 + 30

    # Mit pixel_size_m (Meter pro Pixel des vollen Rasters) wird das Relief
    # zusaetzlich schattiert - Taeler, Haenge und Kaemme sind damit viel
    # besser zu erkennen als in reinem Grau.
    if pixel_size_m:
        k = hillshade(small, pixel_size_m * step)
        gray = gray * np.clip(0.45 + 0.55 * k, 0.2, 1.25)

    gray = np.clip(gray, 0, 255).astype(np.uint8)
    rgb = np.stack([gray, gray, gray], axis=-1)

    water_mask = small <= water_level_m
    rgb[water_mask] = [40, 90, 120]

    if original_heightmap is not None:
        original_small = original_heightmap[::step, ::step]
        lowered = small < original_small - CHANGE_TOLERANCE_M
        raised = small > original_small + CHANGE_TOLERANCE_M
        rgb = _blend(rgb, lowered, CLIP_LOWERED_RGB)
        rgb = _blend(rgb, raised, CLIP_RAISED_RGB)

    img = Image.fromarray(rgb, mode="RGB")

    draw = ImageDraw.Draw(img)
    line1 = tr("Höhenbereich: {range_min_m:.0f} – {range_max_m:.0f} m").format(range_min_m=range_min_m, range_max_m=range_max_m)
    line2 = tr("Wasserhöhe: {water_level_m:.0f} m").format(water_level_m=water_level_m)
    bar_h = 34
    draw.rectangle([0, 0, img.width, bar_h], fill=(20, 20, 20))
    draw.text((6, 3), line1, fill=(255, 255, 255))
    draw.text((6, 18), line2, fill=(150, 200, 255))

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)

    return img