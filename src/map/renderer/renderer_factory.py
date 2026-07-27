from src.map.layer import Layer

from src.map.renderer.geometry_renderer import GeometryRenderer

from src.map.style.building_style_resolver import BuildingStyleResolver
from src.map.style.road_style_resolver import RoadStyleResolver
from src.map.style.railway_style_resolver import RailwayStyleResolver
from src.map.style.water_style_resolver import WaterStyleResolver
from src.map.style.waterway_style_resolver import WaterwayStyleResolver
from src.map.style.park_style_resolver import ParkStyleResolver
from src.map.style.landuse_style_resolver import LanduseStyleResolver
from src.map.style.vegetation_style_resolver import VegetationStyleResolver


class RendererFactory:

    RENDERERS = (

        (
            Layer.ROADS,
            lambda osm: osm.highways(),
            RoadStyleResolver(),
        ),

        (
            Layer.RAILWAYS,
            lambda osm: osm.railways(),
            RailwayStyleResolver(),
        ),

        (
            Layer.BUILDINGS,
            lambda osm: osm.buildings(),
            BuildingStyleResolver(),
        ),

        (
            Layer.WATER,
            lambda osm: osm.water(),
            WaterStyleResolver(),
        ),

        (
            Layer.WATERWAYS,
            lambda osm: osm.waterways(),
            WaterwayStyleResolver(),
        ),

        (
            Layer.PARKS,
            lambda osm: osm.parks(),
            ParkStyleResolver(),
        ),

        (
            Layer.LANDUSE,
            lambda osm: osm.landuse(),
            LanduseStyleResolver(),
        ),

        (
            Layer.VEGETATION,
            lambda osm: osm.vegetation(),
            VegetationStyleResolver(),
        ),

    )

    @classmethod
    def create(cls, api, layer_manager):

        return [

            GeometryRenderer(
                api=api,
                layer_manager=layer_manager,
                style_resolver=style_resolver,
                layer=layer,
                selector=selector,
            )

            for layer, selector, style_resolver in cls.RENDERERS

        ]