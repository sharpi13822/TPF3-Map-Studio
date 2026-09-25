class PolylineManager {

    #layer;
    #polylines;

    constructor(layer) {

        this.#layer = layer;
        this.#polylines = new Map();
    }

    add(id, points, text = "") {

        let polyline = this.#polylines.get(id);

        if (!polyline) {

            const latLngs = points.map(
                point => [
                    point[0],
                    point[1]
                ]
            );

            polyline = L.polyline(
                latLngs
            );

            polyline.addTo(
                this.#layer
            );

            this.#polylines.set(
                id,
                polyline
            );
        }
    }

    remove(id) {

        const polyline =
            this.#polylines.get(id);

        if (!polyline) {
            return;
        }

        this.#layer.removeLayer(
            polyline
        );

        this.#polylines.delete(
            id
        );
    }

    clear() {

        for (const polyline of this.#polylines.values()) {

            this.#layer.removeLayer(
                polyline
            );
        }

        this.#polylines.clear();
    }
}