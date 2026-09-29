class MapEngine {

    #map;
    #config;
    #events;

    // Grundkarten, zwischen denen gewechselt werden kann (immer genau
    // eine aktiv). "satellite" nutzt EOX Sentinel-2 cloudless per WMS -
    // nicht-kommerziell nutzbar, siehe Quellenangabe in der Layer selbst.
    static BASE_LAYERS = {
        osm: {
            type: "xyz",
            url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            attribution: "© OpenStreetMap-Mitwirkende"
        },
        satellite: {
            // Esri World Imagery - laut OSM-Wiki von Esri ausdruecklich
            // ohne Einschraenkungen freigegeben (auch ohne Attributions-
            // pflicht). Deutlich hoehere Aufloesung als Sentinel-2 in
            // vielen Gebieten (bis 30cm in Teilen Westeuropas statt
            // Sentinel-2s festen 10m/Pixel), daher beim Heranzoomen
            // laenger scharf. Sehr weit verbreitetes, gut dokumentiertes
            // URL-Muster.
            type: "xyz",
            url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            maxNativeZoom: 19,
            attribution: "Tiles © Esri — Source: Esri, Maxar, Earthstar " +
                "Geographics, CNES/Airbus DS, USDA FSA, USGS, Aerogrid, " +
                "IGN, IGP und die GIS User Community"
        }
    };

    #baseLayer = null;
    #baseLayerName = null;

    constructor(config = {}) {

        const defaults = {
            target: "map",
            center: [51.1657, 10.4515],
            zoom: 6,
            minZoom: 2,
            maxZoom: 19,
            preferCanvas: true,
            baseLayer: "osm"
        };

        this.#config = Object.freeze({
            ...defaults,
            ...config
        });

        this.#events = new EventTarget();

        this.#map = L.map(this.#config.target, {
            zoomControl: true,
            preferCanvas: this.#config.preferCanvas,
            // Linien lassen sich 6 Pixel neben der Linie anklicken. Ohne
            // diese Toleranz muessen duenne Strassen auf den Pixel genau
            // getroffen werden, und Flaechen (Wald, Wiese) darueber
            // gewinnen den Klick.
            renderer: this.#config.preferCanvas
                ? L.canvas({ tolerance: 6 })
                : undefined,
            minZoom: this.#config.minZoom,
            maxZoom: this.#config.maxZoom
        });

        this.#map.setView(
            this.#config.center,
            this.#config.zoom
        );

        this.setBaseLayer(this.#config.baseLayer);

        window.addEventListener(
            "resize",
            () => this.invalidate()
        );

        this.#installEvents();
    }

    /**
     * Wechselt die Grundkarte (z.B. "osm" <-> "satellite"). Entfernt die
     * vorherige Grundkarte vollstaendig, bevor die neue hinzugefuegt
     * wird - es ist immer nur eine aktiv.
     */
    setBaseLayer(name) {

        const def = MapEngine.BASE_LAYERS[name];

        if (!def) {
            console.warn(`Unbekannte Grundkarte '${name}'`);
            return;
        }

        if (this.#baseLayer) {
            this.#map.removeLayer(this.#baseLayer);
        }

        this.#baseLayer = def.type === "wms"
            ? L.tileLayer.wms(def.url, {
                ...def.wmsOptions,
                attribution: def.attribution,
                maxZoom: this.#config.maxZoom,
                // maxNativeZoom: ab hier gibt es beim Anbieter keine
                // eigenen Kacheln mehr - Leaflet vergroessert dann die
                // letzte verfuegbare Kachel, statt (leere/graue)
                // Kacheln fuer nicht existierende Zoomstufen anzufragen.
                maxNativeZoom: def.maxNativeZoom
            })
            : L.tileLayer(def.url, {
                attribution: def.attribution,
                maxZoom: this.#config.maxZoom,
                maxNativeZoom: def.maxNativeZoom
            });

        this.#baseLayer.addTo(this.#map);
        this.#baseLayerName = name;

    }

    get baseLayerName() {
        return this.#baseLayerName;
    }

    #installEvents() {

        this.#map.whenReady(() => {
            this.invalidate();
            this.emit("ready");
        });

        this.#map.on("moveend", () => {
            this.emit("move", {
                center: this.center,
                zoom: this.zoom
            });
        });

        this.#map.on("zoomend", () => {
            this.emit("zoom", {
                zoom: this.zoom
            });
        });

        this.#map.on("mousemove", event => {

            this.emit("mousemove", {
                lat: event.latlng.lat,
                lon: event.latlng.lng
            });

        });

        this.#map.on("click", event => {

            if (event.originalEvent._stopped) {
                return;

            }    

            this.emit("click", {
                lat: event.latlng.lat,
                lon: event.latlng.lng
            });
        });

    }

    get leaflet() {
        return this.#map;
    }

    get center() {
        return this.#map.getCenter();
    }

    get zoom() {
        return this.#map.getZoom();
    }

    panTo(lat, lon) {
        this.#map.panTo([lat, lon]);
    }

    setZoom(level) {
        this.#map.setZoom(level);
    }

    setView(lat, lon, zoom = this.zoom) {
        this.#map.setView([lat, lon], zoom);
    }

    fitBounds(bounds, options = {}) {
        this.#map.fitBounds(bounds, options);
    }

    invalidate() {
        this.#map.invalidateSize();
    }

    on(type, callback) {
        this.#events.addEventListener(type, callback);
    }

    off(type, callback) {
        this.#events.removeEventListener(type, callback);
    }

    once(type, callback) {

        const wrapper = event => {
            this.off(type, wrapper);
            callback(event);
        };

        this.on(type, wrapper);

    }

    emit(type, detail = {}) {

        this.#events.dispatchEvent(
            new CustomEvent(type, {
                detail
            })
        );

    }

}

class Layer {

    #name;
    #group;
    #objects;
    #options;

