from src.map.style.base_style_resolver import BaseStyleResolver
from src.map.style.style import Style


class WaterwayStyleResolver(BaseStyleResolver):

    STYLES = {

        "river": Style(
            color="#4a90e2",
            width=3,
        ),

        "stream": Style(
            color="#4a90e2",
            width=2,
        ),

        "ditch": Style(
            color="#6aaed6",
            width=1,
            dash_array="4,4",
        ),

        "canal": Style(
            color="#2b7bb9",
            width=3,
        ),
    }


    DEFAULT = Style()

    def resolve(self, waterway, *, zoom=None) -> Style:
        return self.STYLES.get(
            waterway.tags.get("waterway"),
            self.DEFAULT,
        )