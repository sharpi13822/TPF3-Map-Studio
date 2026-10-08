console.log("TopologyManager geladen");

class TopologyManager {

    #geometry;

     #vertexIndex = new Map();
     #edgeIndex = new Map();

    constructor(geometryManager) {

        this.#geometry = geometryManager;

    }

    formatCoordinate(value) {

        return value.toFixed(6);

    }

    //====================================================
    // VERTEX KEY
    //====================================================

    vertexKey(latlng) {

        return `${this.formatCoordinate(latlng.lat)}|${this.formatCoordinate(latlng.lng)}`;

    }

    //====================================================
    // EdgeKey
    //====================================================

    createEdgeKey(key1, key2) {

        return key1 < key2
            ? `${key1} -> ${key2}`
            : `${key2} -> ${key1}`;

    }


    //====================================================
    // EDGE KEY
    //====================================================
    
    edgeKey(a, b) {

        const key1 = this.vertexKey(a);
        const key2 = this.vertexKey(b);

        return this.createEdgeKey(

            key1,
            key2
        );

    }

    //====================================================
    // INDEX VERTEX
    //====================================================

    indexVertex(object, data) {

        if (!data)
            return;

        if (
            data.lat !== undefined &&
            data.lng !== undefined
        ) {

            const key =
                this.vertexKey(data);

            if (!this.#vertexIndex.has(key)) {

                this.#vertexIndex.set(
                    key,
                    []
                );

            }

            this.#vertexIndex
                .get(key)
                .push({

                    object,
                    latlng: data

                });

            return;

        }

