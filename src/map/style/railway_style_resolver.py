from src.map.style.base_style_resolver import BaseStyleResolver
from src.map.style.style import Style


class RailwayStyleResolver(BaseStyleResolver):

    STYLES = {

        "rail": Style(
            color="#333333",
            width=2,
            dash_array="8,4",
        ),

        "tram": Style(
            color="#666666",
            width=1.5,
            dash_array="6,3",
        ),

        "light_rail": Style(
            color="#555555",
            width=2,
            dash_array="6,3",
        ),

        "subway": Style(
            color="#222222",
            width=2,
            dash_array="4,2",
        ),

        "narrow_gauge": Style(
            color="#555555",
            width=1.5,
            dash_array="6,3",
        ),
    }

    DEFAULT = Style(
        color="#888888",
        width=2,
    )

    def resolve(self, railway, *, zoom=None) -> Style:
        return self.STYLES.get(
            railway.tags.get("railway"),
            self.DEFAULT,
        )