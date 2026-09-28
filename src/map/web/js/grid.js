/**
 * Maß-Overlay: zeichnet ein Gitter mit echten Meterabständen über die
 * Karte und zeigt die Koordinaten unter dem Mauszeiger an.
 *
 * Die reine Rechenlogik (Schrittweite wählen, Distanzen formatieren) ist
 * bewusst in eigenständige, reine Funktionen ausgelagert (kein Leaflet
 * nötig) - diese sind einzeln testbar, z.B. mit `node --check` und einem
 * kleinen Testskript ohne Browser. Nur der Zeichenteil selbst braucht
 * echtes Leaflet und wurde daher NICHT in einer echten Karte getestet -
 * das kann nur ein Test im Studio selbst zeigen.
 */

/* ==========================================================================
 * Reine Rechenlogik (ohne Leaflet, einzeln testbar)
 * ======================================================================== */

const GRID_MATH = {

    EARTH_CIRCUMFERENCE_M: 40075016.686,

    /**
     * Meter pro Bildschirmpixel bei gegebenem Zoomlevel und Breitengrad
     * (Standard-Web-Mercator-Auflösung, wie sie OSM/Leaflet intern
     * verwendet: 256px Kachelbreite bei Zoom 0).
     */
    metersPerPixel(zoom, latitudeDeg) {

        const latRad = latitudeDeg * Math.PI / 180;

        return (
            this.EARTH_CIRCUMFERENCE_M * Math.cos(latRad)
        ) / (256 * Math.pow(2, zoom));

    },

    /**
     * Wählt eine "runde" Schrittweite in Metern (1/2/5 × 10^n), sodass
     * der Gitterabstand auf dem Bildschirm möglichst nah an
     * targetPixelSpacing liegt, ohne ihn zu unterschreiten.
     */
    chooseStepMeters(metersPerPixel, targetPixelSpacing = 100) {

        const targetMeters = metersPerPixel * targetPixelSpacing;

        const magnitude = Math.pow(
            10,
            Math.floor(Math.log10(targetMeters))
        );

        const candidates = [1, 2, 5, 10].map(f => f * magnitude);

        for (const candidate of candidates) {
            if (candidate >= targetMeters) {
                return candidate;
            }
        }

        return candidates[candidates.length - 1];

    },

    /**
     * Formatiert eine Distanz in Metern für ein Gitter-Label - ganze
     * Kilometer ab 1000 m, sonst Meter.
     */
    formatDistance(meters) {

        if (meters >= 1000) {

            const km = meters / 1000;

            return (
                Number.isInteger(km)
                    ? `${km} km`
                    : `${km.toFixed(1)} km`
            );

        }

        return `${Math.round(meters)} m`;

    }

};

/* ==========================================================================
 * Darstellung (Leaflet) - ungetestet, siehe Hinweis oben
 * ======================================================================== */

class MeasurementGrid {

    #engine;
    #group;
    #visible = false;
    #targetPixelSpacing;

    constructor(engine, targetPixelSpacing = 100) {

        this.#engine = engine;
        this.#targetPixelSpacing = targetPixelSpacing;
        this.#group = L.layerGroup();

    }

    get leaflet() {
        return this.#group;
    }

    get visible() {
        return this.#visible;
    }

