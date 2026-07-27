class TPF2Styles {


    static get(layer) {


        switch(layer) {


            case "water":

                return {
                    color: "#4da6ff",
                    fillColor: "#66b3ff",
                    fillOpacity: 0.7
                };


            case "waterways":

                return {
                    color: "#3388ff",
                    weight: 3
                };

            case "vegetation":

                return {
                    color: "#4d994d",
                    fillColor: "#80cc80",
                    fillOpacity: 0.5
                };


            case "parks":

                return {
                    color: "#339933",
                    fillColor: "#99dd99",
                    fillOpacity: 0.5
                };


            case "roads":

                return {
                    color: "#555",
                    weight: 4
                };


            case "railways":

                return {
                    color: "#222",
                    weight: 3
                };


            case "buildings":

                return {
                    color: "#666",
                    fillColor: "#aaa",
                    fillOpacity: 0.8
                };


            default:

                return {};

        }

    }

}