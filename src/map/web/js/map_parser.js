console.log("MapParser geladen");


class MapParser {


    parse(data) {

        return data.objects.map(
            object => ({


                id: object.id,

                layer: object.layer,

                type: object.type,

                geometry: object.geometry,


                properties:
                    object.properties ?? {},


                style:
                    LayerStyles.get(object.layer)


            })
        );

    }

}