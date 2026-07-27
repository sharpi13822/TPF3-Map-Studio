from src.map.style.base_style_resolver import BaseStyleResolver
from src.map.style.style import Style


class RoadStyleResolver(BaseStyleResolver):

    STYLES = {

        "motorway": Style(
            color="#d73027",
            width=6,
        ),

        "trunk": Style(
            color="#fc8d59",
            width=5,
        ),

        "primary": Style(
            color="#fee090",
            width=4,
        ),

        "secondary": Style(
            color="#ffffbf",
            width=3,
        ),

        "tertiary": Style(
            color="#e0e0e0",
            width=3,
        ),

        "residential": Style(
            color="#ffffff",
            width=2,
        ),

        "service": Style(
            color="#bbbbbb",
            width=2,
        ),

        "track": Style(
            color="#8c510a",
            width=2,
            dash_array="4,4",
        ),

        "footway": Style(
            color="#cc79a7",
            width=2,
            dash_array="2,6",
        ),

        "cycleway": Style(
            color="#009e73",
            width=2,
            dash_array="6,6",
        ),
    }

    DEFAULT = Style(
        color="#888888",
        width=2,
    )

    def resolve(self, road, *, zoom=None) -> Style:
        return self.STYLES.get(
            road.tags.get("highway"),
            self.DEFAULT,
        )