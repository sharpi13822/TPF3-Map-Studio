console.log("ImportManager geladen");


class ImportManager {


    constructor(geometryManager) {

        this.geometry = geometryManager;

    }



    importFile(file) {


        const reader = new FileReader();



        reader.onload = (event) => {

            this.processImportData(
                event.target.result
            );

        };

    }  

    //====================================================
    // PROCESS IMPORT DATA
    //====================================================

    processImportData(text) {

        const data = JSON.parse(
            text
        );

        console.log(
           "IMPORT DATA:",
            data
        );

        this.loadObjects(
            data
        );

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
