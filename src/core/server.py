from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import sys


def _safe_print(*args, **kwargs):
    """
    print(), aber ohne Absturz, falls sys.stdout nicht existiert (None) -
    genau das ist in einer per PyInstaller mit console=False gebauten
    exe der Fall. Gibt einfach nichts aus, statt eine Exception zu
    werfen.
    """

    if sys.stdout is None:
        return

    try:
        print(*args, **kwargs)
    except Exception:
        pass


class _QuietRequestHandler(SimpleHTTPRequestHandler):
    """
    SimpleHTTPRequestHandler protokolliert jede Anfrage standardmaessig
    nach sys.stderr. In einer per PyInstaller mit console=False
    gebauten exe existiert sys.stderr nicht (ist None) - der Versuch,
    dorthin zu schreiben, wirft dann bei JEDER eingehenden Anfrage eine
    AttributeError im Request-Handler-Thread, die Verbindung bricht ab,
    bevor eine Antwort gesendet wird (das sah in QtWebEngine wie
    ERR_EMPTY_RESPONSE aus). Deshalb hier bewusst abgeschaltet.
    """

    def log_message(self, format, *args):
        pass


class LocalServer:
    def __init__(self, port=8000):
        self.port = port
        self.httpd = None

    def start(self):

        web_root = (Path(__file__).parent.parent / "map" / "web").resolve()

        _safe_print(f"WebRoot: {web_root}")
        _safe_print(f"WebRoot existiert: {web_root.exists()}")

        handler = partial(
            _QuietRequestHandler,
            directory=str(web_root),
        )

        try:

            self.httpd = ThreadingHTTPServer(
                ("127.0.0.1", self.port),
                handler,
            )

        except OSError as exc:

            _safe_print(f"FEHLER beim Starten des lokalen Servers: {exc}")

            raise

        def _serve():

            try:
                self.httpd.serve_forever()
            except Exception as exc:
                _safe_print(f"FEHLER im Server-Thread: {exc}")

        thread = threading.Thread(
            target=_serve,
            daemon=True,
        )

        thread.start()

        _safe_print(f"HTTP Server läuft auf http://127.0.0.1:{self.port}")

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()