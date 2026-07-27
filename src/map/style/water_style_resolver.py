from src.map.style.base_style_resolver import BaseStyleResolver
from src.map.style.style import Style


class WaterStyleResolver(BaseStyleResolver):

    DEFAULT = Style(
        color="#4a90e2",
        width=1,
        fill_color="#4a90e2",
        fill_opacity=0.6,
    )

    STYLES = {
        "water": DEFAULT,       # natural=water
        "lake": DEFAULT,        # water=lake
        "pond": DEFAULT,
        "reservoir": DEFAULT,
        "basin": DEFAULT,
    }

    def resolve(self, water, *, zoom=None) -> Style:

        return self.STYLES.get(
            water.tags.get("water")
            or water.tags.get("natural"),
            self.DEFAULT,
        )