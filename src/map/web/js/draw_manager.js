console.log("DrawManager geladen");


class DrawManager {


    constructor(geometry, polylineLayer) {

        this.geometry = geometry;

        this.polylineLayer = polylineLayer;

        this.mode = null;

        this.points = [];

        this.previewLine = null;

    }


    start(type) {

        this.removePreview();

        this.mode = type;

        this.points = [];


        console.log(
            "DRAW MODE:",
            type
        );

    }


    addPoint(lat, lon) {

        if (!this.mode) {

            return;

        }


        this.points.push([

            lat,
            lon

        ]);


        if (this.points.length >= 2) {

            if (!this.previewLine) {

                this.previewLine = L.polyline(
                    this.points,
                    {
                        color: "#ff0000",
                        weight: 4,

                        // Vorschau darf keine Klicks abfangen
                        interactive: false
                    }
                );

                this.previewLine.addTo(
                    this.polylineLayer
                );

            } else {

                this.previewLine.setLatLngs(
                    this.points
                );

            }

        }


        console.log(
            "POINT:",
            this.points
        );

    }


    finish() {

        if (!this.mode) {

            return null;

        }


        const minimumPoints =
            this.mode === "building"
                ? 3
                : 2;


        if (
            this.points.length < minimumPoints
        ) {

            console.warn(
                "Zu wenige Punkte"
            );

            return null;

        }


        const object =
            this.createObject();


        // Vorschau entfernen
        this.removePreview();


        /*
         * Das echte Objekt wird über den
         * GeometryManager erzeugt.
         *
         * Dadurch bleibt der Click-Handler
         * für die Bearbeitungspunkte erhalten.
         */
        const created = this.geometry.draw({
            layer: object.layer,
            id: object.id,
            type: object.type,
            geometry: object.geometry,
            style: {},
            properties: object.properties
        });
       
        /*
         * Straße / Fluss in das Python-Projekt
         * übernehmen.
         *
         * Die Bridge erzeugt KEINE zweite
         * sichtbare Polyline.
         */
        if (
            this.mode === "road" ||
            this.mode === "river"
        ) {

            if (
                typeof bridges !== "undefined" &&
                bridges.adapter &&
                typeof bridges.adapter.addPolyline === "function"
            ) {

                bridges.adapter.addPolyline(
                    object.id,
                    object.geometry,
                    object.properties.name
                );

            } else {

                console.warn(
                    "DrawManager: bridges.adapter.addPolyline nicht verfügbar"
                );

            }

        }


        /*
         * QtWebEngine zeichnet den Canvas nach dem Entfernen der
         * Vorschau und dem Hinzufügen des Objekts teils nicht neu.
         * Dann bleibt die fertige Straße / der Fluss unsichtbar.
         */
        if (typeof forceMapRedraw === "function") {

            forceMapRedraw();

        }


        if (
            window.infoPanel &&
            created
        ) {

            window.infoPanel.show(
                created.tpf2
            );

        }


        console.log(
            "CREATED:",
            object
        );


        this.reset();


        return created;

    }


    reset() {

        this.removePreview();

        this.mode = null;

        this.points = [];

    }


    cancel() {

        this.reset();

    }


    removePreview() {

        if (!this.previewLine) {

            return;

        }


        try {

            this.polylineLayer.removeLayer(
                this.previewLine
            );

        } catch (error) {

            console.warn(
                "Preview konnte nicht entfernt werden:",
                error
            );

        }


        this.previewLine = null;

    }


    //====================================================
    // CREATE OBJECT
    //====================================================

    createObject() {

        return {

            id:

                this.mode +

                "_" +

                Date.now(),


            layer:

                this.getLayer(),


            type:

                this.getGeometryType(),


            geometry:

                this.createGeometry(),


            properties:

                this.createProperties()

        };

    }


    createGeometry() {

        if (
            this.mode === "building"
        ) {

            const polygon =
                this.points.map(
                    point => [...point]
                );


            if (
                polygon.length > 0
            ) {

                const first =
                    polygon[0];

                const last =
                    polygon[
                        polygon.length - 1
                    ];


                if (
                    first[0] !== last[0] ||
                    first[1] !== last[1]
                ) {

                    polygon.push([
                        first[0],
                        first[1]
                    ]);

                }

            }


            return [
                polygon
            ];

        }


        return this.points.map(
            point => [...point]
        );

    }


    createProperties() {

        const properties = {

            name:
                "Neues Objekt",

            type:
                this.mode

        };


        if (
            this.mode === "building"
        ) {

            properties.height = 10;

            properties.levels = 1;

            properties.usage =
                "residential";

        }


        return properties;

    }


    getLayer() {

        const layers = {

            road:
                "roads",

            river:
                "waterways",

            building:
                "buildings"

        };


        return layers[
            this.mode
        ];

    }


    getGeometryType() {

        if (
            this.mode === "building"
        ) {

            return "polygon";

        }


        return "polyline";

    }

}