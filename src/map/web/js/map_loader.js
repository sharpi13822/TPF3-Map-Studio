console.log("MapLoader geladen");


class MapLoader {


    #reader;

    #parser;

    #geometry;

    #data;


    constructor(reader, parser, geometry) {


        this.#reader = reader;

        this.#parser = parser;

        this.#geometry = geometry;


    }


    load(url) {


        console.log(
            "LOAD:",
            url
        );

        return fetch(url)


            .then(response => {


                if (!response.ok) {


                    throw new Error(
                        `HTTP Error ${response.status}`
                    );


                }


                return response.json();


            })

            .then(data => this.processData(data))

            .catch(error => {



                console.error(
                    "MAPLOADER ERROR:",
                    error
                );

                throw error;

            });


    }

    //====================================================
    // PROCESS DATA
    //====================================================

    processData(data) {

        this.#data = data;

        console.log(
            "MAPLOADER DATA:",
            data
        );

        const raw =

            this.#reader.read(
                data
            );

        console.log(
            "MAPLOADER RAW:",
            raw
        );

        const objects =

            this.#parser.parse(
                raw
            );

        console.log(
            "MAPLOADER OBJECTS:",
            objects
        );

        this.drawObjects(
            objects
        );

        console.log(
            "MAPLOADER RETURN:",
            objects
        );

        return objects;

    }


    //====================================================
    // DRAW OBJECTS
    //====================================================

    drawObjects(objects) {

        for (const object of objects) {
            
            console.log(
                "DRAW:",
                object
            );

            this.#geometry.draw(
                object
            );

        }

    }

    //====================================================
    // GET DATA
    //====================================================
    getData() {

        return this.#data;

    }

}