from src.map.style.base_style_resolver import BaseStyleResolver
from src.map.style.style import Style


class VegetationStyleResolver(BaseStyleResolver):

    DEFAULT = Style(
        color="#5b7f3a",
        width=1,
        fill_color="#7fbf5b",
        fill_opacity=0.6,
    )

    STYLES = {
        "forest": DEFAULT,      # landuse=forest
        "wood": DEFAULT,        # natural=wood
        "tree_row": Style(
            color="#5b7f3a",
            width=2,
        ),
    }

    def resolve(self, vegetation, *, zoom=None) -> Style:

        key = (
            vegetation.tags.get("landuse")
            or vegetation.tags.get("natural")
        )

        return self.STYLES.get(
            key,
            self.DEFAULT,
        )