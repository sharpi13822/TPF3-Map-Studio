"""Export-Einstellungen eines Projekts (ohne Qt, einzeln testbar).

Gespeichert wird nur, was gueltig ist. Ein fehlender Schluessel heisst:
Der Dialog behaelt seinen eigenen Standardwert.
"""

from __future__ import annotations

import math

BOOL_KEYS = (
    "smooth",
    "flatten",
    "slope",
    "enforce",
    "water_blend",
    "sea",
    "clip",
    "relative_values",
    "zones",
)

FLOAT_KEYS = (
    "water_level",
    "compress",
    "smooth_sigma",
    "flatten_sigma",
    "slope_strength",
    "slope_smoothing",
    "slope_max_ref",
    "sea_depth",
    "enforce_transition",
    "enforce_edge",
    "enforce_depth",
    "enforce_bank",
    "enforce_max_rise",
    "blend_transition",
    "blend_max_rise",
    "clip_min",
    "clip_max",
    "rock",
    "snow",
)

CLIP_MODES = ("top", "bottom", "compress")


def sanitize_export_settings(raw) -> dict:
    """Gibt nur gueltige Eintraege zurueck, alles andere wird verworfen."""

    if not isinstance(raw, dict):
        return {}

    result = {}

    for key in BOOL_KEYS:
        if isinstance(raw.get(key), bool):
            result[key] = raw[key]

    for key in FLOAT_KEYS:
        value = raw.get(key)
        if (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        ):
            result[key] = float(value)

    source = raw.get("source")
    if isinstance(source, str) and source:
        result["source"] = source

    if raw.get("clip_mode") in CLIP_MODES:
        result["clip_mode"] = raw["clip_mode"]

    # Weitere Hoehenquellen (kombinieren): Liste von Namen, hoechstens zwei
    combine = raw.get("combine_sources")
    if isinstance(combine, list):
        names = []
        for name in combine:
            if isinstance(name, str) and name and name not in names:
                names.append(name)
        if names:
            result["combine_sources"] = names[:2]

    blend = raw.get("combine_blend")
    if (
        isinstance(blend, (int, float))
        and not isinstance(blend, bool)
        and math.isfinite(blend)
    ):
        result["combine_blend"] = float(min(1000.0, max(0.0, blend)))

    return result