class InfoPanel {


    constructor() {

        this.object = null;

        this.create();

    }



    create() {


        const panel =
            document.createElement("div");


        panel.id = "info-panel";


        panel.innerHTML = `

        <div class="info-title">

            Objekt Information

        </div>


        <div id="info-content">

            Kein Objekt ausgewählt

        </div>


        <button id="edit-object">

            Bearbeiten

        </button>

        <button id="delete-object">

            Löschen

        </button>

        `;



        document.body.appendChild(panel);



        this.panel = panel;


        this.content =
            panel.querySelector(
                "#info-content"
            );


        this.editButton =
            panel.querySelector(
                "#edit-object"
            );

        this.deleteButton =
            panel.querySelector(
                "#delete-object"
            ); 


        this.editButton.onclick = () => {

            this.edit();

        };

        this.deleteButton.onclick = () => {

            this.delete();

        };


    }





    translateValue(key, value) {


        if (key !== "type") {

            return value;

        }


        const translations = {


            river: "Fluss",

            waterway: "Wasserweg",

            road: "Straße",

            railway: "Eisenbahn",

            building: "Gebäude",

            park: "Park",

            forest: "Wald",

            vegetation: "Vegetation",

            lake: "See",

            residential: "Wohngebiet",

            industrial: "Industrie",

            commercial: "Gewerbe"


        };


        return translations[value] ?? value;


    }





    reverseTranslateValue(key, value) {


        if (key !== "type") {

            return value;

        }


        const translations = {


            "Fluss": "river",

            "Wasserweg": "waterway",

            "Straße": "road",

            "Eisenbahn": "railway",

            "Gebäude": "building",

            "Park": "park",

            "Wald": "forest",

            "Vegetation": "vegetation",

            "See": "lake",

            "Wohngebiet": "residential",

            "Industrie": "industrial",

            "Gewerbe": "commercial"


        };


        return translations[value] ?? value;


    }





    translateLayer(layer) {


        const layers = {


            water: "Wasser",

            waterways: "Gewässer",

            roads: "Straßen",

            railways: "Eisenbahn",

            buildings: "Gebäude",

            parks: "Parks",

            vegetation: "Vegetation",

            landuse: "Landnutzung"


        };


        return layers[layer] ?? layer;


    }





    show(object) {


        this.object = object;



        if (!object) {


            this.content.innerHTML =

            `

            Kein Objekt ausgewählt

            `;


            return;

        }



        let properties =
            "Keine Eigenschaften";



        if (
            object.properties &&
            Object.keys(object.properties).length
        ) {


            const order = [


                "name",

                "type",

                "height",

                "width",

                "speed",

                "lanes",

                "surface",

                "usage",

                "access",

                "density"


            ];



            const labels = {


                name: "Name",

                type: "Typ",

                height: "Höhe",

                width: "Breite",

                speed: "Geschwindigkeit",

                lanes: "Spuren",

                surface: "Belag",

                usage: "Nutzung",

                access: "Zugang",

                density: "Dichte"


            };



            properties =


                Object.entries(
                    object.properties
                )

                .sort(
                    ([a],[b]) => {


                        const ia =
                            order.indexOf(a);


                        const ib =
                            order.indexOf(b);



                        if (
                            ia === -1 &&
                            ib === -1
                        ) {

                            return a.localeCompare(b);

                        }


                        if (ia === -1) {

                            return 1;

                        }


                        if (ib === -1) {

                            return -1;

                        }


                        return ia - ib;


                    }
                )


                .map(
                    ([key,value]) => {


                        const title =
                            labels[key] ?? key;


                        const displayValue =
                            this.translateValue(
                                key,
                                value
                            );



                        return `

                        <div class="property-row">

                            <b>${title}:</b>

                            <br>

                            ${displayValue}

                        </div>

                        `;


                    }

                )

                .join("");


        }





        this.content.innerHTML =


        `

        <b>ID:</b>

        ${object.id}


        <br>


        <b>Layer:</b>

        ${this.translateLayer(object.layer)}


        <br>


        <b>Typ:</b>

        ${
            this.translateValue(
                "type",
                object.type
            )
        }


        <br>


        <b>Punkte:</b>

        ${
            object.geometry
            ?
            object.geometry.length
            :
            0
        }


        <br><br>


        <b>Eigenschaften:</b>


        <br><br>


        ${properties}


        `;


    }





    edit() {


        if (!this.object) {

            return;

        }



        if (!this.object.properties) {

            this.object.properties = {};

        }



        const properties =
            this.object.properties;



        const fields = [


            "name",

            "type",

            "height",

            "width",

            "speed",

            "lanes",

            "surface",

            "usage",

            "access",

            "density"


        ];



        const labels = {


            name: "Name",

            type: "Typ",

            height: "Höhe",

            width: "Breite",

            speed: "Geschwindigkeit",

            lanes: "Spuren",

            surface: "Belag",

            usage: "Nutzung",

            access: "Zugang",

            density: "Dichte"


        };



        let html = `


        <b>Eigenschaften bearbeiten</b>


        <br><br>


        `;



        for (const field of fields) {


            let value =
                properties[field] ?? "";



            if (field === "type") {


                value =
                    this.translateValue(
                        field,
                        value
                    );


            }



            html += `


            <label>


            ${labels[field]}


            <br>


            <input

                id="edit-${field}"

                value="${value}"

            >


            </label>


            <br><br>


            `;


        }



        html += `


        <button id="save-properties">

            Speichern

        </button>


        `;



        this.content.innerHTML = html;



        const saveButton =

            this.content.querySelector(
                "#save-properties"
            );



        saveButton.onclick = () => {


            for (const field of fields) {


                const input =

                    this.content.querySelector(
                        "#edit-" + field
                    );



                if (input.value !== "") {


                    properties[field] =

                        this.reverseTranslateValue(
                            field,
                            input.value
                        );


                }


            }



            this.object.properties =
                properties;



            this.show(
                this.object
            );


        };


    }

        delete() {


            if (!this.object) {

                return;

            }


            if (!confirm("Objekt wirklich löschen?")) {

                return;

            }


            console.log(
                "DELETE:",
                this.object
            );


            window.geometryManager.remove(
                this.object.layer,
                this.object.id
            );


            this.object = null;


            this.content.innerHTML =
                "Kein Objekt ausgewählt";


        }

}