console.log("DrawManager geladen");


class DrawManager {


    constructor(geometry) {

        this.geometry = geometry;

        this.mode = null;

        this.points = [];

    }


    start(type) {


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


        console.log(

            "POINT:",

            this.points

        );


    }


    finish() {


        if (!this.mode) {

            return;

        }


        if (this.points.length < 2) {


            console.warn(
                "Zu wenige Punkte"
            );


            return;

        }


        const object = 

            this.createObject();

        const created =

            this.geometry.draw(

                object

            );

        if (window.infoPanel) {


            window.infoPanel.show(

                created.tpf2

            );


        }

        console.log(

            "CREATED:",

            object

        );

        this.reset();

    }

    reset() {

        this.mode = null;

        this.points = [];



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

                [...this.points];



            if (

                polygon.length > 0

            ) {



                polygon.push(

                    polygon[0]

                );


            }



            return [

                polygon

            ];



        }




        return this.points;



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



        return layers[this.mode];



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