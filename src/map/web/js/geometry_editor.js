/*
===========================================================
TPF2 MAP STUDIO
GeometryEditor V2.4
-----------------------------------------------------------
Author : ChatGPT + <dein Projekt>
Version: 2.4
Status : Stable

Änderungen gegenüber V2.1

✔ komplett neu strukturiert
✔ Edit Mode
✔ Style Handling
✔ Vorbereitung Segment Handles
✔ Vorbereitung Snapping
✔ Vorbereitung Undo/Redo
===========================================================
*/

console.log("GeometryEditor V9 TEST");

class GeometryEditor {

    constructor(topologyManager) {

        this.topology = topologyManager;

        // Layer für Editiermarker
        this.handleLayer = null;

        // Segment Handles
        this.segmentHandles = [];

        // Vertex Handles
        this.vertexHandles = [];

        // Originalstyle
        this.originalStyle = null;

        // Editierstyle
        this.editStyle = {

            color: "#2196F3",
            weight: 3,
            opacity: 1,

            fillColor: "#2196F3",
            fillOpacity: 0.20

        };

        // Aktiver Vertex
        this.object = null;

        this.undoStack = [];
        this.redoStack = [];

        //====================================================
        // Event Handler
        //====================================================

        this.keyDownHandler = this.onKeyDown.bind(this);

        this.snapDistance = 10;   // Pixel

        // Mindestabstand zwischen Eckpunkt-Griffen und Mindestlaenge
        // eines Segments fuer einen Mittelpunkt-Griff (jeweils Pixel).
        this.minHandleDistance = 14;
        this.minSegmentLength = 26;

        this.vertexHandleZIndex = 10000;

        this.segmentHandleZIndex = 9000;

        this.enableSnapping = true;

        this.activeSharedVertices = [];

        this.debug = false;

        // Merkt, ob ein Polygonring geschlossen ist (letzter Punkt = erster)
        this.closedRings = new WeakMap();

        // Fuer die Rueckmeldung in map.js (Einblendung nach dem Klick)
        this.lastEditable = true;
        this.lastStats = null;

    }

    //====================================================
    // START EDIT MODE
    //====================================================

    start(object) {


        if (!object)
            return;

        // Nur Linien und Polygone mit gueltigen Punkten sind editierbar.
        // Alles andere (z.B. Sonderformen aus OSM) wird nur ausgewaehlt,
        // ohne Eckpunkte - so gibt es keine kaputten Griffe.
        if (!this.isEditable(object)) {

            this.lastEditable = false;
            this.lastStats = null;

            this.stop();

            return;

        }

        this.lastEditable = true;

        this.stop();

        this.object = object;

        this.map = object._map;

        this.log("START", object);

        this.prepareHandleLayer();
        
        this.enableEditMode();

        this.refresh();

        console.log(
            "VERTEX HANDLES:",
            this.vertexHandles.length
        );

        console.log(
           "SEGMENT HANDLES:",
            this.segmentHandles.length
        ); 

        this.bindEvents();
 
        this.log(
            "GeometryEditor START",
            object
        );

    }

    //====================================================
    // STOP EDIT MODE
    //====================================================

    stop() {

        this.restoreStyle();

        this.clear();

        this.disableEditMode();
 
        this.unbindEvents();

        this.object = null;

        this.log(
            "GeometryEditor STOP"

        );

    }

    //====================================================
    // HANDLE LAYER
    //====================================================

    prepareHandleLayer() {

        if (!this.handleLayer) {

            this.handleLayer = L.layerGroup();
           
            this.handleLayer.addTo(
               this.map
            );

        } else {

            this.handleLayer.clearLayers();

        }
       
    }

    //====================================================
    // ENABLE EDIT MODE
    //====================================================

    enableEditMode() {

        this.saveStyle();

        this.setEditStyle();

        this.map.doubleClickZoom.disable();

        this.map
            .getContainer()
            .style.cursor = "crosshair";

    }

    //====================================================
    // DISABLE EDIT MODE
    //====================================================

    disableEditMode() {

        if (!this.map) {

            return;

        }

        this.map.doubleClickZoom.enable();

        this.map
            .getContainer()
            .style.cursor = "";

    }

    //====================================================
    // BIND EVENTS
    //====================================================