    show(map) {

        this.#visible = true;

        if (!map.hasLayer(this.#group)) {
            this.#group.addTo(map);
        }

        this.redraw();

    }

    hide(map) {

        this.#visible = false;

        if (map.hasLayer(this.#group)) {
            map.removeLayer(this.#group);
        }

    }

    setVisible(map, visible) {

        if (visible) {
            this.show(map);
        } else {
            this.hide(map);
        }

    }

    /**
     * Zeichnet das Gitter für den aktuell sichtbaren Kartenausschnitt neu.
     * Wird von außen bei moveend/zoomend aufgerufen (siehe Einbindung in
     * map.js), damit das Gitter beim Verschieben/Zoomen mitwandert.
     */
    redraw() {

        if (!this.#visible) {
            return;
        }

        this.#group.clearLayers();

        const map = this.#engine.leaflet;
        const bounds = map.getBounds();
        const center = map.getCenter();
        const zoom = map.getZoom();

        const metersPerPixel = GRID_MATH.metersPerPixel(
            zoom,
            center.lat
        );

        const stepM = GRID_MATH.chooseStepMeters(
            metersPerPixel,
            this.#targetPixelSpacing
        );

        // Lokale Meter-Umrechnung um den Kartenmittelpunkt herum -
        // gleiche einfache äquirektangulare Näherung wie an anderen
        // Stellen im Studio (TPF2Geometry, rectLocalToLatLon), für den
        // sichtbaren Kartenausschnitt (wenige Kilometer) ausreichend
        // genau.
        const cos0 = Math.cos(center.lat * Math.PI / 180);
        const R = 6371008.8;

        const toLatLon = (eastM, northM) => {

            const lat = center.lat + (northM / R) * 180 / Math.PI;
            const lon = center.lng + (eastM / (R * cos0)) * 180 / Math.PI;

            return [lat, lon];

        };

        const toLocalMeters = (lat, lon) => {

            const east = (lon - center.lng) * Math.PI / 180 * R * cos0;
            const north = (lat - center.lat) * Math.PI / 180 * R;

            return [east, north];

        };

        const [swE, swN] = toLocalMeters(bounds.getSouth(), bounds.getWest());
        const [neE, neN] = toLocalMeters(bounds.getNorth(), bounds.getEast());

        // Etwas Rand dazu, damit beim Verschieben nicht sofort eine
        // Lücke am Kartenrand sichtbar wird.
        const pad = stepM * 2;

        const startE = Math.floor((swE - pad) / stepM) * stepM;
        const endE = Math.ceil((neE + pad) / stepM) * stepM;
        const startN = Math.floor((swN - pad) / stepM) * stepM;
        const endN = Math.ceil((neN + pad) / stepM) * stepM;

        const style = {
            color: "#ff00ff",
            weight: 2,
            opacity: 0.85,
            interactive: false
        };

        const labelStyle = {
            color: "#000000",
            fillColor: "#ffffff",
            fillOpacity: 0.85,
            weight: 0,
            radius: 0,
            interactive: false
        };

        // Senkrechte Linien (konstantes Ost, über die Nord-Spanne)
        for (let e = startE; e <= endE; e += stepM) {

            const p1 = toLatLon(e, startN);
            const p2 = toLatLon(e, endN);

            L.polyline([p1, p2], style).addTo(this.#group);

        }

        // Waagrechte Linien (konstantes Nord, über die Ost-Spanne)
        for (let n = startN; n <= endN; n += stepM) {

            const p1 = toLatLon(startE, n);
            const p2 = toLatLon(endE, n);

            L.polyline([p1, p2], style).addTo(this.#group);

        }

        // Ein Maßstabs-Label an der unteren linken Ecke des sichtbaren
        // Bereichs, mit der aktuellen Schrittweite - Ablesehilfe, ohne
        // die Karte mit vielen einzelnen Beschriftungen vollzustellen.
        const labelAnchor = toLatLon(
            Math.max(startE, swE + stepM * 0.5),
            Math.max(startN, swN + stepM * 0.5)
        );

        L.marker(labelAnchor, {
            icon: L.divIcon({
                className: "grid-scale-label",
                html: GRID_MATH.formatDistance(stepM),
                iconSize: null
            }),
            interactive: false
        }).addTo(this.#group);

    }

}

/* ==========================================================================
 * Koordinatenanzeige unter dem Mauszeiger
 * ======================================================================== */

class CoordinateReadout {

    #element;

    constructor(elementId) {

        this.#element = document.getElementById(elementId);

    }

    update(lat, lon) {

        if (!this.#element) {
            return;
        }

        this.#element.textContent =
            `${lat.toFixed(6)}, ${lon.toFixed(6)}`;

    }

    clear() {

        if (!this.#element) {
            return;
        }

        this.#element.textContent = "";

    }

}
