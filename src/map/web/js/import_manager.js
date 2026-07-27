console.log("ImportManager geladen");


class ImportManager {


    constructor(geometryManager) {

        this.geometry = geometryManager;

    }



    importFile(file) {


        const reader = new FileReader();



        reader.onload = (event) => {


            const data = JSON.parse(
                event.target.result
            );


            console.log(
                "IMPORT DATA:",
                data
            );



            this.loadObjects(
                data
            );


        };



        reader.readAsText(file);


    }


    loadObjects(objects) {


        console.log(
            "IMPORT OBJECTS:",
            objects
        );

        this.geometry.clearAll();


        for (const object of objects) {


        this.geometry.draw(
            object
        );


        }


        console.log(
            "IMPORT FERTIG"
        );

    }
}