    bindEvents() {

        this.map.on(
            "click",
            this.onMapClick,
            this
        );

        this.map.on(
            "moveend",
            this.onZoom,
            this
        );

        document.addEventListener(
            "keydown",
            this.keyDownHandler
        );

    }

    //====================================================
    // UNBIND EVENTS
    //====================================================

    unbindEvents() {

        if (this.map) {

            this.map.off(
                "click",
                this.onMapClick,
                this
            );

            this.map.off(
                "moveend",
                this.onZoom,
                this
            );

        }

        document.removeEventListener(
            "keydown",
            this.keyDownHandler
        );

    }

    //====================================================
    // REMOVE ALL HANDLES
    //====================================================

    clear() {

        if (!this.handleLayer) return;

        this.handleLayer.clearLayers();

        this.vertexHandles = [];

        this.segmentHandles = [];

    }

    //====================================================
    // REFRESH EDITOR
    //====================================================

    refresh() {

        this.log("REFRESH");

        this.clear();

        if (!this.object) return;

        this.createHandles();

        this.log("CREATE HANDLES");

        this.createSegmentHandles();

        // Auswahl wiederherstellen

        if (this.activeVertex !== null) {

            this.selectVertex(this.activeVertex);
    
        }

    }
    

    //====================================================
    // POLYGON RING
    //====================================================

    // Liefert den aeusseren Ring eines Polygons. Unterstuetzt beide
    // Formate: [[lat, lon], ...] und [[[lat, lon], ...], ...].

    polygonRing(geometry) {

        // Loest [[ring]], [[[ring]]] usw. bis zu einem Ring aus
        // [lat, lon]-Paaren auf (der erste, aeussere Ring).
        let ring = geometry;

        for (let depth = 0; depth < 6; depth++) {

            if (!Array.isArray(ring) || ring.length === 0) {
                return null;
            }

            if (
                Array.isArray(ring[0]) &&
                typeof ring[0][0] === "number"
            ) {
                return ring;
            }

            ring = ring[0];

        }

        return null;

    }

    //====================================================
    // CLOSED RING
    //====================================================

    // Geschlossener Polygonring: letzter Punkt ist eine Kopie des ersten
    // (typisch fuer OSM). Beim Verschieben muessen beide zusammenbleiben.

    isClosedRing(points, object = this.object) {

        if (object?.tpf2?.type !== "polygon") {
            return false;
        }

        if (!this.closedRings.has(points)) {

            const first = points[0];
            const last = points[points.length - 1];

            this.closedRings.set(
                points,
                points.length > 3 &&
                Math.abs(first[0] - last[0]) < 1e-9 &&
                Math.abs(first[1] - last[1]) < 1e-9
            );

        }

        return this.closedRings.get(points);

    }

    //====================================================
    // IS EDITABLE
    //====================================================

    isEditable(object) {

        const type = object?.tpf2?.type;

        if (type !== "polygon" && type !== "polyline") {
            return false;
        }

        const points = this.getGeometryArray(object);

        return (
            points.length > 0 &&
            points.every(point =>
                Array.isArray(point) &&
                typeof point[0] === "number" &&
                typeof point[1] === "number"
            )
        );

    }

    //====================================================
    // NEARBY OBJECTS (fuer Snapping)
    //====================================================

    // Nur sichtbare Objekte im aktuellen Kartenausschnitt: bei grossen
    // OSM-Datenmengen sonst pro Mausbewegung alle Objekte durchsucht.

    getNearbyObjects() {

        const all = window.geometryManager.getLeafletObjects();

        if (!this.map) {
            return all;
        }

        const view = this.map.getBounds().pad(0.1);

        return all.filter(object => {

            if (!object._map) {
                return false;
            }

            try {

                const bounds = object.getBounds?.();

                return !bounds || view.intersects(bounds);

            } catch (error) {

                return true;

            }

        });

    }

    //====================================================
    // RETURN GEOMETRY ARRAY
    //====================================================

