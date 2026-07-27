from src.map.style.base_style_resolver import BaseStyleResolver
from src.map.style.style import Style


class LanduseStyleResolver(BaseStyleResolver):

    STYLES = {

        "farmland": Style(
            color="#c7b07a",
            width=0.5,
            opacity=0.7,
            fill_color="#f3e5ab",
            fill_opacity=0.15,
        ),
         
        "meadow": Style(
            color="#7cb342",
            width=0.5,
            opacity=0.7,
            fill_color="#c8e6a0",
            fill_opacity=0.15,
        ),

        "grass": Style(
            color="#66bb6a",
            width=0.5,
            fill_color="#a5d6a7",
            fill_opacity=0.15,
        ),

        "farmyard": Style(
            color="#8d6e63",
            width=0.5,
            fill_color="#d7ccc8",
            fill_opacity=0.15,
        ),

        "orchard": Style(
            color="#4caf50",
            width=0.5,
            fill_color="#81c784",
            fill_opacity=0.15,
        ),

        "vineyard": Style(
            color="#689f38",
            width=0.5,
            fill_color="#8bc34a",
            fill_opacity=0.15,
        ),

        "plant_nursery": Style(
            color="#388e3c",
            width=0.5,
            fill_color="#66bb6a",
            fill_opacity=0.15,
        ),

        "greenhouse_horticulture": Style(
            color="#00897b",
            width=0.5,
            fill_color="#b2dfdb",
            fill_opacity=0.15,
        ),
    }       
        
    DEFAULT = Style(
        color="#7cb342",
        width=0.5,
        fill_color="#c8e6a0",
        fill_opacity=0.15,
    )

    def resolve(self, landuse, *, zoom=None) -> Style:
        return self.STYLES.get(
            landuse.tags.get("landuse"),
            self.DEFAULT,
        )