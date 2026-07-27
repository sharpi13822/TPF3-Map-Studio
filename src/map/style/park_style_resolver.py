from src.map.style.base_style_resolver import BaseStyleResolver
from src.map.style.style import Style


class ParkStyleResolver(BaseStyleResolver):

    STYLES = {

        "park": Style(
            color="#66bb6a",
            width=1,
            fill_color="#c8e6a0",
            fill_opacity=0.20,
        ),

        "garden": Style(
            color="#81c784",
            width=1,
            fill_color="#dcedc8",
            fill_opacity=0.20,
        ),
    }

    DEFAULT = Style()

    def resolve(self, park, *, zoom=None) -> Style:
        return self.STYLES.get(
            park.tags.get("leisure"),
            self.DEFAULT,
        )