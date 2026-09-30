from __future__ import annotations

from src.map.layer import Layer


class LayerManager:

    def __init__(self) -> None:

        self._visible = {
            layer: True
            for layer in Layer
        }

        self._locked = {
            layer: False
            for layer in Layer
        }

        self._opacity = {
            layer: 1.0
            for layer in Layer
        }

        self._order = list(Layer)

    # ---------------------------------------------------------
    # Sichtbarkeit
    # ---------------------------------------------------------

    def is_visible(self, layer: Layer) -> bool:
        return self._visible[layer]

    def set_visible(
        self,
        layer: Layer,
        visible: bool,
    ) -> None:

        self._visible[layer] = visible

    # ---------------------------------------------------------
    # Sperren
    # ---------------------------------------------------------

    def is_locked(self, layer: Layer) -> bool:
        return self._locked[layer]

    def set_locked(
        self,
        layer: Layer,
        locked: bool,
    ) -> None:

        self._locked[layer] = locked

    # ---------------------------------------------------------
    # Deckkraft
    # ---------------------------------------------------------

    def opacity(self, layer: Layer) -> float:
        return self._opacity[layer]

    def set_opacity(
        self,
        layer: Layer,
        opacity: float,
    ) -> None:

        self._opacity[layer] = max(
            0.0,
            min(1.0, opacity),
        )

    # ---------------------------------------------------------
    # Reihenfolge
    # ---------------------------------------------------------

    def move_up(
        self,
        layer: Layer,
    ) -> None:

        index = self._order.index(layer)

        if index == 0:
            return

        self._order[index], self._order[index - 1] = (
            self._order[index - 1],
            self._order[index],
        )

    def move_down(
        self,
        layer: Layer,
    ) -> None:

        index = self._order.index(layer)

        if index == len(self._order) - 1:
            return

        self._order[index], self._order[index + 1] = (
            self._order[index + 1],
            self._order[index],
        )

    # ---------------------------------------------------------
    # Layer
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # Speichern
    # ---------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "visible": {
                layer.name: value
                for layer, value in self._visible.items()
            },
            "locked": {
                layer.name: value
                for layer, value in self._locked.items()
            },
            "opacity": {
                layer.name: value
                for layer, value in self._opacity.items()
            },
            "order": [
                layer.name
                for layer in self._order
            ],
        }

    # ---------------------------------------------------------
    # Laden
    # ---------------------------------------------------------

    def from_dict(self, data: dict) -> None:

        visible = data.get("visible", {})
        locked = data.get("locked", {})
        opacity = data.get("opacity", {})
        order = data.get("order", [])

        for name, value in visible.items():
            layer = Layer[name]
            self._visible[layer] = bool(value)

        for name, value in locked.items():
            layer = Layer[name]
            self._locked[layer] = bool(value)

        for name, value in opacity.items():
            layer = Layer[name]
            self._opacity[layer] = float(value)

        if order:
            self._order = [
                Layer[name]
                for name in order
            ]
    
    @property
    def layers(self) -> tuple[Layer, ...]:
        return tuple(self._order)