    constructor(map, name, options = {}) {

        this.#name = name;

        this.#options = Object.freeze({
            visible: true,
            polygon: false,
            ...options
        });

        this.#group = L.layerGroup();
        this.#objects = new Map();

        if (this.#options.visible) {
            this.show(map);
        }

    }

    get name() {
        return this.#name;
    }

    get leaflet() {
        return this.#group;
    }

    get polygon() {
        return this.#options.polygon;
    }

    get visible() {
        return this.#options.visible;
    }

    get size() {
        return this.#objects.size;
    }

    has(id) {
        return this.#objects.has(id);
    }

    get(id) {
        return this.#objects.get(id) ?? null;
    }

    add(id, object) {

        if (!id || !object) {
            return null;
        }

        this.remove(id);

        object.addTo(this.#group);
        this.#objects.set(id, object);

        return object;

    }

    remove(id) {

        const object = this.#objects.get(id);

        if (!object) {
            return false;
        }

        object.remove();
        this.#objects.delete(id);

        return true;

    }

    clear() {

        for (const object of this.#objects.values()) {
            object.remove();
        }

        this.#objects.clear();

    }

    forEach(callback) {
        this.#objects.forEach(callback);
    }

    show(map) {

        if (!map.hasLayer(this.#group)) {
            this.#group.addTo(map);
        }

    }

    hide(map) {

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
}

/**
 * Wrapper fuer eine zuschaltbare Raster-Kartenebene (z.B. OpenRailwayMap
 * als Overlay ueber der Grundkarte) - bietet dieselbe show()/hide()/
 * setVisible()-Schnittstelle wie Layer, damit LayerManager.toggle() und
 * die bestehenden Checkboxen in layer_control.js sie ohne Aenderung
 * mitbenutzen koennen.
 */
class RasterLayer {

    #tileLayer;
    #options;

    constructor(url, options = {}) {

        this.#options = Object.freeze({
            visible: false,
            ...options
        });

        this.#tileLayer = L.tileLayer(url, options);

    }

    get leaflet() {
        return this.#tileLayer;
    }

    get visible() {
        return this.#options.visible;
    }

    show(map) {

        if (!map.hasLayer(this.#tileLayer)) {
            this.#tileLayer.addTo(map);
        }

    }

    hide(map) {

        if (map.hasLayer(this.#tileLayer)) {
            map.removeLayer(this.#tileLayer);
        }

    }

    setVisible(map, visible) {

        if (visible) {
            this.show(map);
        } else {
            this.hide(map);
        }

    }

}

class GeometryRenderer {

    create(/* geometry, style */) {
        throw new Error(
            `${this.constructor.name} must implement create()`
        );
    }

}

class PolylineRenderer extends GeometryRenderer {

    create(points, style = {}) {

        const line = 
            L.polyline(
                points,
                style
            );

        return line;

    }

}

class PolygonRenderer extends GeometryRenderer {

    create(points, style = {}) {

        return L.polygon(
            points,
            style
        );

    }

}

class RectangleRenderer extends GeometryRenderer {

    create(bounds, style = {}) {

        return L.rectangle(
            bounds,
            style
        );

    }

}

class CircleRenderer extends GeometryRenderer {

    create(data, style = {}) {

        if (!data || !data.center) {
            throw new Error("CircleRenderer: missing center");
        }

        return L.circle(
            data.center,
            {
                radius: data.radius ?? 1,
                ...style
            }
        );

    }

}

class RendererRegistry {

    #renderers;

    constructor() {
        this.#renderers = new Map();
    }

    register(type, renderer) {

        if (!(renderer instanceof GeometryRenderer)) {
            throw new Error(
                `Renderer '${type}' must extend GeometryRenderer`
            );
        }

        this.#renderers.set(type, renderer);

        return this;

    }

    unregister(type) {
        return this.#renderers.delete(type);
    }

    has(type) {
        return this.#renderers.has(type);
    }

    get(type) {

        const renderer = this.#renderers.get(type);

        if (!renderer) {
            throw new Error(
                `Unknown renderer '${type}'`
            );
        }

        return renderer;

    }

    clear() {
        this.#renderers.clear();
    }

    keys() {
        return [...this.#renderers.keys()];
    }

    values() {
        return [...this.#renderers.values()];
    }

    forEach(callback) {
        this.#renderers.forEach(callback);
    }

}

/**
 * Kleine Einblendung unten links (5 Sekunden). Zeigt Rueckmeldungen und
 * Fehler an, auch wenn keine Entwicklerkonsole zu sehen ist.
 */
let toastTimer = null;

function showToast(text, isError = false) {

    let element = document.getElementById("tpf-toast");

    if (!element) {

        element = document.createElement("div");

        element.id = "tpf-toast";

        element.style.cssText =
            "position:fixed;left:12px;bottom:12px;z-index:100000;" +
            "max-width:70%;padding:6px 10px;border-radius:4px;" +
            "font:12px sans-serif;color:#fff;pointer-events:none;";

        document.body.appendChild(element);

    }

    element.style.background = isError ? "#b71c1c" : "#333333";

    element.textContent = text;

    element.style.display = "block";

    clearTimeout(toastTimer);

    toastTimer = setTimeout(() => {
        element.style.display = "none";
    }, 5000);

}

class GeometryManager {

    #layers;
    #renderers;
    #selectedObject;

    constructor(layerManager, rendererRegistry) {

        this.#layers = layerManager;
        this.#renderers = rendererRegistry;

    }

    createMetadata(id, layer, type, geometry, style, properties) {

        return {

           id,
           layer,
           type,
           geometry,
           style,
           properties

        };

    }

    saveOriginalStyle(object) {

        object.originalStyle = {

            color: object.options.color,
            weight: object.options.weight,
            opacity: object.options.opacity,
            fillColor: object.options.fillColor,
            fillOpacity: object.options.fillOpacity

        };

    }

    attachMetadata(object, metadata) {

        object.tpf2 = metadata;

    }

    getLayer(name) {

        const layer = this.#layers.get(name); 

        if (!layer) {
           throw new Error(`Unknown layer '${name}'`);
        }
        
        return layer;

    }

    createObject(type, geometry, style) {

        const renderer = this.#renderers.get(type);

        return renderer.create(
            geometry,
            style
        );

    }

    addObject(layer, id, object) {

        layer.add(
            id,
            object
        );

        return object;

    }

    bindObjectEvents(object) {

        object.on?.(
            "click",
            (event) => {

                try {

                    L.DomEvent.stopPropagation(event);

                    this.highlight(object);

                    window.infoPanel.show(
                        object.tpf2
                    );

                    if (window.geometryEditor) {

                        window.geometryEditor.start(
                            object
                        );

                    }

                    const meta = object.tpf2 || {};

                    const handles = window.geometryEditor
                        ? window.geometryEditor.vertexHandles.length
                        : 0;

                    showToast(
                        `Ausgewählt: ${meta.layer} ${meta.id} ` +
                        `(${meta.type}), Eckpunkte: ${handles}`
                    );

                } catch (error) {

                    console.error("Objekt-Auswahl:", error);

                    showToast(
                        "Fehler bei der Auswahl: " + error.message,
                        true
                    );

                }

            }
        );
        
}

    draw({
    layer,
    id,
    type,
    geometry,
    style = {},
    properties = {}

}) {

    const target = this.getLayer(layer);

    const object = this.createObject(
        type,
        geometry,
        style
    );

    const metadata = this.createMetadata(
        id,
        layer,
        type,
        geometry,
        style,
        properties
    );

    this.saveOriginalStyle(object);

    this.attachMetadata(
        object,
        metadata
    );

    this.bindObjectEvents(object);
   
    return this.addObject(
        target,
        id,
        object

    );

}

restoreOriginalStyle(object) {

    if (!object) {
        return;
    }

    object.setStyle(
        object.originalStyle
    );

    applyObjectOpacity(
        object,
        layerOpacity[object.tpf2?.layer] ?? 1
    );

}    

highlight(object) {

    console.log("HIGHLIGHT OBJECT:", object);
    console.log("SETSTYLE?", typeof object.setStyle);

    // altes Objekt zurücksetzen

    if (
        this.#selectedObject &&
        this.#selectedObject !== object
    ) {

        this.restoreOriginalStyle(
            this.#selectedObject
        );

    }



    // Editierstil übernimmt der GeometryEditor
    // Daher hier nichts mehr setzen.


    console.log(
        "GEHIGHLIGHTET:",
        object.options

    );

    this.#selectedObject = object;


}

clearHighlight() {

    if (!this.#selectedObject) {
        return;
    }


    this.restoreOriginalStyle(
        this.#selectedObject
);

    this.#selectedObject = null;

}

updateProperties(object, properties) {

    const metadata =
        object?.tpf2 || object;

    if (
        !metadata ||
        !metadata.properties
    ) {

        console.warn(
            "Objekt oder Metadaten nicht gefunden"
        );

        return false;

    }

    metadata.properties = {
        ...metadata.properties,
        ...properties
    };

    console.log(
        "PROPERTIES UPDATED:",
        metadata
    );

    console.log(
        "BRIDGE DEBUG:",
        typeof bridges,
        bridges?.adapter,
        typeof bridges?.adapter?.polylinePropertiesChanged
    );

    if (
        metadata.layer === "roads" &&
        typeof bridges !== "undefined" &&
        bridges.adapter &&
        typeof bridges.adapter.polylinePropertiesChanged === "function"
    ) {

        bridges.adapter.polylinePropertiesChanged(
            metadata.id,
            metadata.properties
        );

    } else {

        console.warn(
            "Polyline-Bridge für Eigenschaften nicht verfügbar"
        );
    
    }

    return true;

}
  
    update(options) {
        return this.draw(options);
    }

    remove(layer, id) {

        const target = this.#layers.get(layer);

        if (!target) {
            return false;
        }

        return target.remove(id);

    }

    clear(layer) {

        const target = this.#layers.get(layer);

        if (!target) {
            return false;
        }

        target.clear();

        return true;

    }

    has(layer, id) {

        const target = this.#layers.get(layer);

        return target
            ? target.has(id)
            : false;

    }

    get(layer, id) {

        const target = this.#layers.get(layer);

        return target
            ? target.get(id)
            : null;

    }

    forEachObject(callback) {

        for (const layer of this.#layers.values()) {

            layer.leaflet.eachLayer(object => {

                if (object.tpf2) {
                    callback(object);
                }

            });

        }

    }

    getObjects() {


        const objects = [];


        this.forEachObject(object => {

            objects.push(object.tpf2);

        });

    return objects;


}

    getLeafletObjects() {
        
        const objects = [];

        this.forEachObject(object => {

            objects.push(object);

        });

        return objects;

    } 

} 


class BatchRenderer {

    #geometry;

    constructor(geometryManager) {

        this.#geometry = geometryManager;

    }

    drawBatch(layer, objects = []) {

        this.clear(layer);

        return this.addBatch(
            layer,
            objects
        );

    }

    addBatch(layer, objects = []) {

        let count = 0;

        for (const object of objects) {

            this.#geometry.draw({

                layer,
                id: object.id,
                type: object.type,
                geometry: object.geometry,
                style: object.style ?? {}

            });

            count++;

        }

        return count;

    }

    updateBatch(layer, objects = []) {

        return this.addBatch(
            layer,
            objects
        );

    }

    clear(layer) {

        this.#geometry.clear(layer);

    }

    clearAll() {

        this.clear("roads");
        this.clear("railways");
        this.clear("buildings");
        this.clear("water");
        this.clear("waterways");
        this.clear("parks");
        this.clear("landuse");
        this.clear("vegetation");

    }

    drawAll(batch = {}) {

        for (const [layer, objects] of Object.entries(batch)) {

            this.drawBatch(
                layer,
                objects
            );

        }

    }

    addAll(batch = {}) {

        for (const [layer, objects] of Object.entries(batch)) {

            this.addBatch(
                layer,
                objects
            );

        }

    }

    updateAll(batch = {}) {

        return this.addAll(batch);

    }

}

class Marker {

    #id;
    #marker;

    constructor(id, leafletMarker) {

        this.#id = id;
        this.#marker = leafletMarker;

    }

    get id() {
        return this.#id;
    }

    get leaflet() {
        return this.#marker;
    }

    get position() {
        return this.#marker.getLatLng();
    }

    move(lat, lon) {

        this.#marker.setLatLng([
            lat,
            lon
        ]);

        return this;

    }

    popup(text = "") {

        if (text !== "") {
            this.#marker.bindPopup(text);
        }

        return this;

    }

    tooltip(text = "") {

        if (text !== "") {
            this.#marker.bindTooltip(text);
        }

        return this;

    }

    click(callback) {

    this.#marker.on(
        "click",
        () => {

            callback(this);

        }
    );

    return this;

}

    icon(icon) {

        if (icon) {
            this.#marker.setIcon(icon);
        }

        return this;

    }

    select(icon) {
        return this.icon(icon);
    }

    remove() {
        this.#marker.remove();
    }

}
class MarkerFactory {

