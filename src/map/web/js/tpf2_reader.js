class TPF2Reader {


    read(data) {

        console.log("TPF2Reader DATA:", data);

        const objects = [];


        this.readRoads(data, objects);


        this.readRailways(data, objects);


        this.readBuildings(data, objects);


        this.readWater(data, objects);

        this.readWaterways(data, objects);

        this.readVegetation(data, objects);


        this.readParks(data, objects);


        this.readLanduse(data, objects);


        return {
            objects
        };

    }



    readRoads(data, objects) {


        for (const road of data.roads ?? []) {


            objects.push({

                id: road.id,

                layer: "roads",

                type: "polyline",

                geometry: road.geometry,

                properties: road.properties ?? {}

            });


        }

    }

    readRailways(data, objects) {


        for (const rail of data.railways ?? []) {


            objects.push({

                id: rail.id,

                layer: "railways",

                type: "polyline",

                geometry: rail.geometry,

                properties: rail.properties ?? {}

            });


        }

    }

    readBuildings(data, objects) {


        for (const building of data.buildings ?? []) {


            objects.push({

                id: building.id,

                layer: "buildings",

                type: "polygon",

                geometry: building.geometry,

                properties: building.properties ?? {}

            });


        }

    }



    readWater(data, objects) {


        for (const water of data.water ?? []) {


            objects.push({

                id: water.id,

                layer: "water",

                type: "multipolygon",

                geometry: water.geometry,

                properties: water.properties ?? {}

            });


        

        }


    }

    readWaterways(data, objects) {


        for (const waterway of data.waterways ?? []) {


            objects.push({

                id: waterway.id,

                layer: "waterways",

                type: "polyline",

                geometry: waterway.geometry,

                properties: waterway.properties ?? {}

            });


        }


    }

    readVegetation(data, objects) {


        for (const item of data.vegetation ?? []) {


            objects.push({

                id: item.id,

                layer: "vegetation",

                type: "polygon",

                geometry: item.geometry,

                properties:
                    item.properties ?? {}

            });


        }

    }

    readParks(data, objects) {


        for (const item of data.parks ?? []) {


            objects.push({

                id: item.id,

                layer: "parks",

                type: "polygon",

                geometry: item.geometry,

                properties:
                    item.properties ?? {}

            });


        }

    }
    
    readLanduse(data, objects) {


        for (const item of data.landuse ?? []) {


            objects.push({

                id: item.id,

                layer: "landuse",

                type: "polygon",

                geometry: item.geometry,

                properties:
                    item.properties ?? {}

            });


        }

    } 

}