    getGeometryPoints() {

        if (!this.object) {
            return [];
        }

        const type =
            this.object.tpf2?.type;

        const geometry = 
            this.object.tpf2?.geometry;
        

    //====================================================
    // Polygon
    //====================================================

    if (type === "polygon") {

        const ring = this.polygonRing(geometry);

        if (ring && ring.length > 0) {

            return ring;

        }

        // Fallback: Geometrie direkt aus Leaflet holen
        
        const latlngs =
            this.object.getLatLngs?.();

        if (
            Array.isArray(latlngs) &&
            Array.isArray(latlngs[0])
        ) {

            return latlngs[0].map(
                point => [
                    point.lat,
                    point.lng
                ]
            );

        }

        return [];

    }

    // -------------------------------------------------
    // Polyline
    // -------------------------------------------------

        if (
            Array.isArray(geometry) &&
            geometry.length > 0
        ) {

            return geometry;

        }

        // Fallback: Geometrie direkt aus Leaflet holen

        const latlngs =
            this.object.getLatLngs?.();

        if (
            Array.isArray(latlngs) &&
            latlngs.length > 0
        ) {

            return latlngs.map(
                point => [
                    point.lat,
                    point.lng
                ]
            );

        }

        return [];

    }

    getGeometryArray(object = this.object) {

        if (!object) {
            return [];
        }

        const type =
            object.tpf2?.type;

        const geometry =
            object.tpf2?.geometry;

        // Polygon

        if (type === "polygon") {

            return this.polygonRing(geometry) ?? [];

        }

        // Polyline

        if (Array.isArray(geometry)) {

            return geometry;

        }


        return [];

    }

    //====================================================
    // MAP CLICK
    //====================================================

    onMapClick(event) {

        this.selectVertex(null);

    }

    //====================================================
    // RETURN ONE VERTEX
    //====================================================

    getVertex(index) {

        const points = this.getGeometryPoints();

        if (index < 0 || index >= points.length) {

            return null;

        }

        return points[index];

    }
    //====================================================
    // FIND EDGE INDEX
    //====================================================

    findEdgeIndex(object, a, b) {

        const points = this.getGeometryArray(object);
            
        const keyA =
            this.topology.vertexKey(a);

        const keyB =
            this.topology.vertexKey(b);
               
        const count =
            object.tpf2.type === "polygon"
                ? points.length
                : points.length - 1;

        for (let i = 0; i < count; i++) {

            const p1 = points[i];
            const p2 = points[(i + 1) % points.length];

            const k1 =
                this.topology.vertexKey(
                    L.latLng(p1[0], p1[1])
                );

            const k2 =
                this.topology.vertexKey(
                    L.latLng(p2[0], p2[1])
                );

            if (

                (k1 === keyA && k2 === keyB) ||

                (k1 === keyB && k2 === keyA)

            ) {

                return i;

            }

        }

        return -1;

    }

    //====================================================
    // REDRAW OBJECT
    //====================================================

    redrawObject(object = this.object) {

        if (!object) return;

        const points = this.getGeometryArray(object);
            
        const latlngs = points.map(p => [
            p[0],
            p[1]
        
        ]);    

        if (object.tpf2.type === "polygon") {

            // Geometrie mit ihrer urspruenglichen Verschachtelung
            // (Loecher, mehrere Teile) an Leaflet geben.
            object.setLatLngs(object.tpf2.geometry);

        } else {

            object.setLatLngs(latlngs);

        }

        object.redraw();

    } 

    //====================================================
    // SAVE STYLE
    //====================================================

    saveStyle() {

        if (!this.object) return;

        if (typeof this.object.setStyle !== "function") return;

        this.originalStyle = {

            color: this.object.options.color,
            weight: this.object.options.weight,
            opacity: this.object.options.opacity,

            fillColor: this.object.options.fillColor,
            fillOpacity: this.object.options.fillOpacity

        };

    }

    //====================================================
    // APPLY EDIT STYLE
    //====================================================

    setEditStyle() {

        if (!this.object) return;

        if (typeof this.object.setStyle !== "function") return;

        this.object.setStyle(this.editStyle);

    }

    //====================================================
    // RESTORE ORIGINAL STYLE
    //====================================================

    restoreStyle() {

        if (!this.object) return;

        if (!this.originalStyle) return;

        if (typeof this.object.setStyle !== "function") return;

        this.object.setStyle(this.originalStyle);

    }

    //====================================================
    // CREATE VERTEX MARKER
    //====================================================

