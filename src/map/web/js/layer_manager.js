class LayerManager {

    #engine;
    #layers;


    constructor(engine) {

        this.#engine = engine;

        this.#layers = new Map();

    }


    register(name, options = {}) {

        if (this.#layers.has(name)) {

            return this.#layers.get(name);

        }


        const layer = new Layer(
            this.#engine.leaflet,
            name,
            options
        );


        this.#layers.set(
            name,
            layer
        );


        return layer;

    }



    /**
     * Registriert ein bereits fertiges Layer-artiges Objekt (z.B.
     * RasterLayer fuer eine externe Kachelebene) statt intern einen neuen
     * Layer zu erzeugen wie register(). Das Objekt muss .leaflet,
     * .show(map), .hide(map) und .setVisible(map, visible) bereitstellen -
     * danach funktionieren toggle()/get()/clear() etc. identisch wie bei
     * einem normalen Layer.
     */
    registerExternal(name, layerLike) {

        if (this.#layers.has(name)) {
            return this.#layers.get(name);
        }

        this.#layers.set(name, layerLike);

        return layerLike;

    }

    unregister(name) {

        return this.#layers.delete(name);

    }



    get(name) {

        return this.#layers.get(name) ?? null;

    }



    has(name) {

        return this.#layers.has(name);

    }



    clear(name) {

        const layer = this.get(name);


        if (!layer) {

            return false;

        }


        layer.clear();

        return true;

    }



    clearAll() {

        for (const layer of this.#layers.values()) {

            layer.clear();

        }

    }



    names() {

        return [
            ...this.#layers.keys()
        ];

    }



    values() {

        return [
            ...this.#layers.values()
        ];

    }



    forEach(callback) {

        this.#layers.forEach(
            callback
        );

    }



    statistics() {

        const result = {};


        for (const [name, layer] of this.#layers) {

            result[name] = layer.size
                
        }


        return result;

    }



    setOrder() {

        const order = [

            "landuse",
            "vegetation",
            "parks",
            "water",
            "waterways",
            "roads",
            "railways",
            "buildings",
            "selection",
            "markers"

        ];

        for (let i = 0; i < order.length; i++) {


            const name =
                order[i];


            const layer =
                this.get(name);



            if (!layer) {

                continue;

            }



            layer.leaflet.eachLayer(

                object => {


                    object.setZIndex?.(
                        i
                    );


                }

            );


        }


    }

    toggle(name) {

        const layer = this.get(name);

        if (!layer) {

            return false;

        }


        const map = this.#engine.leaflet;


        if (map.hasLayer(layer.leaflet)) {

            layer.hide(map);

        } else {

            layer.show(map);

        }


        return true;

    }
}