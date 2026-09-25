from PySide6.QtCore import QObject, Signal, QTimer
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

    # Der lokale HTTP-Server (LocalServer) laeuft in einem eigenen
    # Thread und braucht nach dem Start ein paar Millisekunden, bis er
    # tatsaechlich Verbindungen annimmt - in einer per PyInstaller
    # gebauten exe (mehr beim Start zu laden/entpacken) reicht die Zeit
    # bis zum ersten load()-Aufruf manchmal knapp nicht. Deshalb bei
    # einem fehlgeschlagenen ersten Versuch automatisch mehrfach mit
    # kurzer Pause erneut versuchen, bevor wirklich ein Fehler gemeldet
    # wird.
    MAX_LOAD_ATTEMPTS = 15
    RETRY_DELAY_MS = 300

    def __init__(self, base_url: str):
        super().__init__()

        # Basis-URL des lokalen Servers (LocalServer.url) - der Port
        # steht erst nach dessen Start fest, siehe LocalServer.
        self._base_url = base_url

        self._load_attempts = 0

        # ---------------------------------------------------------
        # WebEngine Entwicklerkonsole
        # ---------------------------------------------------------

        self.devtools = QWebEngineView()

        self.devtools.setWindowTitle(
            "TPF3-Map-Studio – WebEngine Konsole"
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

        self._try_load()

    # ---------------------------------------------------------
    # Intern
    # ---------------------------------------------------------

    def _try_load(self):

        self._load_attempts += 1

        self.load(
            f"{self._base_url}/index.html"
        )

    def _load_finished(
        self,
        ok: bool
    ):

        if ok:
            print("Karte geladen")

            self.map_loaded.emit(True)
            return

        if self._load_attempts < self.MAX_LOAD_ATTEMPTS:

            print(
                f"Karte noch nicht erreichbar (Versuch "
                f"{self._load_attempts}/{self.MAX_LOAD_ATTEMPTS}) - "
                f"lokaler Server vermutlich noch am Starten, "
                f"versuche erneut..."
            )

            QTimer.singleShot(
                self.RETRY_DELAY_MS,
                self._try_load
            )

            return

        print(
            f"Fehler beim Laden der Karte nach "
            f"{self.MAX_LOAD_ATTEMPTS} Versuchen"
        )

        self.map_loaded.emit(False)