    #icon;

    constructor(defaultIcon) {
        this.#icon = defaultIcon;
    }

    create(id, lat, lon) {

        const marker = L.marker(
            [lat, lon],
            {
                icon: this.#icon,
                draggable: true
            }
        );

        return new Marker(
            id,
            marker
        );

    }

}
class SelectionController {

    #selected = null;

    #defaultIcon;
    #selectedIcon;

    constructor(defaultIcon, selectedIcon) {

        this.#defaultIcon = defaultIcon;
        this.#selectedIcon = selectedIcon;

    }

    get current() {
        return this.#selected;
    }

    hasSelection() {
        return this.#selected !== null;
    }

    clear() {

        if (!this.#selected) {
            return;
        }

        this.#selected.icon(this.#defaultIcon);
        this.#selected = null;

    }

    select(marker) {

        if (this.#selected === marker) {
            return marker;
        }

        this.clear();

        if (!marker) {
            return null;
        }

        marker.icon(this.#selectedIcon);

        this.#selected = marker;

        return marker;

    }

    isSelected(marker) {
        return this.#selected === marker;
    }

}

class MarkerManager {

    #layer;
    #factory;
    #selection;
    #markers;
    #eventTarget;

    constructor(layer, factory, selection, eventTarget = null) {

        this.#layer = layer;
        this.#factory = factory;
        this.#selection = selection;
        this.#eventTarget = eventTarget;

        this.#markers = new Map();

    }

