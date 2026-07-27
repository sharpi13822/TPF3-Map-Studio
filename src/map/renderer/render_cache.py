from src.map.renderer.render_state import RenderState


class RenderCache:

    def __init__(self):
        self._states: dict[int, RenderState] = {}

    def get(self, object_id: int) -> RenderState | None:
        return self._states.get(object_id)

    def store(
        self,
        object_id: int,
        state: RenderState,
    ) -> None:
        self._states[object_id] = state

    def remove(self, object_id: int) -> None:
        self._states.pop(object_id, None)

    def clear(self):
        self._states.clear()

    @property
    def ids(self) -> set[int]:
        return set(self._states)