"""3D-Vorschau: kleine Web-Ansicht (Three.js) im Heightmap-Dialog."""

from __future__ import annotations

import json

from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView


class Preview3DWidget(QWebEngineView):

    def __init__(self, base_url: str, parent=None):
        super().__init__(parent)
        self._base_url = base_url
        self._loading = False
        self._ready = False
        self._pending = None
        self.setMinimumSize(360, 300)
        self.loadFinished.connect(self._on_loaded)

    def _on_loaded(self, ok: bool):
        self._loading = False
        self._ready = bool(ok)
        self._flush()

    def _flush(self):
        if self._ready and self._pending is not None:
            self.page().runJavaScript(f"window.setMesh({self._pending});")
            self._pending = None

    def set_mesh(self, payload: dict):
        self._pending = json.dumps(payload)
        if not self._ready and not self._loading:
            self._loading = True
            self.load(QUrl(f"{self._base_url}/preview3d.html"))
        self._flush()