    add(id, lat, lon, text = "") {

        let marker = this.#markers.get(id);

        if (!marker) {

            marker = this.#factory.create(
                id,
                lat,
                lon
            );

            marker.leaflet.on(
                "click",
                () => {

                    this.select(id);

                    if (this.#eventTarget) {

                        this.#eventTarget.emit(
                            "marker.click",
                            { id }
                        );

                    }

                }
            );

            marker.leaflet.on(
                "dragend",
                () => {

                const pos = marker.position;
                
                this.#eventTarget.emit(
                    "marker.move",
                {
                    id: id,
                    lat: pos.lat,
                    lon: pos.lng
                }
            );
        }
    );

            marker.leaflet.addTo(
                this.#layer
            );

            this.#markers.set(
                id,
                marker
            );

        }

        marker
            .move(lat, lon)
            .popup(text);

        return marker;

    }

    update(id, lat, lon, text = "") {

        return this.add(
            id,
            lat,
            lon,
            text
        );

    }

    has(id) {
        return this.#markers.has(id);
    }

    get(id) {
        return this.#markers.get(id) ?? null;
    }

    remove(id) {

        const marker = this.#markers.get(id);

        if (!marker) {
            return false;
        }

        if (this.#selection.current === marker) {
            this.#selection.clear();
        }

        marker.remove();

        this.#markers.delete(id);

        return true;

    }

    clear() {

        this.#selection.clear();

        for (const marker of this.#markers.values()) {
            marker.remove();
        }

        this.#markers.clear();

    }

    select(id) {

        return this.#selection.select(
            this.#markers.get(id) ?? null
        );

    }

    forEach(callback) {
        this.#markers.forEach(callback);
    }

    statistics() {

        return {
            markers: this.#markers.size,
            selected: this.#selection.hasSelection()
        };

    }

}

class PolylineManager {

    #layer;
    #polylines;

    constructor(layer) {

        this.#layer = layer;
        this.#polylines = new Map();
    }

    add(id, points, text = "") {

        let polyline = this.#polylines.get(id);

        if (polyline) {
            polyline.remove();
        }

        polyline = L.polyline(points);

        if (text) {
            polyline.bindPopup(text);
        }

        polyline.addTo(this.#layer);

        this.#polylines.set(
            id,
            polyline
        );

        return polyline;
    }

    remove(id) {

        const polyline =
            this.#polylines.get(id);

        if (!polyline) {
            return false;
        }

        polyline.remove();

        this.#polylines.delete(id);

        return true;
    }

    clear() {

        for (const polyline of this.#polylines.values()) {
            polyline.remove();
        }

        this.#polylines.clear();
    }
}

class BridgeAdapter {

    connect() {}
    disconnect() {}

    mapClicked(lat, lon) {}
    addPolyline(id, points, text) {}
    markerClicked(id) {}
    selectionChanged(ids) {}
    markerMoved(id, lat, lon) {}
    polylineMoved(id, points) {}
    rectangleChanged(centerLat, centerLon, widthM, heightM, rotationDeg) {}

    send(name, ...args) {}

}

class QtBridge extends BridgeAdapter {

    #bridge = null;

    connect(channel) {

        this.#bridge = channel?.objects?.bridge ?? null;

        console.info("QtBridge connected");

    }

    disconnect() {
        this.#bridge = null;
    }

    get connected() {
        return this.#bridge !== null;
    }

    mapClicked(lat, lon) {
        this.#bridge?.mapClicked?.(lat, lon);
    }

    addPolyline(id, points, text) {
        this.#bridge?.addPolyline?.(
            id,
            points,
            text
        );
    }

    markerClicked(id) {
        this.#bridge?.markerClicked?.(id);
    }

    markerMoved(id, lat, lon) {
        this.#bridge?.markerMoved?.(id, lat, lon);
    }

    polylineMoved(id, points) {
        this.#bridge?.polylineMoved?.(id, points);
    }

    // Rechteck-Tool: Mittelpunkt/Groesse/Drehung nach Verschieben oder
    // Drehen per Maus an Python melden (Bridge.rectangleChanged ->
    // MapController.rectangle_changed). Fehlte bisher - dadurch blieb
    // die Drehung in Python immer bei 0 Grad.
    rectangleChanged(centerLat, centerLon, widthM, heightM, rotationDeg) {
        this.#bridge?.rectangleChanged?.(
            centerLat,
            centerLon,
            widthM,
            heightM,
            rotationDeg
        );
    }

    polylinePropertiesChanged(
        id,
        properties
    ) {

        this.#bridge?.polylinePropertiesChanged?.(
            id,
            properties
        );

    }

    selectionChanged(ids) {
        this.#bridge?.selectionChanged?.(ids);
    } 

    send(name, ...args) {

        if (!this.connected) {
            return false;
        }

        const fn = this.#bridge[name];

        if (typeof fn !== "function") {
            return false;
        }

        fn.apply(this.#bridge, args);

        return true;

    }

}

