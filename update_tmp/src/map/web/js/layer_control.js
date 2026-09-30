console.log("LayerControl geladen");


class LayerControl {


    constructor(layerManager) {

        this.layerManager = layerManager;

        this.init();

    }



    init() {


        document
            .querySelectorAll('#layer-control input[type="checkbox"]')
            .forEach(input => {


                input.addEventListener(
                    "change",
                    () => {

                        this.layerManager.toggle(
                            input.dataset.layer
                        );

                    }
                );


            });



        document
            .getElementById("layers-on")
            .addEventListener(
                "click",
                () => {

                    document
                        .querySelectorAll('#layer-control input[type="checkbox"]')
                        .forEach(input => {

                            if (!input.checked) {

                                input.checked = true;

                                this.layerManager.toggle(
                                    input.dataset.layer
                                );

                            }

                        });

                }
            );


        document
            .getElementById("layers-off")
            .addEventListener(
                "click",
                () => {

                    document
                        .querySelectorAll('#layer-control input[type="checkbox"]')
                        .forEach(input => {

                            if (input.checked) {

                                input.checked = false;

                                this.layerManager.toggle(
                                    input.dataset.layer
                                );

                            }

                        });

                }
            );


    }


}