    createVertexMarker(point) {

        return L.marker(
            [point[0], point[1]],
            {
                draggable: true,
                zIndexOffset: this.vertexHandleZIndex,
                icon: L.divIcon({
                    className: "",
                    html: `
                        <div style="
                            width: 16px;
                            height: 16px;
                            background: #ff0000;
                            border: 3px solid #ffffff;
                            border-radius: 50%;
                            box-sizing: border-box;
                            box-shadow: 0 0 0 2px #990000;
                        "></div>
                    `,
                    iconSize: [16, 16],
                    iconAnchor: [8, 8]
                })
            }
        );

    }
        
    //====================================================
    // SEGMENT ZU KURZ FUER EINEN GRIFF?
    //====================================================

    isSegmentOutOfView(a, b) {

        const view = this._editView || this.map.getBounds().pad(0.3);

        return !(
            view.contains(L.latLng(a[0], a[1])) ||
            view.contains(L.latLng(b[0], b[1])) ||
            view.contains(L.latLng(
                (a[0] + b[0]) / 2,
                (a[1] + b[1]) / 2
            ))
        );

    }

    isSegmentTooShort(a, b) {

        const pa = this.map.latLngToContainerPoint(L.latLng(a[0], a[1]));
        const pb = this.map.latLngToContainerPoint(L.latLng(b[0], b[1]));

        return pa.distanceTo(pb) < this.minSegmentLength;

    }

    //====================================================
    // ZOOM: GRIFFE NEU AUFBAUEN
    //====================================================

    onZoom() {

        if (this.object) {
            this.refresh();
        }

    }

    //====================================================
    // CREATE ALL VERTEX HANDLES
    //====================================================

    createHandles() {

        console.log("CREATE HANDLES");

        if (!this.object) return;

        const points = this.getGeometryPoints();

        // Bei geschlossenen Ringen ist der letzte Punkt nur die Kopie des
        // ersten und bekommt keinen eigenen Griff.
        const closed = this.isPolygon() && this.isClosedRing(points);

        const stats = {
            total: points.length,
            outOfView: 0,
            thinned: 0,
            created: 0
        };

        // Zu dicht liegende Punkte weglassen (Mindestabstand in Pixeln),
        // sonst entsteht bei langen Linien ein unbedienbarer Haufen.
        // Anfang und Ende bleiben immer. Beim Hineinzoomen erscheinen
        // mehr Punkte (siehe onZoom()).
        let lastPixel = null;

        // Nur Punkte im sichtbaren Ausschnitt (plus Rand). Bei grossen
        // Flaechen sonst tausende Griffe ausserhalb des Bildes.
        this._editView = this.map.getBounds().pad(0.3);

        points.forEach((point, index) => {

            if (closed && index === points.length - 1) {
                return;
            }

            const latlng = L.latLng(point[0], point[1]);

            if (!this._editView.contains(latlng)) {
                stats.outOfView++;
                return;
            }

            const pixel = this.map.latLngToContainerPoint(latlng);

            const isEnd =
                index === 0 || index === points.length - 1;

            if (
                !isEnd &&
                lastPixel &&
                pixel.distanceTo(lastPixel) < this.minHandleDistance
            ) {
                stats.thinned++;
                return;
            }

            lastPixel = pixel;

            this.createHandle(point, index);

            stats.created++;

        });

        this.lastStats = stats;

    }

    //====================================================
    // CREATE VERTEX HANDLE
    //====================================================

    createHandle(point, index) {

        const marker = this.createVertexMarker(point);

        marker.vertexIndex = index;

        this.bindVertexDragEvents(marker);

        this.bindVertexSelectionEvents(marker);

        this.bindVertexDeleteEvent(marker);

        marker.addTo(this.handleLayer);

        this.vertexHandles.push(marker);

    }

    //------------------------------------------------
    // BIND VERTEX DRAG EVENTS
    //------------------------------------------------