class NullBridge extends BridgeAdapter {}

class BridgeManager {

    #adapter;

    constructor(adapter = new NullBridge()) {
        this.#adapter = adapter;
    }

    get adapter() {
        return this.#adapter;
    }

    setAdapter(adapter) {
        this.#adapter = adapter;
    }

}

class CommandDispatcher {

    #commands = new Map();

    register(name, callback) {

        this.#commands.set(name, callback);

        return this;

    }

    has(name) {
        return this.#commands.has(name);
    }

    unregister(name) {
        return this.#commands.delete(name);
    }

    execute(name, ...args) {

        const command = this.#commands.get(name);

        if (!command) {
            throw new Error(
                `Unknown command '${name}'`
            );
        }

        return command(...args);

    }

    clear() {
        this.#commands.clear();
    }

    keys() {
        return [...this.#commands.keys()];
    }

}

        window.engine = new MapEngine();

        window.layerManager = new LayerManager(window.engine);

        window.layerManager.register("markers");

        const layers = window.layerManager;

        layers.register("polylines");

        window.layerControl =
            new LayerControl(
                window.layerManager
        );

        window.infoPanel =
            new InfoPanel();

        layers.register("roads");
        layers.register("railways");
        layers.register("buildings");
        layers.register("water");
        layers.register("waterways");
        layers.register("parks");
        layers.register("landuse");
        layers.register("vegetation");

        layers.register("selection");
        layers.register("measure");


        // ---------------------------------------------------------
        // OpenRailwayMap-Overlay (Eisenbahn-Infrastruktur) - nicht-
        // kommerzielle Nutzung mit wenigen Anfragen laut Nutzungs-
        // bedingungen, https://wiki.openstreetmap.org/wiki/OpenRailwayMap/API
        // ---------------------------------------------------------

        const ormLayer = new RasterLayer(
            "https://{s}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png",
            {
                subdomains: "abc",
                maxZoom: 19,
                opacity: 0.8,
                attribution:
                    "Daten © OpenStreetMap-Mitwirkende, Stil: CC-BY-SA 2.0 " +
                    "OpenRailwayMap"
            }
        );

        layers.registerExternal("openrailwaymap", ormLayer);

        // ---------------------------------------------------------
        // Maß-Gitter
        // ---------------------------------------------------------

        const measurementGrid = new MeasurementGrid(engine);

        layers.registerExternal("measurement-grid", measurementGrid);

        window.measurementGrid = measurementGrid;

        engine.on("move", () => measurementGrid.redraw());
        engine.on("zoom", () => measurementGrid.redraw());

        // ---------------------------------------------------------
        // Koordinatenanzeige unter dem Mauszeiger
        // ---------------------------------------------------------

        const coordinateReadout = new CoordinateReadout(
            "coordinate-readout"
        );

        engine.on("mousemove", event => {

            const { lat, lon } = event.detail;

            coordinateReadout.update(lat, lon);

        });

        // ---------------------------------------------------------
        // Grundkarten-Auswahl (OSM <-> Satellit)
        // ---------------------------------------------------------

        document
            .querySelectorAll('input[name="base-layer"]')
            .forEach(input => {

                input.addEventListener("change", () => {

                    if (input.checked) {
                        engine.setBaseLayer(input.value);
                    }

                });

            });

        const renderers = new RendererRegistry();

        renderers
        .register("polyline", new PolylineRenderer())
        .register("polygon", new PolygonRenderer())
        .register("multipolygon", new PolygonRenderer())
        .register("rectangle", new RectangleRenderer())
        .register("circle", new CircleRenderer());

        const geometry = new GeometryManager(
            layers,
            renderers
        );

        window.geometryManager = geometry;


        const topologyManager =
            new TopologyManager(
                geometry
            );

        window.topologyManager =
            topologyManager;

        const geometryEditor =
            new GeometryEditor(
                topologyManager 
            );
            
        window.geometryEditor =
            geometryEditor;

        const polylineLayer =
            layers.get("polylines").leaflet;

        const drawManager = new DrawManager(
            geometry,
            polylineLayer
        );

        window.drawManager = drawManager;

        document
        .getElementById("draw-road")
        .onclick = () => {

        drawManager.start(
            "road"
        );

    };



document
    .getElementById("draw-river")
    .onclick = () => {

        drawManager.start(
            "river"
        );

    };



document
    .getElementById("draw-building")
    .onclick = () => {

        drawManager.start(
            "building"
        );

    };



document
    .getElementById("draw-finish")
    .onclick = () => {

        drawManager.finish();

    };

        const exporter = new ExportManager();


        window.exporter = exporter;

        const importer =
            new ImportManager(
                geometry
            );


        window.importer = importer;

        document
            .getElementById("export-json")
            .onclick = () => {


                const data =
                    geometry.getObjects();


                exporter.export(
                    data
                );


            };

        document
             .getElementById("import-json")
             .onclick = () => {


        document
            .getElementById("json-file")
            .click();


        };

        document
            .getElementById("json-file")
            .onchange = (event) => {


                const file =
                    event.target.files[0];


                if (file) {


                importer.importFile(
                file
            );


        }


    };

        const loader = new MapLoader(
            new TPF2Reader(),
            new MapParser(),
            geometry
        );

        
        // Testdaten (Muenchen) nur zum Entwickeln laden. Im Normalbetrieb
        // aus, sonst erscheinen sie in den Ebenen und ueberlagern die
        // eigenen OSM-Daten.
        const LOAD_TEST_DATA = false;

