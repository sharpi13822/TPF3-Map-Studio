export default class EditManager {

    #engine;

    #feature = null;

    #layer = null;

    #handles = [];


    constructor(engine) {

        this.#engine = engine;

    }


    get feature() {

        return this.#feature;

    }


    get editing() {

        return this.#feature !== null;

    }


    start(feature, layer) {

        this.stop();

        this.#feature = feature;

        this.#layer = layer;

        this.createHandles();

    }


    stop() {

        this.removeHandles();

        this.#feature = null;

        this.#layer = null;

    }


    createHandles() {

        // kommt im nächsten Schritt

    }


    removeHandles() {

        for (const handle of this.#handles) {

            handle.remove();

        }

        this.#handles.length = 0;

    }

}