        if (Array.isArray(data)) {

           for (const item of data)
               this.indexVertex(
                   object,
                   item
                );

        }

    }

    //====================================================
    // BUILD VERTEX INDEX
    //====================================================

    buildVertexIndex() {
  
       this.#vertexIndex.clear();

    const objects =
        this.#geometry.getLeafletObjects();

    for (const object of objects) {

        this.indexVertex(
            object,
            object.getLatLngs?.()
        );

    }
  
    console.log(
        "VertexIndex:",
        this.#vertexIndex.size
    );

    

}

    //====================================================
    // PROCESS EDGE RING
    //====================================================

    processEdgeRing(object, ring) {

        if (ring.length < 2)
            return;

        for (let i = 0; i < ring.length; i++) {

            const a = ring[i];
            const b = ring[(i + 1) % ring.length];

            const key =  this.edgeKey(a, b);

            if (!this.#edgeIndex.has(key)) {

                this.#edgeIndex.set(
                    key,
                    []
                );

            }

            this.#edgeIndex
                .get(key)
                .push({

                    object,
                    a,
                    b

                });

        }

    }

    //====================================================
    // ADD EDGES
    //====================================================

    addEdges(object) {

        const latlngs = object.getLatLngs();

        const process = (coords) => {

            if (!coords)
                return;

            if (coords[0] instanceof L.LatLng) {

               this.processEdgeRing(
                   object,
                   coords
                );

            } else {

                coords.forEach(process);

            }
        };

        process(latlngs);
    }

    //====================================================
    // BUILD EDGE INDEX
    //====================================================

    buildEdgeIndex() {

        this.#edgeIndex.clear();

        const objects = this.#geometry.getLeafletObjects();

        for (const object of objects) { 
            
            this.addEdges(object);
          
                
        } 


        console.log(
            "EdgeIndex:",
            this.#edgeIndex.size
        );

    }

    //====================================================
    // REBUILD
    //====================================================

    rebuild() {

        console.log("REBUILD");

        this.buildVertexIndex();
        
        this.buildEdgeIndex();

        this.showSharedVertices();

        this.showSharedEdges();

    }

    //====================================================
    // SHOW SHARED VERTICES
    //====================================================

    showSharedVertices() {

        for (const [key, vertices] of this.#vertexIndex) {

            if (vertices.length > 1) {

                console.log(key, vertices);
            
            }

        }

    }

    //====================================================
    // SHOW SHARED EDGES
    //====================================================

    showSharedEdges() {

        for (const [key, edges] of this.#edgeIndex) {

            if (edges.length > 1) {

                console.log(key, edges);

            }

        }

    }



    //====================================================
    // GET SHARED VERTICES
    //====================================================

    getSharedVertices(latlng) {

        const key = this.vertexKey(latlng);

       return this.#vertexIndex.get(key) || [];
           

    }

    //====================================================
    // GET SHARED EDGES
    //====================================================

    getSharedEdges(a, b) {

        const key = this.edgeKey(a, b);

        return this.#edgeIndex.get(key) || [];

    }

    //====================================================
    // COLLECT NEIGHBORS
    //====================================================

    collectNeighbors(
        neighbors,
        object,
        a,
        b
    ) {

        const edges = this.getSharedEdges(a, b);

        for (const edge of edges) {

            if (edge.object !== object) {

                neighbors.add(edge.object);
                
            }

        }

    }

    //====================================================
    // GET NEIGHBORS
    //====================================================

    getNeighbors(object) {

        const neighbors = new Set();

        const latlngs = object.getLatLngs?.();

        if (!latlngs)
            return neighbors;

        const processRing = (ring) => {

            if (ring.length < 2)
                return;

            for (let i = 0; i < ring.length; i++) {

                const a = ring[i];
                const b = ring[(i + 1) % ring.length];

                this.collectNeighbors(
                    neighbors,
                    object,
                    a,
                    b
                );

            }

        };

        const process = (coords) => {

            if (!coords)
                return;

            if (coords[0] instanceof L.LatLng) {

                processRing(coords);

            } else {

                coords.forEach(process);

            }

        };

        process(latlngs);

        return neighbors;

    }

    //====================================================
    // MOVE SHARED VERTICES
    //====================================================

    moveSharedVertices(sharedVertices, latlng) {

        const objects = new Set();

        if (!sharedVertices)
            return objects;

        if (sharedVertices.length <= 1)
            return objects;

        for (const shared of sharedVertices) {

            shared.latlng.lat = latlng.lat;
            shared.latlng.lng = latlng.lng;

            objects.add(shared.object);

        }

        return objects;

    }

    // Hinweis: Durchsucht alle Objekte linear. Ein VertexIndex könnte das
    // bei sehr vielen Objekten beschleunigen.

    //====================================================
    // RETURN SHARED VERTICES
    //====================================================

    findSharedVertices(latlng) {

        const shared = [];

        const objects =
            this.#geometry.getLeafletObjects();

        for (const object of objects) {

            const addPoints = data => {

                if (!data)
                    return;

                if (
                    data.lat !== undefined &&
                    data.lng !== undefined
                ) {

                    if (
                        data.lat === latlng.lat &&
                        data.lng === latlng.lng
                    ) {

                        shared.push({
                            object,
                            latlng: data
                        });

                    }

                    return;

                }

                if (Array.isArray(data)) {

                    for (const item of data)
                        addPoints(item);

                }

            };

            addPoints(
                object.getLatLngs?.()
            );

        }

        return shared;

    }

    //====================================================
    // INSPECT VERTEX
    //====================================================

    inspectVertex(data) {

        const key = this.vertexKey(data);

        const shared = this.#vertexIndex.get(key) || [];

        console.log({

            key,
            lat: data.lat,
            lng: data.lng,
            isShared: shared.length > 1,
            objects: shared.map(v =>
                v.object.tpf2?.id
            )

        });
    }

    //====================================================
    // INSPECT OBJECT
    //====================================================

    inspectObject(object) {

        if (!object) {

            console.warn("inspectObject: Kein Objekt.");

            return;

        }

        console.group(
             `Topology ${object.tpf2?.id ?? ""}`
        );

        const addPoints = data => {

            if (!data)
                return;

            if (
               data.lat !== undefined &&
               data.lng !== undefined
            ) {

                this.inspectVertex(data);
                return;    

            }

            if (Array.isArray(data)) {

                for (const item of data)
                    addPoints(item);

            }

        };

        addPoints(
            object.getLatLngs?.()
        );

        console.groupEnd();

    }

}