        if (LOAD_TEST_DATA) {

            loader.load(
                "test-tpf2-raw.json"
            )
            .then(objects => {

                console.log(
                    "Loaded objects:",
                    objects
                );

                console.log(topologyManager);
                topologyManager.buildVertexIndex();
                topologyManager.showSharedVertices();

            });

        }

const batch = new BatchRenderer(
    geometry
);

const defaultIcon = L.icon({
    iconUrl: "icons/marker-default.png",
    iconSize: [25,41],
    iconAnchor: [12,41],
    popupAnchor: [1,-34]
});

const selectedIcon = L.icon({
    iconUrl: "icons/marker-selected.png?v=4",
    iconSize: [25,41],
    iconAnchor: [12,41],
    popupAnchor: [1,-34]
});

const markerFactory =
    new MarkerFactory(defaultIcon);

const selection =
    new SelectionController(
        defaultIcon,
        selectedIcon
    );

const markerLayer =
    layers.get("markers").leaflet;
    
    
const polylines =
    new PolylineManager(
        polylineLayer
    );

const markers =
    new MarkerManager(
        markerLayer,
        markerFactory,
        selection,
        engine
    );

/* ============================================================================
 * Rechteck-Tool: gedrehtes Kartenband, verschieb- und drehbar
 * ========================================================================== */

const RECT_R_EARTH = 6371008.8;

function rectLocalToLatLon(centerLat, centerLon, rotationDeg, x, y) {

    const theta = rotationDeg * Math.PI / 180;

    const up = [Math.sin(theta), Math.cos(theta)];
    const right = [Math.sin(theta + Math.PI / 2), Math.cos(theta + Math.PI / 2)];

    const cos0 = Math.cos(centerLat * Math.PI / 180);

    const e = right[0] * x + up[0] * y;
    const n = right[1] * x + up[1] * y;

    const lat = centerLat + (n / RECT_R_EARTH) * 180 / Math.PI;
    const lon = centerLon + (e / (RECT_R_EARTH * cos0)) * 180 / Math.PI;

    return [lat, lon];

}

function rectLatLonToEastNorth(centerLat, centerLon, lat, lon) {

    // Ost-/Nordversatz in Metern (unrotiert) - wird nur fuer den
    // Drehwinkel-Handle gebraucht, um aus seiner Position den Winkel
    // zum Mittelpunkt zu berechnen.

    const cos0 = Math.cos(centerLat * Math.PI / 180);

    const e = (lon - centerLon) * Math.PI / 180 * RECT_R_EARTH * cos0;
    const n = (lat - centerLat) * Math.PI / 180 * RECT_R_EARTH;

    return [e, n];

}

function computeRectCorners(centerLat, centerLon, widthM, heightM, rotationDeg) {

    const hx = widthM / 2;
    const hy = heightM / 2;

    return [
        rectLocalToLatLon(centerLat, centerLon, rotationDeg, -hx, hy),
        rectLocalToLatLon(centerLat, centerLon, rotationDeg, hx, hy),
        rectLocalToLatLon(centerLat, centerLon, rotationDeg, hx, -hy),
        rectLocalToLatLon(centerLat, centerLon, rotationDeg, -hx, -hy)
    ];

}

const rectState = {
    centerLat: null,
    centerLon: null,
    widthM: null,
    heightM: null,
    rotationDeg: null,
    polygon: null,
    moveHandle: null,
    rotateHandle: null
};

function rectHandleIcon(color) {

    return L.divIcon({
        className: "",
        html: `
            <div style="
                width: 16px;
                height: 16px;
                background: ${color};
                border: 3px solid #ffffff;
                border-radius: 50%;
                box-sizing: border-box;
                box-shadow: 0 0 0 2px #333333;
            "></div>
        `,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    });

}

function rectRotateHandlePosition() {

    // Griff sitzt ein Stueck ueber der oberen Kante, damit er nicht mit
    // dem Verschiebe-Griff in der Mitte kollidiert. Fester Mindestabstand,
    // damit er auch bei kleinen Kartenbaendern noch gut greifbar ist.

    const offset = Math.max(300, rectState.heightM * 0.06);

    return rectLocalToLatLon(
        rectState.centerLat,
        rectState.centerLon,
        rectState.rotationDeg,
        0,
        rectState.heightM / 2 + offset
    );

}

function redrawRect() {

    const corners = computeRectCorners(
        rectState.centerLat,
        rectState.centerLon,
        rectState.widthM,
        rectState.heightM,
        rectState.rotationDeg
    );

    if (rectState.polygon) {
        rectState.polygon.setLatLngs(corners);
    }

    if (rectState.rotateHandle) {
        rectState.rotateHandle.setLatLng(
            rectRotateHandlePosition()
        );
    }

}

function notifyRectChanged() {

    // Nur die Python-Seite (Selection/Projekt) aktualisieren - die
    // sichtbare Karte hat sich waehrend des Ziehens bereits live
    // veraendert, ein Neuzeichnen von Python aus ist hier nicht noetig
    // (gleiches Prinzip wie bei markerMoved).

    if (
        typeof bridges !== "undefined" &&
        bridges.adapter &&
        typeof bridges.adapter.rectangleChanged === "function"
    ) {

        bridges.adapter.rectangleChanged(
            rectState.centerLat,
            rectState.centerLon,
            rectState.widthM,
            rectState.heightM,
            rectState.rotationDeg
        );

    } else {

        console.warn("rectangleChanged nicht verfügbar");

    }

}

function removeRectHandles() {

    if (rectState.moveHandle) {
        engine.leaflet.removeLayer(rectState.moveHandle);
        rectState.moveHandle = null;
    }

    if (rectState.rotateHandle) {
        engine.leaflet.removeLayer(rectState.rotateHandle);
        rectState.rotateHandle = null;
    }

    rectState.polygon = null;

}

/* ============================================================================
 * Erzwungenes Neuzeichnen nach Batch-Operationen
 * ========================================================================== */

// Nach addBatch()/updateBatch()/removeObjects() erschienen die Objekte in
// der QtWebEngine-Ansicht teils erst, nachdem man im Layer-Dock Haken
// aus- und wieder eingeschaltet hat (das loest ein Neuzeichnen des
// Canvas-Renderers aus). Eine kurze 1-px-Verschiebung der Karte mit
// sofortigem Zurueck stoesst dasselbe an, ohne dass sich die Ansicht
// dauerhaft aendert. Entprellt, damit mehrere Layer-Batches direkt
// hintereinander nur ein Neuzeichnen ausloesen.

let forceRedrawTimer = null;

/* ============================================================================
 * Ebenen: Deckkraft und Reihenfolge (Layer-Dock in der Oberflaeche)
 * ========================================================================== */

// Deckkraft je Ebene als Faktor 0..1 (1 = wie gezeichnet).
const layerOpacity = {};

// Ebenennamen von oben nach unten, wie im Layer-Dock.
let layerOrderNames = [];

let layerOrderTimer = null;

function applyObjectOpacity(object, factor) {

    const base = object.originalStyle;

    if (!base || typeof object.setStyle !== "function") {
        return;
    }

    object.setStyle({
        opacity: (base.opacity ?? 1) * factor,
        fillOpacity: (base.fillOpacity ?? 0.2) * factor
    });

}

function applyLayerOpacity(name) {

    const factor = layerOpacity[name] ?? 1;

    const layer = layers.get(name);

    if (!layer) {
        return;
    }

    layer.forEach(object => applyObjectOpacity(object, factor));

}

function applyLayerOrder() {

    // Von unten nach oben: die zuletzt behandelte Ebene liegt oben.
    for (let i = layerOrderNames.length - 1; i >= 0; i--) {

        const layer = layers.get(layerOrderNames[i]);

        if (!layer) {
            continue;
        }

        layer.forEach(object => object.bringToFront?.());

    }

}

// Entprellt: mehrere Aenderungen kurz hintereinander ordnen nur einmal.
function scheduleLayerOrder() {

    if (!layerOrderNames.length || layerOrderTimer !== null) {
        return;
    }

    layerOrderTimer = setTimeout(() => {

        layerOrderTimer = null;

        applyLayerOrder();

    }, 30);

}

function forceMapRedraw() {

    if (forceRedrawTimer !== null) {
        return;
    }

    forceRedrawTimer = setTimeout(() => {

        forceRedrawTimer = null;

        const map = engine.leaflet;

        map.invalidateSize();

        map.panBy([1, 0], { animate: false });
        map.panBy([-1, 0], { animate: false });

    }, 50);

}

const bridges = new BridgeManager();

if (typeof qt !== "undefined") {

    new QWebChannel(
        qt.webChannelTransport,
        channel => {

            const bridge =
                new QtBridge();

            bridge.connect(channel);

            bridges.setAdapter(
                bridge
            );

        }
    );

}

const dispatcher =
    new CommandDispatcher();

/* ============================================================================
 * Bridge Events
 * ========================================================================== */

engine.on("click", event => {

    const { lat, lon } = event.detail;

    if (drawManager.mode) {


        drawManager.addPoint(
            lat,
            lon
        );


        return;

    } 

    
    // Ein Objekt wird gerade bearbeitet (Eckpunkte sichtbar): ein Klick
    // ins Leere waehlt es nur ab. Es wird dabei kein Marker gesetzt.
    if (
        window.geometryEditor &&
        window.geometryEditor.isEditing()
    ) {

        window.geometryEditor.stop();

        geometry.clearHighlight();

        window.infoPanel.show(null);

        return;

    }

    geometry.clearHighlight();

    window.infoPanel.show(null);

    bridges.adapter.mapClicked(lat, lon);

});

engine.on("dblclick", event => {

    if (drawManager.mode) {

        drawManager.finish();

        return;
    }

});

engine.on("marker.click", event => {

    const { id } = event.detail;

    bridges.adapter.markerClicked(id);

});

engine.on("marker.move", event => {

    const { id, lat, lon } = event.detail;

    bridges.adapter.markerMoved(
        id,
        lat,
        lon
    );

});

/* ============================================================================
 * Public API
 * ========================================================================== */

window.MapApi = {

     ready: true,

    /* ------------------------------------------------------------------------
     * Map
     * ----------------------------------------------------------------------*/

    center(lat, lon) {

        engine.panTo(lat, lon);

    },

    zoom(level) {

        engine.setZoom(level);

    },

    centerAndZoom(lat, lon, zoom) {

        engine.setView(lat, lon, zoom);

    },

    /* ------------------------------------------------------------------------
     * Marker
     * ----------------------------------------------------------------------*/

    addMarker(id, lat, lon, text = "") {

        markers.add(id, lat, lon, text);

    },

    updateMarker(id, lat, lon, text = "") {

        markers.update(id, lat, lon, text);

    },

    removeMarker(id) {

        markers.remove(id);

    },

    clearMarkers() {

        markers.clear();

    },

    addPolyline(id, points, text = "") {

        return geometry.draw({
            layer: "polylines",
            id: id,
            type: "polyline",
            geometry: points,
            style: {},
            properties: {
                text: text
            }
        });
    },

    updatePolylineProperties(id, properties) {

        const layers = [
        "roads",
        "waterways",
        "railways"
    ];

    let object = null;

    for (const layer of layers) {

        object = geometry.get(
            layer,
            id
        );

        if (object) {
            break;
        }

    }

    if (!object || !object.tpf2) {

        console.warn(
            "Objekt oder Metadaten nicht gefunden:",
            id
        );

        return false;

    }

    object.tpf2.properties = {
        ...object.tpf2.properties,
        ...properties
    };

    console.log(
        "POLYLINE PROPERTIES UPDATED:",
        object.tpf2
    );

    if (
        typeof bridges !== "undefined" &&
        bridges.adapter &&
        typeof bridges.adapter.polylinePropertiesChanged === "function"
    ) {

        bridges.adapter.polylinePropertiesChanged(
            id,
            object.tpf2.properties
        );

        console.log(
           "PROPERTIES AN PYTHON GESENDET:",
           id
        );
        
    } else {

        console.warn(
           "polylinePropertiesChanged nicht verfügbar"
        );
        
    }

    return true;

},

    removePolyline(id) {

        return geometry.remove(
            "roads",
            id
        );
    },

    clearPolylines() {

        return geometry.clear(
            "roads"
        );    
    },

    selectMarker(id) {

        return markers.select(id);

    },

    /* ------------------------------------------------------------------------
     * Selection
     * ----------------------------------------------------------------------*/

    drawRectangle(minLat, minLon, maxLat, maxLon) {

        geometry.draw({

            layer: "selection",

            id: "__selection__",

            type: "rectangle",

            geometry: [
                 
                    [minLat, minLon],
                    [maxLat, maxLon]
                ],

            style: {
                color: "#3388ff",
                weight: 1,
                fillOpacity: 0.15,
                interactive: false
            }

        });

    },

    clearRectangle() {

        geometry.clear("selection");
        removeRectHandles();

    },

    /* ------------------------------------------------------------------------
     * Koordinaten-Messwerkzeug
     * ----------------------------------------------------------------------*/

    drawMeasureLine(lat1, lon1, lat2, lon2, text = "") {

        // Alte Messung entfernen, bevor die neue gezeichnet wird - es soll
        // immer nur eine aktive Messstrecke sichtbar sein (analog zu
        // clearRectangle() vor enableRectangleEditing()).
        geometry.clear("measure");

        const line = geometry.draw({

            layer: "measure",

            id: "__measure__",

            type: "polyline",

            geometry: [
                [lat1, lon1],
                [lat2, lon2]
            ],

            style: {
                color: "#ff8800",
                weight: 3,
                dashArray: "6 6"
            }

        });

        if (text && line && typeof line.bindPopup === "function") {
            line.bindPopup(text).openPopup();
        }

    },

    clearMeasureLine() {

        geometry.clear("measure");

    },

    enableRectangleEditing(centerLat, centerLon, widthM, heightM, rotationDeg) {

        // Gedrehtes Kartenband, verschieb- und drehbar per Maus.
        // Ersetzt eine vorher vorhandene Auswahl komplett.

        geometry.clear("selection");
        removeRectHandles();

        rectState.centerLat = centerLat;
        rectState.centerLon = centerLon;
        rectState.widthM = widthM;
        rectState.heightM = heightM;
        rectState.rotationDeg = rotationDeg;

        const corners = computeRectCorners(
            centerLat,
            centerLon,
            widthM,
            heightM,
            rotationDeg
        );

        rectState.polygon = geometry.draw({

            layer: "selection",

            id: "__selection__",

            type: "polygon",

            geometry: corners,

            style: {
                color: "#3388ff",
                weight: 1,
                fillOpacity: 0.15,
                interactive: false
            }

        });

        // ---------------------------------------------------------
        // Verschiebe-Griff (Mittelpunkt)
        // ---------------------------------------------------------

        rectState.moveHandle = L.marker(
            [centerLat, centerLon],
            {
                draggable: true,
                zIndexOffset: 1000,
                icon: rectHandleIcon("#3388ff")
            }
        ).addTo(engine.leaflet);

        rectState.moveHandle.on("drag", (event) => {

            const latlng = event.target.getLatLng();

            rectState.centerLat = latlng.lat;
            rectState.centerLon = latlng.lng;

            redrawRect();

        });

        rectState.moveHandle.on("dragend", () => {

            notifyRectChanged();

        });

        // ---------------------------------------------------------
        // Dreh-Griff (oberhalb der Bandmitte)
        // ---------------------------------------------------------

        rectState.rotateHandle = L.marker(
            rectRotateHandlePosition(),
            {
                draggable: true,
                zIndexOffset: 1000,
                icon: rectHandleIcon("#ff8800")
            }
        ).addTo(engine.leaflet);

        rectState.rotateHandle.on("drag", (event) => {

            const latlng = event.target.getLatLng();

            const [de, dn] = rectLatLonToEastNorth(
                rectState.centerLat,
                rectState.centerLon,
                latlng.lat,
                latlng.lng
            );

            rectState.rotationDeg =
                (Math.atan2(de, dn) * 180 / Math.PI + 360) % 360;

            redrawRect();

        });

        rectState.rotateHandle.on("dragend", () => {

            notifyRectChanged();

        });

    },

    drawRotatedRectangle(corners) {

        // corners: [[lat, lon], [lat, lon], [lat, lon], [lat, lon]]
        // Gedrehtes Kartenband - wie drawRectangle, aber als Polygon
        // statt als achsenparalleles Leaflet-Rechteck, da ein gedrehtes
        // Rechteck kein natives L.rectangle mehr ist.

        geometry.draw({

            layer: "selection",

            id: "__selection__",

            type: "polygon",

            geometry: corners,

            style: {
                color: "#3388ff",
                weight: 1,
                fillOpacity: 0.15,
                interactive: false
            }

        });

    },

    setLayerVisible(layerName, visible) {

        const layer = layers.get(layerName);

        if (!layer) {
            console.warn(
                "setLayerVisible: unbekannter Layer",
                layerName
            );
            return;
        }

        layer.setVisible(
            engine.leaflet,
            visible
        );

        // Erst jetzt sichtbar gewordene Objekte in die richtige
        // Reihenfolge bringen.
        scheduleLayerOrder();

    },

    setLayerOpacity(layerName, opacity) {

        layerOpacity[layerName] = Math.max(0, Math.min(1, opacity));

        applyLayerOpacity(layerName);

    },

    setLayerOrder(names = []) {

        layerOrderNames = names;

        scheduleLayerOrder();

    },

    clearRoads() {

        geometry.clear("roads");

    },

    clearRailways() {

        geometry.clear("railways");

    },

    clearBuildings() {

        geometry.clear("buildings");

    },

    clearWater() {

        geometry.clear("water");

    },

    clearWaterways() {

        geometry.clear("waterways");

    },

    clearParks() {

        geometry.clear("parks");

    },

    clearLanduse() {

        geometry.clear("landuse");

    },

    clearVegetation() {

        geometry.clear("vegetation");

    },

    /* ------------------------------------------------------------------------
     * Batch
     * ----------------------------------------------------------------------*/

    addBatch(layer, objects = []) {

        let count = 0;

        for (const object of objects) {

            geometry.draw({

                layer: layer,

                id: object.id,

                type: object.type,

                geometry: object.geometry,

                style: object.style || {}

            });

            count++;

        }

        applyLayerOpacity(layer);

        scheduleLayerOrder();

        forceMapRedraw();

        return count;

    },

    updateBatch(layer, objects = []) {

        let count = 0;

        for (const object of objects) {

            geometry.draw({

                layer: layer,

                id: object.id,

                type: object.type,

                geometry: object.geometry,

                style: object.style || {}

            });

            count++;

        }

        applyLayerOpacity(layer);

        scheduleLayerOrder();

        forceMapRedraw();

        return count;

    },

    removeObjects(layer, ids = []) {

        for (const id of ids) {

            geometry.remove(
                layer,
                id
            );

        }

        forceMapRedraw();

        return ids.length;

    }

}
