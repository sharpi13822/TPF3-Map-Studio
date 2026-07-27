class GeometryNormalizer {


    normalize(type, geometry) {

        switch(type) {


            case "polyline":

                return this.line(
                    geometry
                );


            case "polygon":

                return this.polygon(
                    geometry
                );


            case "multipolygon":

                return this.multiPolygon(
                    geometry
                );


            default:

                throw new Error(
                    `Unknown geometry type '${type}'`
                );

        }

    }



    line(points) {

        return points.map(
            point => [
                point[0],
                point[1]
            ]
        );

    }



    polygon(rings) {

        return rings.map(
            ring =>
                ring.map(
                    point => [
                        point[0],
                        point[1]
                    ]
                )
        );

    }



    multiPolygon(polygons) {

        return polygons.map(
            polygon =>
                polygon.map(
                    ring =>
                        ring.map(
                            point => [
                                point[0],
                                point[1]
                            ]
                        )
                )
        );

    }

}