from copy import deepcopy

from src.map.style.style import Style


class ZoomStyleResolver:
    """Passt einen Style an den aktuellen Zoom an."""

    def resolve(
        self,
        style: Style,
        *,
        zoom: int | None = None,
    ) -> Style:

        if zoom is None:
            return style

        style = deepcopy(style)

        if zoom < 10:

            style.width = max(1, style.width - 2)

        elif zoom < 14:

            style.width = max(1, style.width - 1)

        return style