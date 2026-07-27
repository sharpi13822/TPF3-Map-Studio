class LayerStyles {

    static get(layer) {

        switch (layer) {

            case "roads":
                return {
                    color: "#555",
                    weight: 3
                };

            case "railways":
                return {
                    color: "#222",
                    weight: 2
                };

            case "buildings":
                return {
                    color: "#666",
                    fillColor: "#aaa",
                    fillOpacity: 0.7
                };

            case "water":
                return {
                    color: "#3388ff",
                    fillColor: "#3388ff",
                    fillOpacity: 0.5
                };

            case "vegetation":
                return {
                    color: "#4c9",
                    fillColor: "#6c6",
                    fillOpacity: 0.5
                };

            default:
                return {};

        }

    }

}