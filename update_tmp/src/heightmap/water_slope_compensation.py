"""
Gefälle-Ausgleich ("Karte vertikal gerade richten").

Problem: TPF2/TPF3 kennen kein Wassergefälle - Flüsse und Seen liegen dort
immer auf EINER Höhe. Echte Höhendaten haben aber Gefälle: liegt ein Fluss
am einen Ende 100 m höher als am anderen, gibt es im Spiel entweder
trockene Flussbetten oder man müsste tiefe Canyons graben. Die Uferanpassung
(water_terrain_blend) hilft nur in einem schmalen Streifen direkt am Wasser.

Dieses Modul geht einen Schritt weiter:

1. Es schätzt für JEDEN Punkt der Karte, auf welcher Höhe das nächstgelegene
   (Bezugs-)Gewässer in der Realität liegt - geglättet über die Karte.
2. Es zieht diese "Wasseroberfläche" von der Karte ab und legt sie auf das
   gewünschte Spiel-Wasserniveau.

Ergebnis: Das Wasser liegt überall auf derselben Ebene, Hänge und Berge
behalten ihre Höhe über dem ÖRTLICHEN Wasserspiegel. Die absoluten Höhen
über NN stimmen danach nicht mehr - bewusster Kompromiss zugunsten einer
Karte, die sich im Spiel ohne Nacharbeit umsetzen lässt.

Rechenaufwand: Die Wasseroberfläche ist per Definition glatt (Glättung über
hunderte Meter), deshalb wird sie auf einem grob aufgelösten Feld berechnet
und erst danach auf die volle Auflösung hochgerechnet. Das ist um Größen-
ordnungen schneller als eine Glättung auf 4 m/Pixel und verliert nichts.
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, gaussian_filter

from src.heightmap.water_terrain_blend import filter_small_water_bodies


DEFAULT_SMOOTHING_M = 400.0

# Zellgroesse des groben Feldes, auf dem die Wasseroberflaeche berechnet wird.
FIELD_PIXEL_SIZE_M = 32.0

# Reine Wasserflaechen unter dieser Pixelzahl gelten nicht als Bezugswasser
# (einzelne Tuempel/Kurzstuecke sagen nichts ueber das Gefaelle der Gegend aus).
DEFAULT_MIN_REFERENCE_AREA_PX = 200


def _reduce_to_low_res(
    heightmap: np.ndarray,
    water_mask: np.ndarray,
    factor: int,
) -> tuple[np.ndarray, np.ndarray] | None:
    """
    Verdichtet Wassermaske und -hoehen auf ein Raster, das 'factor' mal
    gröber ist. Pro Zelle: liegt irgendein Wasserpixel darin, ist die
    Zelle Wasser, ihre Höhe der Mittelwert der darin liegenden
    Wasserpixel. Arbeitet in Zeilenblöcken, damit keine riesigen
    Zwischenkopien des vollen Rasters entstehen.

    Liefert None, wenn die Maske kein Wasser enthält.
    """

    h, w = heightmap.shape

    low_h = -(-h // factor)
    low_w = -(-w // factor)

    counts = np.zeros((low_h, low_w), dtype=np.int64)
    sums = np.zeros((low_h, low_w), dtype=np.float64)

    rows_per_chunk = factor * 64  # Vielfaches von factor

    for r0 in range(0, h, rows_per_chunk):

        r1 = min(h, r0 + rows_per_chunk)

        mask_chunk = water_mask[r0:r1]

        if not mask_chunk.any():
            continue

        height_chunk = heightmap[r0:r1]

        pad_rows = (-(r1 - r0)) % factor
        pad_cols = (-w) % factor

        if pad_rows or pad_cols:
            mask_chunk = np.pad(mask_chunk, ((0, pad_rows), (0, pad_cols)))
            height_chunk = np.pad(height_chunk, ((0, pad_rows), (0, pad_cols)))

        blocks_h = mask_chunk.shape[0] // factor
        blocks_w = mask_chunk.shape[1] // factor

        mask_blocks = mask_chunk.reshape(blocks_h, factor, blocks_w, factor)
        height_blocks = (height_chunk * mask_chunk).reshape(
            blocks_h, factor, blocks_w, factor
        )

        b0 = r0 // factor

        counts[b0:b0 + blocks_h, :] += mask_blocks.sum(axis=(1, 3))
        sums[b0:b0 + blocks_h, :] += height_blocks.sum(
            axis=(1, 3), dtype=np.float64
        )

    has_water = counts > 0

    if not has_water.any():
        return None

    low_height = np.zeros_like(sums)
    low_height[has_water] = sums[has_water] / counts[has_water]

    return has_water, low_height


def estimate_water_surface(
    heightmap: np.ndarray,
    water_mask: np.ndarray,
    pixel_size_m: float,
    smoothing_m: float = DEFAULT_SMOOTHING_M,
    field_pixel_size_m: float = FIELD_PIXEL_SIZE_M,
) -> np.ndarray | None:
    """
    Schätzt für jeden Punkt der Karte die Höhe des nächstgelegenen
    Gewässers, geglättet über smoothing_m Meter. Liefert ein float32-Raster
    in voller Auflösung - oder None, wenn die Maske kein Wasser enthält.
    """

    h, w = heightmap.shape

    factor = max(1, int(round(field_pixel_size_m / pixel_size_m)))

    reduced = _reduce_to_low_res(heightmap, water_mask, factor)

    if reduced is None:
        return None

    has_water, low_height = reduced

    # Für jede Zelle den Index der nächstgelegenen Wasserzelle bestimmen
    # und deren Höhe übernehmen (Voronoi-artiges, noch blockiges Feld).
    nearest = distance_transform_edt(
        ~has_water,
        return_distances=False,
        return_indices=True,
    )

    nearest_height = low_height[nearest[0], nearest[1]]

    # Glätten: entfernt die Blockstruktur und die Sprünge zwischen den
    # Einzugsgebieten verschiedener Gewässer.
    sigma_cells = max(0.5, smoothing_m / (factor * pixel_size_m))

    # Randbehandlung: Wuerde man das Feld am Kartenrand einfach konstant
    # fortsetzen (mode="nearest"), zoege die Glaettung ein gleichmaessiges
    # Gefaelle dort flach (Fehler ca. Gefaelle x Glaettungsradius x 0.4 -
    # bei 6 % Gefaelle und 200 m Radius rund 5 m). Deshalb wird das Feld
    # vor dem Glaetten punktgespiegelt ("odd") ueber den Rand hinaus
    # fortgesetzt: ein lineares Gefaelle bleibt dadurch bis zum Rand exakt
    # erhalten.
    pad = int(np.ceil(3.0 * sigma_cells)) + 1

    padded = np.pad(nearest_height, pad, mode="reflect", reflect_type="odd")

    smooth_padded = gaussian_filter(
        padded, sigma=sigma_cells, truncate=3.0, mode="nearest"
    )

    smooth = smooth_padded[pad:-pad, pad:-pad]

    # Auf volle Auflösung hochrechnen (bilinear).
    field_image = Image.fromarray(smooth.astype(np.float32))

    upscaled = field_image.resize((w, h), Image.Resampling.BILINEAR)

    # np.array (statt np.asarray) liefert eine beschreibbare Kopie - die
    # PIL-Ansicht waere schreibgeschuetzt, compensate_water_slope rechnet
    # aber in-place darauf weiter.
    return np.array(upscaled, dtype=np.float32)


def compensate_water_slope(
    heightmap: np.ndarray,
    water_mask: np.ndarray,
    water_level_m: float,
    pixel_size_m: float,
    strength: float = 1.0,
    smoothing_m: float = DEFAULT_SMOOTHING_M,
    min_area_px: float | None = DEFAULT_MIN_REFERENCE_AREA_PX,
    max_reference_height_above_water_m: float | None = None,
) -> np.ndarray:
    """
    Legt die Bezugsgewässer auf water_level_m und zieht das Gelände
    relativ dazu mit. Liefert eine NEUE Kopie, heightmap bleibt unverändert.

    strength: 0.0 = keine Wirkung, 1.0 = vollständig auf eine Ebene.
    smoothing_m: Glättungsradius der Wasseroberfläche - je größer, desto
        weicher/großräumiger der Ausgleich.
    min_area_px: Gewässer unter dieser Pixelzahl gelten nicht als Bezug.
    max_reference_height_above_water_m: Nur Gewässerpixel, deren Höhe höchstens
        so viel über water_level_m liegt, dienen als Bezug. Ohne diese Grenze
        wirken auch Nebenflüsse und Bergseen hoch im Gelände als Bezug: das
        Gelände in ihrer Nähe wird dann um deren volle Höhe nach unten
        gezogen (Beispiel: ein Fluss bei 200 m drückt sein Tal um 140 m
        unter den Wasserspiegel und flutet es). None = keine Begrenzung.
    """

    if heightmap.shape != water_mask.shape:
        raise ValueError(
            "heightmap und water_mask müssen dieselbe Form haben "
            f"({heightmap.shape} != {water_mask.shape})"
        )

    strength = float(min(1.0, max(0.0, strength)))

    if strength == 0.0:
        return heightmap.copy()

    reference_mask = water_mask

    if max_reference_height_above_water_m is not None:
        reference_mask = reference_mask & (
            heightmap <= water_level_m + max_reference_height_above_water_m
        )

    if min_area_px:
        reference_mask = filter_small_water_bodies(reference_mask, min_area_px)

    surface = estimate_water_surface(
        heightmap,
        reference_mask,
        pixel_size_m,
        smoothing_m=smoothing_m,
    )

    if surface is None:
        # Kein (ausreichend grosses) Bezugswasser - nichts zu tun.
        return heightmap.copy()

    # surface wird in-place zur Korrektur umgerechnet (spart eine
    # weitere Kopie des vollen Rasters).
    surface -= np.float32(water_level_m)
    surface *= np.float32(strength)

    result = heightmap - surface

    return result.astype(heightmap.dtype, copy=False)
