"""
Hoehenfenster fuer den TPF3-Import: Was der Karteneditor annimmt, und was mit
Hoehen ausserhalb des gewaehlten Fensters passiert.

Der Editor von TPF3 nimmt beim Heightmap-Import nur Werte von GAME_MIN_M bis
GAME_MAX_M (im Spiel getestet: -20 bis 3177 m). Liegt das Gelaende (zum Beispiel
in den Alpen) ausserhalb, muss es in ein Fenster gelegt werden. Alle Rechnungen
dazu stehen hier, damit Vorschau, Zahlen im Dialog und Export dasselbe Raster
und dieselbe Normierung benutzen.

Alle Hoehen in diesem Modul sind "echte" Hoehen des Rasters (Meter ueber Meer).
Der Dialog rechnet die Eintragswerte des Editors (bei "Werte auf Wasserhoehe 0
beziehen" relativ zur Wasserhoehe) vorher um.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Grenzen der Werte, die der Karteneditor von TPF3 beim Import annimmt
# (Eintragswerte Mindest- und Maximalhoehe, im Spiel getestet).
GAME_MIN_M = -20.0
GAME_MAX_M = 3177.0
GAME_MAX_SPAN_M = GAME_MAX_M - GAME_MIN_M

# Modi fuer Werte ausserhalb des Fensters
MODE_CAP = "cap"          # oben kappen: Gipfel werden flach auf die Obergrenze gesetzt
MODE_CUT = "cut"          # unten abschneiden: Tiefen werden flach auf die Untergrenze gesetzt
MODE_SQUEEZE = "squeeze"  # stauchen: das ganze Gelaende wird ins Fenster gedrueckt

MODES = (MODE_CAP, MODE_CUT, MODE_SQUEEZE)

# Kleinere Aenderungen (Meter) zaehlen nicht als "veraendert".
CHANGE_TOLERANCE_M = 0.05

# Kleinste erlaubte Fensterhoehe in Metern.
MIN_WINDOW_M = 1.0


@dataclass
class ClipReport:
    """Was das Hoehenfenster mit dem Raster gemacht hat."""

    mode: str
    window_min_m: float
    window_max_m: float
    data_min_m: float
    data_max_m: float
    # Anteile der Rasterflaeche (0..1), die tiefer bzw. hoeher gesetzt wurden
    lowered_fraction: float = 0.0
    raised_fraction: float = 0.0
    # Nur beim Stauchen: Faktor ueber bzw. unter dem Bezugspunkt (1 = unveraendert)
    scale_up: float = 1.0
    scale_down: float = 1.0

    @property
    def changed_fraction(self) -> float:
        return self.lowered_fraction + self.raised_fraction


def normalize_heights(
    heightmap: np.ndarray,
    range_min_m: float,
    range_max_m: float,
) -> np.ndarray:
    """
    Bildet Hoehen auf 0..1 ab (range_min_m = 0, range_max_m = 1, ausserhalb
    abgeschnitten). Die Vorschau und der PNG-Export benutzen genau diese Funktion.
    """

    return np.clip((heightmap - range_min_m) / (range_max_m - range_min_m), 0, 1)


def apply_height_window(
    heights: np.ndarray,
    win_min: float,
    win_max: float,
    mode: str = MODE_CAP,
    anchor: float | None = None,
) -> tuple[np.ndarray, ClipReport]:
    """
    Legt das Raster in das Fenster win_min..win_max. Liefert eine NEUE Kopie
    (float32), die Eingabe bleibt unveraendert, und einen Bericht.

    MODE_CAP und MODE_CUT setzen alles ausserhalb des Fensters flach auf die
    naechste Grenze. Sie unterscheiden sich nur darin, wo der Dialog das Fenster
    voreinstellt (CAP: an der tiefsten Stelle, die Gipfel werden gekappt; CUT: an
    der hoechsten Stelle, die Tiefen werden abgeschnitten).

    MODE_SQUEEZE drueckt das ganze Gelaende ins Fenster, ohne zu strecken (ein
    Gelaende, das schon passt, bleibt unveraendert). anchor ist ein Bezugspunkt
    (der Dialog gibt die Wasserhoehe), der nicht verschoben wird: darueber und
    darunter wird getrennt gestaucht, so dass das Wasserniveau erhalten bleibt.
    Ohne anchor wird von der tiefsten Stelle aus gestaucht.
    """

    if mode not in MODES:
        raise ValueError(f"Unbekannter Modus: {mode}")

    if not win_max > win_min:
        raise ValueError("Die Obergrenze des Fensters muss ueber der Untergrenze liegen.")

    src = np.asarray(heights)
    h = src.astype(np.float32, copy=False)

    data_min = float(h.min())
    data_max = float(h.max())

    scale_up = 1.0
    scale_down = 1.0

    if mode in (MODE_CAP, MODE_CUT):

        out = np.clip(h, np.float32(win_min), np.float32(win_max))

    else:

        a_in = data_min if anchor is None else min(max(float(anchor), data_min), data_max)
        a_out = min(max(a_in, win_min), win_max)

        if data_max > a_in:
            scale_up = min(1.0, (win_max - a_out) / (data_max - a_in))

        if a_in > data_min:
            scale_down = min(1.0, (a_out - win_min) / (a_in - data_min))

        above = h >= np.float32(a_in)

        out = np.where(
            above,
            a_out + (h - a_in) * scale_up,
            a_out - (a_in - h) * scale_down,
        ).astype(np.float32)

        # Rundungsfehler duerfen das Fenster nicht verlassen
        out = np.clip(out, np.float32(win_min), np.float32(win_max))

    size = out.size or 1

    lowered = float(np.count_nonzero(out < h - np.float32(CHANGE_TOLERANCE_M))) / size
    raised = float(np.count_nonzero(out > h + np.float32(CHANGE_TOLERANCE_M))) / size

    report = ClipReport(
        mode=mode,
        window_min_m=float(win_min),
        window_max_m=float(win_max),
        data_min_m=data_min,
        data_max_m=data_max,
        lowered_fraction=lowered,
        raised_fraction=raised,
        scale_up=scale_up,
        scale_down=scale_down,
    )

    return out, report


def default_window(
    data_min: float,
    data_max: float,
    mode: str,
    width: float | None = None,
) -> tuple[float, float]:
    """
    Voreinstellung des Fensters in Eintragswerten (so, wie sie im Editor stehen).
    Ausgangspunkt ist der Bereich des Geländes innerhalb der Editor-Grenzen. Mit
    width (kleiner als dieser Bereich) bestimmt der Modus, wo das Fenster liegt:
    CAP an der tiefsten Stelle, CUT an der hoechsten, SQUEEZE immer ueber dem
    ganzen Bereich.
    """

    if mode not in MODES:
        raise ValueError(f"Unbekannter Modus: {mode}")

    low = max(data_min, GAME_MIN_M)
    high = min(data_max, GAME_MAX_M)

    if high - low < MIN_WINDOW_M:
        # Gelaende liegt (fast) ganz ausserhalb der Grenzen: am naechsten Rand
        if data_max < GAME_MIN_M + MIN_WINDOW_M:
            return GAME_MIN_M, GAME_MIN_M + MIN_WINDOW_M
        if data_min > GAME_MAX_M - MIN_WINDOW_M:
            return GAME_MAX_M - MIN_WINDOW_M, GAME_MAX_M
        return low, low + MIN_WINDOW_M

    span = high - low

    if mode == MODE_SQUEEZE or width is None:
        return low, high

    width = min(max(float(width), MIN_WINDOW_M), span)

    if mode == MODE_CAP:
        return low, low + width

    return high - width, high


def window_slider_range(width: float) -> tuple[float, float]:
    """
    Bereich, in dem die Untergrenze eines Fensters der Breite width liegen darf
    (Eintragswerte): ueber den ganzen Bereich des Editors, vom tiefsten erlaubten
    Wert bis so, dass die Obergrenze noch bei GAME_MAX_M endet. So laesst sich das
    Fenster auch bei einem Gelaende verschieben, das schon ganz hineinpasst:
    nach oben werden die Tiefen abgeschnitten, nach unten die Gipfel gekappt.
    Bei einem Fenster ueber die ganze Editor-Spanne gibt es nichts zu schieben.
    """

    return GAME_MIN_M, max(GAME_MIN_M, GAME_MAX_M - width)


def limit_warning(entered_min: float, entered_max: float) -> str | None:
    """Hinweis, wenn die Eintragswerte ausserhalb der Editor-Grenzen liegen."""

    if entered_min >= GAME_MIN_M - 0.5 and entered_max <= GAME_MAX_M + 0.5:
        return None

    return (
        f"Achtung: Der Karteneditor nimmt nur Höhen von {GAME_MIN_M:.0f} bis "
        f"{GAME_MAX_M:.0f} m. Dein Bereich ({entered_min:.0f} bis {entered_max:.0f} m) "
        "liegt außerhalb. „Höhenfenster begrenzen“ anhaken oder „Höhen stauchen“ "
        "verwenden."
    )


def _percent(fraction: float) -> str:

    percent = fraction * 100.0

    if 0.0 < percent < 0.1:
        return "<0,1"

    return f"{percent:.1f}".replace(".", ",")


def describe_report(report: ClipReport) -> str:
    """Eine Zeile fuer den Dialog, zum Beispiel "4,2 % der Fläche werden planiert"."""

    if report.mode == MODE_SQUEEZE:

        if report.scale_up >= 0.9995 and report.scale_down >= 0.9995:
            return "Nichts wird gestaucht: Das Gelände passt schon ins Fenster."

        return (
            f"Gestaucht: Höhen über dem Bezugspunkt auf {report.scale_up * 100:.0f} %, "
            f"darunter auf {report.scale_down * 100:.0f} % "
            f"({_percent(report.changed_fraction)} % der Fläche verändert)."
        )

    if report.changed_fraction <= 0.0:
        return (
            "Nichts wird planiert: Das Gelände liegt ganz im Fenster. Mit dem "
            "Schieberegler oder engeren Feldern lässt sich das ändern."
        )

    return (
        f"{_percent(report.changed_fraction)} % der Fläche werden planiert "
        f"(oben gekappt: {_percent(report.lowered_fraction)} %, "
        f"unten abgeschnitten: {_percent(report.raised_fraction)} %)."
    )