    bindVertexDragEvents(marker) {

        //------------------------------------------------
        // DRAG START
        //------------------------------------------------

        marker.on("dragstart", e => {

            this.saveHistory();

            this.log("DRAGSTART");

            // Ausgangsposition fuer die Meldung an Python (OSM-Nodes)
            const startLatLng = e.target.getLatLng();

            marker.dragFrom = [startLatLng.lat, startLatLng.lng];

            this.activeSharedVertices =
                this.topology.getSharedVertices(
                        e.target.getLatLng()

                );
                
            this.table(
                this.activeSharedVertices.map(v => ({
                    id: v.object.tpf2?.id,
                    lat: v.latlng.lat,
                    lng: v.latlng.lng
                }))

            );
       

            this.selectVertex(marker.vertexIndex);

            const element = marker.getElement();

            if (element) {

                element.classList.add("active");

            }

        });

        //------------------------------------------------
        // DRAG
        //------------------------------------------------

        marker.on("drag", (e) => {

            const latlng = this.snap(
                e.target.getLatLng(),
                e.target.vertexIndex
            );

            const changedObjects =
                this.topology.moveSharedVertices(
                    this.activeSharedVertices,
                    latlng
                );

            for (const object of changedObjects) {

                if (object === this.object)
                    continue;

                this.redrawObject(object);

            }

            this.updateGeometry(
                this.object,
                e.target.vertexIndex,
                latlng
            );

        });
        
        //------------------------------------------------
        // DRAG END
        //------------------------------------------------

        marker.on("dragend", () => {

            const element = marker.getElement();

            if (element) {

                element.classList.remove("active");

            }

            bridges.adapter.polylineMoved(
                this.object.tpf2.id,
                this.object.tpf2.geometry
            );

            // OSM-Objekte (numerische ID): verschobenen Punkt an Python
            // melden, dort werden die OSM-Nodes angepasst.
            if (
                typeof this.object.tpf2.id === "number" &&
                marker.dragFrom
            ) {

                const moved = this.getGeometryArray(this.object)[
                    marker.vertexIndex
                ];

                if (
                    moved &&
                    (
                        moved[0] !== marker.dragFrom[0] ||
                        moved[1] !== marker.dragFrom[1]
                    )
                ) {

                    bridges.adapter.osmVertexMoved(
                        marker.dragFrom[0],
                        marker.dragFrom[1],
                        moved[0],
                        moved[1]
                    );

                }

            }

            this.refresh();

            // Nur die Indizes neu aufbauen; rebuild() wuerde zusaetzlich
            // alle geteilten Punkte und Kanten in die Konsole schreiben.
            this.topology.buildVertexIndex();

            this.topology.buildEdgeIndex();

        });

    }

        //====================================================
        // BIND VERTEX SELECTION
        //====================================================

        bindVertexSelectionEvents(marker) {

            marker.on("click", () => {

                this.log("CLICK");
               
                this.selectVertex(
                   marker.vertexIndex
                );

                this.log(
                    "Aktiver Vertex:",
                    this.activeVertex
                );

            });

        }

        //====================================================
        // BIND VERTEX DELETE
        //====================================================
        
        bindVertexDeleteEvent(marker) {

            marker.on("contextmenu", () => {

                this.removeVertex(
                    marker.vertexIndex
                );

            });

        }

    //====================================================
    // UPDATE GEOMETRY
    //====================================================

    updateGeometry(object = this.object, index, latlng) {

        if (!object) return;

        const points =
           this.getGeometryArray(object);

        if (index < 0 || index >= points.length)
            return;

        points[index][0] = latlng.lat;
        points[index][1] = latlng.lng;

        // Geschlossener Ring: erster und letzter Punkt bleiben gleich.
        if (
            this.isClosedRing(points, object) &&
            (index === 0 || index === points.length - 1)
        ) {

            const other = index === 0 ? points.length - 1 : 0;

            points[other][0] = latlng.lat;
            points[other][1] = latlng.lng;

        }

        this.redrawObject(object);

    }

    //====================================================
    // SELECT VERTEX
    //====================================================

    selectVertex(index) {

        this.activeVertex = index;

        this.vertexHandles.forEach((handle, i) => {

            const element = handle.getElement();

            if (!element) return;

            if (handle.vertexIndex === index) {

                element.classList.add("active");

            } else {

                element.classList.remove("active");

            }

        });

    }

    //====================================================
    // SAVE HISTORY
    //====================================================

    saveHistory() {

        if (!this.object) return;

        const geometry = JSON.parse(
            JSON.stringify(this.object.tpf2.geometry)

        );

        const last = this.undoStack.at(-1);

        if (last && JSON.stringify(last) === JSON.stringify(geometry)) {
             return;
        }

        this.undoStack.push(geometry);

            
        // maximal 50 Undo-Schritte behalten
        if (this.undoStack.length > 50) {

             this.undoStack.shift();

        }


        // nach neuer Änderung ist Redo ungültig
        this.redoStack = [];

}

