from dataclasses import dataclass


@dataclass(slots=True)
class Style:

    color: str = "#000000"
    width: int = 1

    opacity: float = 1.0

    fill_color: str | None = None
    fill_opacity: float = 0.0

    dash_array: str | None = None

    visible: bool = True

    z_index: int = 0

    def to_dict(self) -> dict:

        return {
            "color": self.color,
            "width": self.width,
            "opacity": self.opacity,
            "fillColor": self.fill_color,
            "fillOpacity": self.fill_opacity,
            "dashArray": self.dash_array,
            "visible": self.visible,
            "zIndex": self.z_index,
        }