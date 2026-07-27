class OSMFilter:
    """
    Filter für OSM-Objekte.
    """

    # ---------------------------------------------------------
    # Straßen
    # ---------------------------------------------------------

    @staticmethod
    def highways(osm):

        print("===== HIGHWAYS =====")
        print("ways:", len(osm.ways))

        found = 0

        for i, way in enumerate(osm.ways.values()):

            if i < 10:
                print(way.id, way.tags)

            if "highway" in way.tags:
                found += 1

        print("highways gefunden:", found)

        return (
             way
            for way in osm.ways.values()
            if "highway" in way.tags
        )

    # ---------------------------------------------------------
    # Gebäude
    # ---------------------------------------------------------

    @staticmethod
    def buildings(osm):

        return (
            way
            for way in osm.ways.values()
            if "building" in way.tags
        )

    # ---------------------------------------------------------
    # Eisenbahn
    # ---------------------------------------------------------

    @staticmethod
    def railways(osm):

        return (
            way
            for way in osm.ways.values()
            if "railway" in way.tags
        )

    # ---------------------------------------------------------
    # Parks
    # ---------------------------------------------------------

    @staticmethod
    def parks(osm):

        return (
            way
            for way in osm.ways.values()
            if way.tags.get("leisure") in {
                "park",
                "garden",
            }
        )

    # ---------------------------------------------------------
    # Landuse
    # ---------------------------------------------------------

    @staticmethod
    def landuse(osm):

        allowed = {
            "farmland",
            "farmyard",
            "grass",
            "meadow",
            "orchard",
            "vineyard",
            "plant_nursery",
            "greenhouse_horticulture",
        }

        return (
            way
            for way in osm.ways.values()
            if way.tags.get("landuse") in allowed
        )

    # ---------------------------------------------------------
    # Vegetation
    # ---------------------------------------------------------

    @staticmethod
    def vegetation_ways(osm):

        return (
            way
            for way in osm.ways.values()
            if (
                way.tags.get("landuse") == "forest"
                or way.tags.get("natural") == "wood"
                or way.tags.get("natural") == "tree_row"
            )
        )

    @staticmethod
    def vegetation_relations(osm):

        return (
            relation
            for relation in osm.relations.values()
            if (
                relation.tags.get("landuse") == "forest"
                or relation.tags.get("natural") == "wood"
            )
        )

    @staticmethod
    def vegetation(osm):

        yield from OSMFilter.vegetation_ways(osm)
        yield from OSMFilter.vegetation_relations(osm)

    # ---------------------------------------------------------
    # Wasserflächen
    # ---------------------------------------------------------

    @staticmethod
    def water_ways(osm):

        return (
            way
            for way in osm.ways.values()
            if (
                way.tags.get("natural") == "water"
                or way.tags.get("water") in {
                    "lake",
                    "pond",
                    "reservoir",
                    "basin",
                }
                or way.tags.get("landuse") == "reservoir"
            )
        )

    @staticmethod
    def water_relations(osm):

        return (
            relation
            for relation in osm.relations.values()
            if (
                relation.tags.get("type") == "multipolygon"
                and (
                    relation.tags.get("natural") == "water"
                    or relation.tags.get("water") in {
                        "lake",
                        "pond",
                        "reservoir",
                        "basin",
                    }
                    or relation.tags.get("landuse") == "reservoir"
                )
            )
        )

    @staticmethod
    def water(osm):

        # Ways sammeln, die Teil einer Wasser-Relation sind
        relation_way_ids = set()

        for relation in OSMFilter.water_relations(osm):
            for member in relation.members:
                if member.type == "way":
                    relation_way_ids.add(member.ref)

        # Nur eigenständige Wasser-Ways zurückgeben
        yield from (
            way
            for way in OSMFilter.water_ways(osm)
            if way.id not in relation_way_ids
        )

        # Danach die Multipolygone
        yield from OSMFilter.water_relations(osm)

    # ---------------------------------------------------------
    # Wasserwege
    # ---------------------------------------------------------

    @staticmethod
    def waterway_ways(osm):

        return (
            way
            for way in osm.ways.values()
            if "waterway" in way.tags
        )

    @staticmethod
    def waterway_relations(osm):

        return iter(())

    @staticmethod
    def waterways(osm):

        yield from OSMFilter.waterway_ways(osm)
        yield from OSMFilter.waterway_relations(osm)