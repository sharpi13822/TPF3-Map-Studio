from PySide6.QtCore import QObject, Signal
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView

from src.map.leaflet_api import LeafletAPI
from src.map.map_controller import MapController
from src.map.bridge import Bridge


class MapWidget(QWebEngineView):
    """
    Kartenwidget mit Leaflet, Bridge und Controller.
    """

    map_loaded = Signal(bool)

    def __init__(self):
        super().__init__()


        # ---------------------------------------------------------
        # WebEngine Entwicklerkonsole
        # ---------------------------------------------------------

        self.devtools = QWebEngineView()

        self.devtools.setWindowTitle(
            "TPF2 Map Studio – WebEngine Konsole"
        )

        self.devtools.resize(
            1000,
            700
        )

        self.page().setDevToolsPage(
            self.devtools.page()
        )

        # ---------------------------------------------------------
        # API
        # ---------------------------------------------------------

        self.api = LeafletAPI(
            self
        )

        # ---------------------------------------------------------
        # Controller
        # ---------------------------------------------------------

        self.controller = MapController(
            self.api
        )

        # ---------------------------------------------------------
        # Bridge
        # ---------------------------------------------------------

        self.bridge = Bridge(
            self.controller
        )

        self.channel = QWebChannel()

        self.channel.registerObject(
            "bridge",
            self.bridge
        )

        self.page().setWebChannel(
            self.channel
        )

        # ---------------------------------------------------------
        # Signale
        # ---------------------------------------------------------

        self.loadFinished.connect(
            self._load_finished
        )

        # ---------------------------------------------------------
        # Karte laden
        # ---------------------------------------------------------

        self.load(
            "http://127.0.0.1:8000/index.html"
        )

    # ---------------------------------------------------------
    # Intern
    # ---------------------------------------------------------

    def _load_finished(
        self,
        ok: bool
    ):

        if ok:
            print("Karte geladen")

            self.devtools.show()
            
        else:
            print("Fehler beim Laden der Karte")

        self.map_loaded.emit(ok)