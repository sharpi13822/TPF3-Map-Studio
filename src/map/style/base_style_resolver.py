from abc import ABC

from src.map.style.style import Style


class BaseStyleResolver(ABC):

    STYLES: dict[str, Style] = {}
    DEFAULT = Style()

    TAG: str

    def resolve(
        self,
        obj,
        *,
        zoom: int | None = None,
    ) -> Style:

        return self.STYLES.get(
            obj.tags.get(self.TAG),
            self.DEFAULT,
        )