    //====================================================
    // UNDO
    //====================================================

    undo() {

        if (!this.undoStack.length) return;

        this.redoStack.push(

            JSON.parse(
                JSON.stringify(this.object.tpf2.geometry)
            )

        );

        this.object.tpf2.geometry =
            this.undoStack.pop();

        this.redrawObject();

        this.refresh();

}

    //====================================================
    // REDO
    //====================================================

    redo() {

        if (!this.redoStack.length) return;

        this.undoStack.push(

            JSON.parse(
                JSON.stringify(this.object.tpf2.geometry)
            )

        );

        this.object.tpf2.geometry =
            this.redoStack.pop();

        this.redrawObject();

        this.refresh();

}

    //====================================================
    // INSERT NEW VERTEX
    //====================================================

    // refresh = false: Handles nicht neu aufbauen. Noetig waehrend ein
    // Mittelpunkt-Handle gezogen wird, sonst wird der gezogene Marker
    // zerstoert und die Linie folgt der Maus nicht mehr.
    insertVertex(object = this.object, index, latlng, refresh = true) {

        if (!object) return;

        if (object === this.object) {

            this.saveHistory();

        }


        const points =
           this.getGeometryArray(object);

         points.splice(index, 0, [

            latlng.lat,
            latlng.lng

        ]);

        this.redrawObject(object);

        if (refresh && object === this.object) {

             this.refresh();

        }

    }

    //====================================================
    // CAN REMOVE VERTEX
    //====================================================

    canRemoveVertex() {

        const points =
        this.getGeometryPoints();

        if (
            this.isPolygon() &&
            points.length <= (this.isClosedRing(points) ? 4 : 3)
        ) {

            return false;

        }

        if (

            this.isPolyline() &&
            points.length <= 2
        ) {

            return false;

        }

        return true;

    }

    //====================================================
    // REMOVE VERTEX
    //====================================================

    removeVertex(index) {

        if (!this.object) return;

        if (!this.canRemoveVertex()) return;

        this.saveHistory();

        const points = 
            this.getGeometryPoints();

        const closed = this.isPolygon() && this.isClosedRing(points);

        points.splice(index, 1);

        // Wurde der erste Punkt eines geschlossenen Rings geloescht,
        // muss der Ring wieder am neuen ersten Punkt schliessen.
        if (closed && index === 0) {
            points[points.length - 1] = [points[0][0], points[0][1]];
        }

        this.redrawObject();

        this.refresh();

    }

    //====================================================
    // CREATE ALL SEGMENT HANDLES
    //====================================================

    createSegmentHandles() {

        if (!this.object) return;

        const points = this.getGeometryPoints();

        if (points.length < 2) return;

        this.segmentHandles = [];

        // Alle normalen Segmente

        for (let i = 0; i < points.length - 1; i++) {

            if (
                this.isSegmentTooShort(points[i], points[i + 1]) ||
                this.isSegmentOutOfView(points[i], points[i + 1])
            ) {
                continue;
            }

            this.createSegmentHandle(

                points[i],
                points[i + 1],
                i + 1

            );

        }

        // Polygon schließen

        if (
            this.object.tpf2.type === "polygon" &&
            !this.isSegmentTooShort(points[points.length - 1], points[0]) &&
            !this.isSegmentOutOfView(points[points.length - 1], points[0])
        ) {

            this.createSegmentHandle(

                points[points.length - 1],
                points[0],
                points.length

            );

        }

    }

    //====================================================
    // CREATE SEGMENT MARKER
    //====================================================

    createSegmentMarker(a, b) {

        return L.marker(

            [

                (a[0] + b[0]) / 2,

                (a[1] + b[1]) / 2

            ],

            {

                draggable: true,

                zIndexOffset: this.segmentHandleZIndex,

                icon: L.divIcon({

                    className: "",
                    html: `
                        <div style="
                            width: 12px;
                            height: 12px;
                            background: #ffd600;
                            border: 2px solid #ffffff;
                            border-radius: 50%;
                            box-sizing: border-box;
                            box-shadow: 0 0 0 1px #8a7200;
                        "></div>
                    `,
                    iconSize: [12, 12],
                    iconAnchor: [6, 6]

                })

            }

        );

    }

