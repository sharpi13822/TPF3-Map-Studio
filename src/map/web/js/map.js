class MapEngine {

    #map;
    #config;
    #events;

    constructor(config = {}) {

        const defaults = {
            target: "map",
            center: [51.1657, 10.4515],
            zoom: 6,
            minZoom: 2,
            maxZoom: 19,
            preferCanvas: true,
            tileLayer: {
                url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                attribution: "© OpenStreetMap"
            }
        };

        this.#config = Object.freeze({
            ...defaults,
            ...config,
            tileLayer: {
                ...defaults.tileLayer,
                ...(config.tileLayer || {})
            }
        });

        this.#events = new EventTarget();

        this.#map = L.map(this.#config.target, {
            zoomControl: true,
            preferCanvas: this.#config.preferCanvas,
            minZoom: this.#config.minZoom,
            maxZoom: this.#config.maxZoom
        });

        this.#map.setView(
            this.#config.center,
            this.#config.zoom
        );

        L.tileLayer(
            this.#config.tileLayer.url,
            {
                attribution: this.#config.tileLayer.attribution,
                maxZoom: this.#config.maxZoom
            }
        ).addTo(this.#map);

        window.addEventListener(
            "resize",
            () => this.invalidate()
        );

        this.#installEvents();
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

class GeometryManager {

    #layers;
    #renderers;
    #selectedObject;

    constructor(layerManager, rendererRegistry) {

        this.#layers = layerManager;
        this.#renderers = rendererRegistry;

    }

    draw({
    layer,
    id,
    type,
    geometry,
    style = {},
    properties = {}

}) {

    const target = this.#layers.get(layer);

    if (!target) {
        throw new Error(`Unknown layer '${layer}'`);
    }


    const renderer = this.#renderers.get(type);


    const object = renderer.create(
        geometry,
        style
    );


    // echten Leaflet-Style merken
    object.originalStyle = {

        color: object.options.color,

        weight: object.options.weight,

        opacity: object.options.opacity,

        fillColor: object.options.fillColor,

        fillOpacity: object.options.fillOpacity

    };


    object.tpf2 = {

        id,
        layer,
        type,
        geometry,
        style,
        properties

    };


    object.on?.(
        "click",
        (event) => {

            L.DomEvent.stopPropagation(event);

            this.highlight(object);

            console.log(
                "Info Daten",
                object.tpf2
            );

            window.infoPanel.show(
                object.tpf2
            );

            if (window.geometryEditor) {
                window.geometryEditor.start(
                    object
                );
            }

        }
    );

    target.add(id, object);


    return object;

}

highlight(object) {

    console.log("HIGHLIGHT OBJECT:", object);
    console.log("SETSTYLE?", typeof object.setStyle);

    // altes Objekt zurücksetzen

    if (
        this.#selectedObject &&
        this.#selectedObject !== object
    ) {

        this.#selectedObject.setStyle(
            this.#selectedObject.originalStyle
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


    this.#selectedObject.setStyle({

        color: this.#selectedObject.originalStyle.color,

        weight: this.#selectedObject.originalStyle.weight,

        opacity: this.#selectedObject.originalStyle.opacity
        
    });


    this.#selectedObject = null;


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

    getObjects() {


    const objects = [];


    for (const layer of this.#layers.values()) {


        layer.leaflet.eachLayer(
            
            object => {


                if (object.tpf2) {


                    objects.push(
                        object.tpf2
                    );


                }


            }

        );


    }


    return objects;


}
    getLeafletObjects() {
        
        const objects = [];

        for (const layer of this.#layers.values()) {

            layer.leaflet.eachLayer(object => {

                 if (object.tpf2) {
                     objects.push(object);
                }

            });

        }

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
                icon: this.#icon
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

class BridgeAdapter {

    connect() {}
    disconnect() {}

    mapClicked(lat, lon) {}
    markerClicked(id) {}
    selectionChanged(ids) {}

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

    markerClicked(id) {
        this.#bridge?.markerClicked?.(id);
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

        const drawManager =new DrawManager(
            geometry
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

const markers =
    new MarkerManager(
        markerLayer,
        markerFactory,
        selection,
        engine
    );

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

    
    geometry.clearHighlight();

    window.infoPanel.show(null);

    bridges.adapter.mapClicked(lat, lon);

});

engine.on("marker.click", event => {

    const { id } = event.detail;

    bridges.adapter.markerClicked(id);

});

/* ============================================================================
 * Public API
 * ========================================================================== */

window.MapApi = {

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

            geometry: {
                bounds: [
                    [minLat, minLon],
                    [maxLat, maxLon]
                ]
            },

            style: {
                color: "#3388ff",
                weight: 1,
                fillOpacity: 0.15
            }

        });

    },

    clearRectangle() {

        geometry.clear("selection");

    },

    /* ------------------------------------------------------------------------
     * Roads
     * ----------------------------------------------------------------------*/

    drawRoad(id, coordinates, style = {}) {

        geometry.draw({

            layer: "roads",

            id,

            type: "polyline",

            geometry: coordinates,

            style

        });

    },

    clearRoads() {

        geometry.clear("roads");

    },

    /* ------------------------------------------------------------------------
     * Railways
     * ----------------------------------------------------------------------*/

    drawRailway(id, coordinates, style = {}) {

        geometry.draw({

            layer: "railways",

            id,

            type: "polyline",

            geometry: coordinates,

            style

        });

    },

    clearRailways() {

        geometry.clear("railways");

    },

    /* ------------------------------------------------------------------------
     * Buildings
     * ----------------------------------------------------------------------*/

    drawBuilding(id, coordinates, style = {}) {

        geometry.draw({

            layer: "buildings",

            id,

            type: "polygon",

            geometry: coordinates,

            style

        });

    },

    clearBuildings() {

        geometry.clear("buildings");

    },

    /* ------------------------------------------------------------------------
     * Water
     * ----------------------------------------------------------------------*/

    drawWater(id, coordinates, style = {}) {

        geometry.draw({

            layer: "water",

            id,

            type: "polygon",

            geometry: coordinates,

            style

        });

    },

    clearWater() {

        geometry.clear("water");

    },

    /* ------------------------------------------------------------------------
     * Waterways
     * ----------------------------------------------------------------------*/

    drawWaterway(id, coordinates, style = {}) {

        geometry.draw({

            layer: "waterways",

            id,

            type: "polyline",

            geometry: coordinates,

            style

        });

    },

    clearWaterways() {

        geometry.clear("waterways");

    },

    /* ------------------------------------------------------------------------
     * Parks
     * ----------------------------------------------------------------------*/

    drawPark(id, coordinates, style = {}) {

        geometry.draw({

            layer: "parks",

            id,

            type: "polygon",

            geometry: coordinates,

            style

        });

    },

    clearParks() {

        geometry.clear("parks");

    },

    /* ------------------------------------------------------------------------
     * Landuse
     * ----------------------------------------------------------------------*/

    drawLanduse(id, coordinates, style = {}) {

        geometry.draw({

            layer: "landuse",

            id,

            type: "polygon",

            geometry: coordinates,

            style

        });
    },

    clearLanduse() {

        geometry.clear("landuse");

    },

    /* ------------------------------------------------------------------------
     * Vegetation
     * ----------------------------------------------------------------------*/

    drawVegetation(id, coordinates, style = {}) {

        geometry.draw({

            layer: "vegetation",

            id,

            type: "polygon",

            geometry: coordinates,

            style

        });

    },

    clearVegetation() {

        geometry.clear("vegetation");

    },

    /* ------------------------------------------------------------------------
     * Batch
     * ----------------------------------------------------------------------*/

    drawBatch(layer, objects = []) {

        return batchRenderer.drawBatch(
            layer,
            objects
        );

    }

};

