"""
Mod-Checker fuer den OSM-TPF2-Importer.

Prueft, ob die auf https://github.com/Vacuum-Tube/OSM-TPF2-Importer/blob/main/doc/Mods.md
dokumentierten Mods installiert sind - sowohl ueber den Steam-Workshop-Ordner
(numerische Ordner-IDs) als auch ueber den lokalen mod-Ordner (Ordnername
bzw. der in mod.lua hinterlegte Anzeigename).

WICHTIG zur Genauigkeit: Ob ein Mod "installiert" ist, laesst sich zuverlaessig
pruefen (Ordner vorhanden). Ob er in einem konkreten Spielstand tatsaechlich
AKTIV ist, steht nicht in einer lesbaren Konfigurationsdatei, sondern im
(binaeren, komprimierten) Savegame selbst - das prueft dieses Modul bewusst
NICHT, um keine falsche Sicherheit vorzutaeuschen.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Datenmodell
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RequiredMod:
    name: str
    category: str
    # Steam-Workshop-ID (Ordnername unter .../workshop/content/1066780/):
    workshop_id: str | None = None
    # Bekannter/dokumentierter lokaler Ordnername (aus mod.lua-Namen
    # abgeleitet, siehe Mods.md):
    local_names: tuple[str, ...] = ()
    url: str = ""
    note: str = ""
    # Kategorie, die per Checkbox ausgeschaltet werden kann, weil der
    # Nutzer die zugehoerige Importer-Funktion nicht verwendet
    # (z.B. build_bridges=false):
    toggle: str | None = None


@dataclass
class ModCheckResult:
    mod: RequiredMod
    # "found_workshop", "found_local", "missing", "manual", "skipped"
    status: str
    found_path: Path | None = None
    found_display_name: str | None = None


@dataclass
class ModCheckReport:
    results: list[ModCheckResult] = field(default_factory=list)
    crash_mods_found: list[tuple[str, Path]] = field(default_factory=list)
    importer_duplicate: bool = False
    importer_locations: list[Path] = field(default_factory=list)
    workshop_path_ok: bool = True
    local_path_ok: bool = True


# ---------------------------------------------------------------------------
# Offizielle Mod-Anforderungen (Stand: Mods.md, Vacuum-Tube/OSM-TPF2-Importer)
# ---------------------------------------------------------------------------

REQUIRED_MODS: tuple[RequiredMod, ...] = (

    # --- Gleistypen -----------------------------------------------------
    RequiredMod("Natural Environment Professional 2", "Gleistypen",
                note="Nur ueber transportfever.net erhaeltlich, kein fester Ordnername bekannt."),
    RequiredMod("NEP Addon", "Gleistypen",
                note="GitHub-Mod, kein Workshop-Eintrag."),
    RequiredMod("Gleispaket mit 750mm 1000mm", "Gleistypen"),
    RequiredMod("Feldbahn Infrastruktur", "Gleistypen"),
    RequiredMod("Vienna Fever: Infrastructure", "Gleistypen", workshop_id="2060012969"),
    RequiredMod("Berlin Stadtbahn Viaduct Construction - Basic Segments", "Gleistypen",
                workshop_id="2258619623", toggle="elektrifizierte_gleise",
                note="Nur noetig, falls das Gebiet elektrifizierte Bahnstrecken enthaelt."),
    RequiredMod("Old Track", "Gleistypen", workshop_id="1983390040"),
    RequiredMod("Ballast", "Gleistypen", workshop_id="2072274420"),

    # --- Straßentypen -----------------------------------------------------
    RequiredMod("ext.roads footpaths standalone", "Straßentypen", workshop_id="1968514713"),
    RequiredMod("Street fine tuning", "Straßentypen", workshop_id="2021038808"),
    RequiredMod("Freestyle train station", "Straßentypen", workshop_id="2363493916",
                note="Wird auch fuer Bruecken-Typen verwendet."),
    RequiredMod("Marc's Street and Trampack", "Straßentypen", workshop_id="1933747406"),
    RequiredMod("Airport Roads (EXPERIMENTAL)", "Straßentypen", workshop_id="2232249704"),
    RequiredMod("Roads´n Trams Projekt (RTP)", "Straßentypen"),
    RequiredMod("SMP 2.0", "Straßentypen", workshop_id="1943578742"),
    RequiredMod("Joe Fried Straßenpaket: Straßengeschichte", "Straßentypen",
                local_names=("joefried_roadstrassen_em_2",)),
    RequiredMod("Autobahnkreuz TpF2", "Straßentypen"),
    RequiredMod("Water Textures - Natural Water Surfaces", "Straßentypen",
                workshop_id="2014569888",
                note="Water 4 (4.2/4.3/4.4) und Street 4 mit blauem Wasser aktivieren."),

    # --- Brückentypen -----------------------------------------------------
    RequiredMod("TFMR2.0 Bridge (Transport Fever Modular Road)", "Brückentypen",
                workshop_id="2187434173", toggle="bruecken"),
    RequiredMod("Bridge Type-1", "Brückentypen", workshop_id="1939805466", toggle="bruecken"),
    RequiredMod("Vienna Fever: Bridge and Retaining Wall", "Brückentypen",
                workshop_id="2060132685", toggle="bruecken"),
    RequiredMod("Gitterträger-Fachwerkbrücke", "Brückentypen", toggle="bruecken",
                note="Nur bis Importer-Version 1.3 benoetigt."),
    RequiredMod("Autobahnkreuz TpF2 (Brücke)", "Brückentypen", toggle="bruecken"),

    # --- Signale ------------------------------------------------------
    RequiredMod("H/V-Signale Einheitsbauform²", "Signale", toggle="signale",
                local_names=("sebbe_hv69signale_basis_1", "sebbe_hv69signale_erw1_1"),
                note="Basis + Erweiterungen 1-3 vom selben Autor (sebbe_hv69signale_*)."),
    RequiredMod("Signalkomponenten", "Signale", workshop_id="2770909719", toggle="signale"),
    RequiredMod("Ks-Signalsystem", "Signale", workshop_id="2920749928", toggle="signale"),
    RequiredMod("Level crossing signals", "Signale", workshop_id="2770910636", toggle="signale"),
    RequiredMod("Signal Distance", "Signale", workshop_id="2294246900", toggle="signale",
                note="Wird fuer die Signalplatzierung vorausgesetzt."),

    # --- Objekte --------------------------------------------------------
    RequiredMod("Connum's German Traffic Assets", "Objekte", workshop_id="1963592311",
                toggle="objekte"),
    RequiredMod("Litfaßsäulen", "Objekte", local_names=("sabon_litfass_era_c_1",),
                toggle="objekte"),
    RequiredMod("Hide Street Trees", "Objekte", toggle="objekte",
                note="Empfohlen, kein Pflicht-Mod."),

    # --- Forester / Baummodelle ------------------------------------------
    RequiredMod("Forester", "Forester / Bäume", toggle="wald_import",
                local_names=("vt_snowball_forester_1.4_Interface",),
                note="Zwingend genau diese Version (Interface-Variante) verwenden."),
    RequiredMod("Spacky_Trees conifers", "Forester / Bäume", workshop_id="2247194383",
                toggle="wald_import"),

    # --- Paver / Bodentexturen --------------------------------------------
    RequiredMod("Paver", "Paver / Bodentexturen", toggle="paver"),
    RequiredMod("Ingo's textures - pavement", "Paver / Bodentexturen",
                workshop_id="2763516913", toggle="paver"),
    RequiredMod("Ingo's Vegetation Extended", "Paver / Bodentexturen",
                workshop_id="3432184100", toggle="paver"),
    RequiredMod("Bodentexturen 1.0", "Paver / Bodentexturen", toggle="paver"),
    RequiredMod("Bodentexturen 4.0", "Paver / Bodentexturen", toggle="paver"),

)

# Nur informativ, nie als "fehlt" gewertet - Empfehlungen der Doku, die
# VOR dem OSM-Import aktiviert werden sollten:
RECOMMENDED_BEFORE_IMPORT: tuple[RequiredMod, ...] = (
    RequiredMod("Realistic Railway Slopes", "Empfohlen vor dem Import",
                workshop_id="2161175689",
                note="Embankment Slope: 1, Embankment Slope High: off."),
    RequiredMod("Maximum Street Slopes", "Empfohlen vor dem Import",
                workshop_id="2206802861",
                note="Embankment Slope: 1, Embankment Slope High: off."),
    RequiredMod("Realistic Track Curve Speeds", "Empfohlen vor dem Import",
                workshop_id="2558586098",
                note="'No superelevation at speed restricted tracks' deaktivieren."),
    RequiredMod("Sidewalk Lowerer", "Empfohlen vor dem Import",
                note="'Adjust Small Streets town new' deaktivieren."),
)

# Bekannte, vom Nutzer als problematisch identifizierte Mods - werden
# unabhaengig von der obigen Liste gesucht und als Warnung gemeldet, falls
# gefunden (Ordner- oder Anzeigename-Teilstring, gross-/kleinschreibungs-
# unabhaengig):
KNOWN_CRASH_MODS: tuple[tuple[str, str], ...] = (
    ("snowball_fences", "Bekannter Absturzverursacher (nicht Teil der Importer-Anforderungen)."),
)


# ---------------------------------------------------------------------------
# Ordner-Scan
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(
    r'name\s*=\s*_?\(?\s*"([^"]+)"',
)


def _parse_mod_display_name(mod_folder: Path) -> str | None:
    """
    Liest, falls vorhanden, den Anzeigenamen aus mod.lua.

    Rein textbasiert (Regex), OHNE Lua auszufuehren - Mod-Code ist nicht
    vertrauenswuerdig. Liefert None, wenn nichts gefunden wird.
    """

    mod_lua = mod_folder / "mod.lua"

    if not mod_lua.is_file():
        return None

    try:
        text = mod_lua.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None

    match = _NAME_RE.search(text)

    return match.group(1) if match else None


def scan_local_mod_folder(local_path: Path) -> dict[str, dict]:
    """
    Liest alle Unterordner von local_path (dem TPF2-'mod'-Ordner) ein.

    Rueckgabe: {ordner_name: {"path": Path, "display_name": str|None}}
    """

    result: dict[str, dict] = {}

    if not local_path.is_dir():
        return result

    for entry in local_path.iterdir():

        if not entry.is_dir():
            continue

        result[entry.name] = {
            "path": entry,
            "display_name": _parse_mod_display_name(entry),
        }

    return result


def scan_workshop_folder(workshop_path: Path) -> dict[str, Path]:
    """
    Liest alle Unterordner von workshop_path ein (numerische Workshop-IDs).

    Rueckgabe: {workshop_id: Path}
    """

    result: dict[str, Path] = {}

    if not workshop_path.is_dir():
        return result

    for entry in workshop_path.iterdir():

        if entry.is_dir():
            result[entry.name] = entry

    return result


# ---------------------------------------------------------------------------
# Hauptpruefung
# ---------------------------------------------------------------------------

def _local_match(
    mod: RequiredMod,
    local_mods: dict[str, dict],
) -> tuple[Path, str] | None:
    """
    Sucht einen der bekannten lokalen Ordnernamen (lang: exakt oder als
    Praefix, da Versionsnummern oft angehaengt werden, z.B. '..._1.4').
    """

    for local_name in mod.local_names:

        for folder_name, info in local_mods.items():

            if folder_name == local_name or folder_name.startswith(local_name):
                return info["path"], (info["display_name"] or folder_name)

    return None


def run_check(
    workshop_path: Path,
    local_path: Path,
    importer_folder_name: str,
    enabled_toggles: set[str],
) -> ModCheckReport:
    """
    Fuehrt die vollstaendige Pruefung durch.

    enabled_toggles: Menge der Toggle-Namen (siehe RequiredMod.toggle), fuer
    die die jeweilige Importer-Funktion tatsaechlich genutzt wird. Mods mit
    einem Toggle, der NICHT in enabled_toggles enthalten ist, werden als
    "skipped" markiert statt als "missing".
    """

    report = ModCheckReport()

    report.workshop_path_ok = workshop_path.is_dir()
    report.local_path_ok = local_path.is_dir()

    workshop_mods = scan_workshop_folder(workshop_path)
    local_mods = scan_local_mod_folder(local_path)

    for mod in REQUIRED_MODS + RECOMMENDED_BEFORE_IMPORT:

        if mod.toggle is not None and mod.toggle not in enabled_toggles:

            report.results.append(
                ModCheckResult(mod=mod, status="skipped")
            )

            continue

        if mod.workshop_id and mod.workshop_id in workshop_mods:

            report.results.append(
                ModCheckResult(
                    mod=mod,
                    status="found_workshop",
                    found_path=workshop_mods[mod.workshop_id],
                )
            )

            continue

        local_hit = _local_match(mod, local_mods) if mod.local_names else None

        if local_hit is not None:

            path, display_name = local_hit

            report.results.append(
                ModCheckResult(
                    mod=mod,
                    status="found_local",
                    found_path=path,
                    found_display_name=display_name,
                )
            )

            continue

        if not mod.workshop_id and not mod.local_names:

            # Kein bekannter Ordnername/ID -> automatisch nicht pruefbar.
            report.results.append(
                ModCheckResult(mod=mod, status="manual")
            )

            continue

        report.results.append(
            ModCheckResult(mod=mod, status="missing")
        )

    # -----------------------------------------------------------------
    # Bekannte Absturz-Mods
    # -----------------------------------------------------------------

    for folder_name, info in local_mods.items():

        haystack = f"{folder_name} {info['display_name'] or ''}".lower()

        for pattern, reason in KNOWN_CRASH_MODS:

            if pattern.lower() in haystack:
                report.crash_mods_found.append((f"{pattern} ({reason})", info["path"]))

    # -----------------------------------------------------------------
    # Doppelt aktiver OSM-Importer (Workshop + lokal)
    # -----------------------------------------------------------------

    locations: list[Path] = []

    if importer_folder_name:

        for folder_name, info in local_mods.items():

            if (
                folder_name == importer_folder_name
                or importer_folder_name.lower() in folder_name.lower()
            ):
                locations.append(info["path"])

    needle = importer_folder_name.lower() if importer_folder_name else ""

    for folder_name, path in workshop_mods.items():

        display = _parse_mod_display_name(path) or ""

        haystack = f"{folder_name} {display}".lower()

        if needle and needle in haystack:
            locations.append(path)
        elif "osm" in haystack and "importer" in haystack:
            locations.append(path)

    report.importer_locations = locations
    report.importer_duplicate = len(locations) > 1

    return report