    //====================================================
    // CREATE SEGMENT HANDLE
    //====================================================

    createSegmentHandle(a, b, insertIndex) {

        const marker = this.createSegmentMarker(a, b);

            this.bindSegmentDragEvents(

                marker,

                a,

                b,

                insertIndex

        );

        marker.addTo(this.handleLayer);

        this.segmentHandles.push(marker);

    }

        //====================================================
        // BIND SEGMENT DRAG EVENTS
        //====================================================

        bindSegmentDragEvents(marker, a, b, insertIndex) {

            let inserted = false;

            let vertexIndex = -1;

            let activeSharedEdges = [];

            let activeSegmentVertices = [];

        //------------------------------------------------
        // DRAG START
        //------------------------------------------------

        marker.on("dragstart", () => {

            this.saveHistory();

            activeSegmentVertices = [];

            activeSharedEdges = 
                this.topology.getSharedEdges(

                    L.latLng(a[0], a[1]),
                    L.latLng(b[0], b[1])

                );

            for (const edge of activeSharedEdges) {

                const edgeIndex = 
                    this.findEdgeIndex(

                        edge.object,
                        edge.a,
                        edge.b

                    );

                if (edgeIndex < 0)
                    continue;

                const vertexIndex = edgeIndex + 1;

                this.insertVertex(

                    edge.object,
                    vertexIndex,
                    marker.getLatLng(),
                    false

                );

                activeSegmentVertices.push({

                    object: edge.object,

                    index: vertexIndex

                });

            }

        });

                
        //------------------------------------------------
        // DRAG 
        //------------------------------------------------

        marker.on("drag", (e) => {

            const latlng = this.snap(

                e.target.getLatLng()

            );

            if (activeSegmentVertices.length === 0) {

                if (!inserted) {

                    this.insertVertex(

                        this.object,
                        insertIndex,
                        latlng,
                        false

                    );

                    inserted = true;
                    vertexIndex = insertIndex;

                }

                this.updateGeometry(

                    this.object,

                    vertexIndex,

                    latlng

                );

                return;

            } 

            inserted = true;

            for (const item of activeSegmentVertices) {

                this.updateGeometry(

                    item.object,

                    item.index,

                    latlng

                );

            }

        });

        //------------------------------------------------
        // DRAG END
        //------------------------------------------------

        marker.on("dragend", () => {

            if (!inserted) {
                return;
            }

            const changed = new Set([this.object]);

            for (const item of activeSegmentVertices) {
                changed.add(item.object);
            }

            for (const object of changed) {

                bridges.adapter.polylineMoved(
                    object.tpf2.id,
                    object.tpf2.geometry
                );

            }

            // Handles erst jetzt neu aufbauen (siehe insertVertex).
            this.refresh();

            this.topology.buildVertexIndex();

            this.topology.buildEdgeIndex();

        });

        //------------------------------------------------
        // Marker anzeigen
        //------------------------------------------------

        marker.addTo(this.handleLayer);

        this.segmentHandles.push(marker);

    }
    //====================================================
    // RETURN SNAP VERTICES
    //====================================================

    getSnapVertices() {

        const vertices = [];

        // Eigene Vertex-Handles
        vertices.push(...this.vertexHandles);

        const addPoints = data => {

            if (!data)
                return;

            // Echter Leaflet-LatLng?
            if (data.lat !== undefined && data.lng !== undefined) {

                vertices.push({
                    getLatLng() {
                        return data;
                    }
                });

                return;

            }

            if (Array.isArray(data)) {

                for (const item of data)
                      addPoints(item);
                    
             }

        };

        const objects =
            this.getNearbyObjects();

        for (const object of objects) {

            if (object === this.object)
                continue;
            
            addPoints(
                object.getLatLngs?.()
            );

        }

         return vertices;

    }
    //====================================================
    // RETURN SNAP SEGMENTS
    //====================================================
    
