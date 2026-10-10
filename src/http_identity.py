"""Gemeinsame Kennung fuer alle ausgehenden HTTP-Anfragen.

Overpass (OSM), swisstopo und hoehendaten.de erwarten einen
erkennbaren User-Agent mit Programmname, Version und Projekt-URL.
Bewusst keine E-Mail-Adresse.
"""

APP_NAME = "TPF3-Map-Studio"
APP_VERSION = "0.3.0"
APP_URL = "https://github.com/sharpi13822/TPF3-Map-Studio"

USER_AGENT = f"{APP_NAME}/{APP_VERSION} (+{APP_URL})"
