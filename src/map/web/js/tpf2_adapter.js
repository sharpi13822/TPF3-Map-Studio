class TPF2Adapter {

    #geometry;


    constructor() {

        this.#geometry = new GeometryNormalizer();

    }

    parse(data) {

        const objects = [];


        for (const item of data.objects ?? []) {


            objects.push({

                id: item.id,

                layer: this.layer(item),

                type: this.type(item),

                geometry: 
                    this.#geometry.normalize(
                        this.type(item),
                        item.geometry
                    ),

                style: 
                    item.style ?? 
                    TPF2Styles.get(
                        this.layer(item)
                    )    

            });


        }


        return objects;

    }



    layer(item) {

        switch (item.kind) {

            case "road":
                return "roads";

            case "rail":
                return "railways";

            case "building":
                return "buildings";

            case "water":
                return "water";

            case "vegetation":
                return "vegetation";

            case "park":
                 return "parks";
                 
            case "landuse":
                 return "landuse";     

                 
            default:
                return "landuse";

        }

    }



    type(item) {

        if (item.geometryType) {

            return item.geometryType;

        }
        
        return "polygon";

    }

}