    getSnapSegments() {

        const segments = [];

        const addSegments = data => {

            if (!Array.isArray(data))
                return;

            // Eine Linie gefunden?
             if (
                data.length >= 2 &&
                data[0]?.lat !== undefined &&
                data[1]?.lat !== undefined
            ) {

                for (let i = 0; i < data.length - 1; i++) {

                    segments.push({
                        a: data[i],
                        b: data[i + 1]
                    });
                
                }

                return;

            }

            // Sonst weiter in verschachtelten Arrays suchen
            for (const item of data) {

                addSegments(item);

            }

        };

        const objects = this.getNearbyObjects();

        for (const object of objects) {

            addSegments(
                object.getLatLngs?.()
            );

        }

        return segments;

    }

    //====================================================
    // RETURN CONTAINER POINT
    //====================================================

    getContainerPoint(latlng) {

        return this.map.latLngToContainerPoint(
            latlng
        );

    }

    //====================================================
    // FIND SNAP VERTEX
    //====================================================

    findSnapVertex(latlng, ignoreIndex = -1) {

        if (!this.enableSnapping) return null;

        const mouse = this.getContainerPoint(latlng);

        const vertices = this.getSnapVertices();

        for (let i = 0; i < vertices.length; i++) {

           if (
               ignoreIndex >= 0 &&
               vertices[i].vertexIndex === ignoreIndex
           ) continue;
           
           const p = this.getContainerPoint(
               vertices[i].getLatLng()

            );

            if (mouse.distanceTo(p) <= this.snapDistance) {

                 return vertices[i].getLatLng();

            }

        }

         return null;

    }

    //====================================================
    // FIND SNAP SEGMENT
    //====================================================

    findSnapSegment(latlng) {

        const mouse =
       this.getContainerPoint(latlng);

        const segments =
        this.getSnapSegments();

        for (const segment of segments) {

            const a =
             this.getContainerPoint(segment.a);

            const b =
            this.getContainerPoint(segment.b);

            const dx = b.x - a.x;
            const dy = b.y - a.y;

            const length2 =
                dx * dx + dy * dy;

            if (length2 === 0)
                continue;

            let t =
                ((mouse.x - a.x) * dx +
                 (mouse.y - a.y) * dy) / length2;

            t = Math.max(0, Math.min(1, t));

            const snapPoint = L.point(
                a.x + t * dx,
                a.y + t * dy
            );

            if (
                mouse.distanceTo(snapPoint)
                <= this.snapDistance
            ) {

                return this.map.containerPointToLatLng(
                    snapPoint
                );

            }

        }


        return null;

    }

    //====================================================
    // SNAP
    //====================================================

    snap(latlng,  ignoreIndex = -1) {

        let snap = this.findSnapVertex(latlng, ignoreIndex);

        if (!snap) {

            snap =  this.findSnapSegment(latlng);

        }

        return snap || latlng;

    }

    //====================================================
    // GET VERTEX COUNT
    //====================================================

    getVertexCount() {

        return this.getGeometryPoints().length;

    }

    //====================================================
    // IS POLYGON
    //====================================================

    isPolygon() {

        if (!this.object) return false;

        return this.object.tpf2.type === "polygon";

    }

    //====================================================
    // IS POLYLINE
    //====================================================

    isPolyline() {

        if (!this.object) return false;

        return this.object.tpf2.type !== "polygon";

    }

    //====================================================
    // GET OBJECT
    //====================================================

    getObject() {

        return this.object;

    }

    //====================================================
    // IS EDITING
    //====================================================

    isEditing() {

        return this.object !== null;

    }

    log(...args) {

        if (!this.debug)
            return;

        console.log(...args);

    }

    table(data) {

        if (!this.debug)
            return;

        console.table(data);

    }

    onKeyDown(event) {

        if (!this.object) return;

        // ESC beendet den Editiermodus
        if (event.key === "Escape") {

            event.preventDefault();

            this.stop();

             return;

        }

        // Undo
        if (event.ctrlKey && event.key.toLowerCase() === "z") {

            event.preventDefault();

            this.undo();

            return;

        }

        // Redo
         if (event.ctrlKey && event.key.toLowerCase() === "y") {

            event.preventDefault();

            this.redo();

            return;

        }

        // Delete        
        if (event.key !== "Delete") return;

        if (this.activeVertex === null) return;

        event.preventDefault();

        this.removeVertex(this.activeVertex);

        this.activeVertex = null;

    }

}
        