from src.map.style.base_style_resolver import BaseStyleResolver
from src.map.style.style import Style


class BuildingStyleResolver(BaseStyleResolver):

    STYLES = {
        "house": Style(
            color="#666666",
            width=1,
            fill_color="#bdbdbd",
            fill_opacity=0.8,
        ),
        "garage": Style(
            color="#666666",
            width=1,
            fill_color="#bdbdbd",
            fill_opacity=0.8,
        ),
        "industrial": Style(
            color="#666666",
            width=1,
            fill_color="#bdbdbd",
            fill_opacity=0.8,
        ),
        "commercial": Style(
            color="#666666",
            width=1,
            fill_color="#bdbdbd",
            fill_opacity=0.8,
        ),
        "church": Style(
            color="#666666",
            width=1,
            fill_color="#bdbdbd",
            fill_opacity=0.8,
        ),
    }

    DEFAULT = Style(
        color="#666666",
        width=1,
        fill_color="#bdbdbd",
        fill_opacity=0.8,
    )

    def resolve(self, building, *, zoom=None) -> Style:
        return self.STYLES.get(
            building.tags.get("building"),
            self.DEFAULT,
        )