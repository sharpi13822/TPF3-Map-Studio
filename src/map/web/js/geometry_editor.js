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

        // aktiver Drag eines Segmenthandles
        this.activeSegmentMarker = null;

        // Index des neu erzeugten Vertex
        this.activeVertexIndex = -1;

        // Aktiver Vertex
        this.object = null;

        this.undoStack = [];
        this.redoStack = [];

        //====================================================
        // Event Handler
        //====================================================

        this.keyDownHandler = this.onKeyDown.bind(this);

        this.snapDistance = 10;   // Pixel

        this.vertexHandleZIndex = 10000;

        this.segmentHandleZIndex = 9000;

        this.enableSnapping = true;

        this.activeSharedVertices = [];

        this.debug = false;

    }

    //====================================================
    // START EDIT MODE
    //====================================================

    start(object) {


        if (!object)
            return;

        this.stop();

        this.object = object;
        this.map = object._map;

        if (!this.handleLayer) {

            this.handleLayer = L.layerGroup();

        }

        this.handleLayer.addTo(this.map);

        this.saveStyle();

        this.setEditStyle();

        this.refresh();

        this.map.doubleClickZoom.disable();

        this.map.getContainer().style.cursor = "crosshair";

        this.map.on(
            "click",
            this.onMapClick,
            this
        );
        
        document.addEventListener(
            "keydown",
            this.keyDownHandler
        );

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

        if (this.map) {


            this.map.doubleClickZoom.enable();

            this.map.getContainer().style.cursor = "";
            
            this.map.off(
            "click",
            this.onMapClick,
            this
        );

    }
        this.object = null;

        document.removeEventListener(
            "keydown",
            this.keyDownHandler
        );

        this.log("GeometryEditor STOP");

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

        this.clear();

        if (!this.object) return;

        this.createHandles();

        this.createSegmentHandles();

        // Auswahl wiederherstellen

        if (this.activeVertex !== null) {

            this.selectVertex(this.activeVertex);
    
        }

    }
    

    //====================================================
    // RETURN GEOMETRY ARRAY
    //====================================================

    getGeometryPoints() {

        if (!this.object) return [];

        if (this.object.tpf2.type === "polygon") {

             return this.object.tpf2.geometry[0];

        }

        return this.object.tpf2.geometry;

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

        const points =
            object.tpf2.type === "polygon"
                ? object.tpf2.geometry[0]
                : object.tpf2.geometry;

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

        const points = 
            object.tpf2.type === "polygon"
                ? object.tpf2.geometry[0]
                : object.tpf2.geometry;
        

        const latlngs = points.map(p => [
            p[0],
            p[1]
        
        ]);    

        if (object.tpf2.type === "polygon") {

            object.setLatLngs([latlngs]);

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
                    className: "geometry-handle",
                    iconSize: [18, 18]
                })
            }
        );

    }
        
    //====================================================
    // CREATE ALL VERTEX HANDLES
    //====================================================

    createHandles() {

        if (!this.object) return;

        const points = this.getGeometryPoints();

        points.forEach((point, index) => {

            this.createHandle(point, index);

        });

    }

    //====================================================
    // CREATE VERTEX HANDLE
    //====================================================

    createHandle(point, index) {

        const marker = this.createVertexMarker(point);

        marker.vertexIndex = index;

        //------------------------------------------------
        // DRAG START
        //------------------------------------------------

        marker.on("dragstart", e => {

            this.saveHistory();

            this.log("DRAGSTART");

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
        });

            this.selectVertex(marker.vertexIndex);

            const element = marker.getElement();

            if (element) {

                element.classList.add("active");

            }

        

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

        marker.on("dragend", () => {

            const element = marker.getElement();

            if (element) {

                element.classList.remove("active");

            }

            this.refresh();

            this.topology.rebuild();

        });


        //------------------------------------------------
        // DELETE VERTEX
        //------------------------------------------------

        marker.on("contextmenu", () => {

            this.removeVertex(

                marker.vertexIndex

            );

        });

        marker.on("click", () => {

            this.log("CLICK");

            this.selectVertex(marker.vertexIndex);

            this.log("Aktiver Vertex:", this.activeVertex);

        });

        marker.addTo(this.handleLayer);

        this.vertexHandles.push(marker);

    }

    //====================================================
    // UPDATE GEOMETRY
    //====================================================

    updateGeometry(object = this.object, index, latlng) {

        if (!object) return;

        const points = 
            object.tpf2.type === "polygon"
                ? object.tpf2.geometry[0]
                : object.tpf2.geometry;

        if (index < 0 || index >= points.length)
            return;

        // Nur den Punkt aktualisieren
        points[index][0] = latlng.lat;
        points[index][1] = latlng.lng;

        // Objekt neu zeichnen
        this.redrawObject(object);


    }

    onVertexDragStart(marker, e) {

        this.saveHistory();

        this.log("DRAGSTART");

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

    }

    //====================================================
    // REFRESH HANDLES
    //====================================================

    refreshHandles() {

        this.refresh();

    }
    //====================================================
    // SELECT VERTEX
    //====================================================

    selectVertex(index) {

        this.activeVertex = index;

        this.vertexHandles.forEach((handle, i) => {

            const element = handle.getElement();

            if (!element) return;

            if (i === index) {

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

    insertVertex(object = this.object, index, latlng) {

        if (!object) return;

        if (object === this.object) {

            this.saveHistory();

        }


        const points =
            object.tpf2.type === "polygon"
               ? object.tpf2.geometry[0]
               : object.tpf2.geometry;

         points.splice(index, 0, [

            latlng.lat,
            latlng.lng

        ]);

        this.redrawObject(object);

        if (object === this.object) {

             this.refresh();

        }

    }

    //====================================================
    // REMOVE VERTEX
    //====================================================

    removeVertex(index) {

        if (!this.object) return;

        this.saveHistory();

        const points = this.getGeometryPoints();

        // Polygon benötigt mindestens 3 Punkte
        if (

            this.object.tpf2.type === "polygon" &&
            points.length <= 3

        ) {

            return;

        }

        // Linie mindestens 2 Punkte
        if (

            this.object.tpf2.type !== "polygon" &&
            points.length <= 2

        ) {

            return;

        }

        points.splice(index, 1);

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

            this.createSegmentHandle(

                points[i],
                points[i + 1],
                i + 1

            );

        }

        // Polygon schließen

        if (this.object.tpf2.type === "polygon") {

            this.createSegmentHandle(

                points[points.length - 1],
                points[0],
                points.length

            );

        }

    }

    //====================================================
    // CREATE SEGMENT HANDLE
    //====================================================

    createSegmentHandle(a, b, insertIndex) {

        const marker = L.marker(

            [

                (a[0] + b[0]) / 2,
                (a[1] + b[1]) / 2

            ],

            {

                draggable: true,

                zIndexOffset: this.segmentHandleZIndex,

                icon: L.divIcon({

                    className: "segment-handle",

                    iconSize: [14, 14]

                })

            }

        );

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
                    marker.getLatLng()

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

            // Falls keine gemeinsame Kante existiert,
            // normales Verhalten

            if (activeSegmentVertices.length === 0) {

                if (!inserted) {

                    this.insertVertex(

                        this.object,
                        insertIndex,
                        latlng

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

            //------------------------------------------------
            // Beim ersten Ziehen wird ein neuer Vertex erzeugt
            //------------------------------------------------

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
        // Marker anzeigen
        //------------------------------------------------

        marker.addTo(this.handleLayer);

        this.segmentHandles.push(marker);

    }
    //====================================================
    // RETURN SNAP VERTICES
    //====================================================

    findVertices() {

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
            window.geometryManager.getLeafletObjects();

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
    
    findSegments() {

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

        const objects =  window.geometryManager.getLeafletObjects();

        for (const object of objects) {

            addSegments(
                object.getLatLngs?.()
            );

        }

        return segments;

    }

    //====================================================
    // FIND SNAP VERTEX
    //====================================================

    findSnapVertex(latlng, ignoreIndex = -1) {

        if (!this.enableSnapping) return null;

        const mouse = this.map.latLngToContainerPoint(latlng);

        const vertices = this.findVertices();

        for (let i = 0; i < vertices.length; i++) {

           if (i === ignoreIndex) continue;
           
           const p = this.map.latLngToContainerPoint(

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
        this.map.latLngToContainerPoint(latlng);

        const segments =
        this.findSegments();

        for (const segment of segments) {

            const a =
            this.map.latLngToContainerPoint(segment.a);

            const b =
            this.map.latLngToContainerPoint(segment.b);

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
        