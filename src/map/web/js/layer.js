class Layer {

    #leaflet;
    #name;
    #options;


    constructor(leaflet, name, options = {}) {

        this.#leaflet = leaflet;
        this.#name = name;
        this.#options = options;

    }


    get name() {
        return this.#name;
    }


    get leaflet() {
        return this.#leaflet;
    }


    clear() {

        if (this.#leaflet.clearLayers) {
            this.#leaflet.clearLayers();
        }

    }


    show(map) {

        this.#leaflet.addTo(map);

    }


    hide(map) {

        map.removeLayer(
            this.#leaflet
        );

    }

}

const LAYER_ORDER = [

    "landuse",

    "vegetation",

    "parks",

    "water",

    "roads",

    "railways",

    "buildings",

    "selection",

    "markers"

];