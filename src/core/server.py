from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
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

    def end_headers(self):
        # Ohne Cache-Header behaelt QtWebEngine alte JS-Dateien und
        # Aenderungen an den Skripten kommen in der App nicht an.
        self.send_header("Cache-Control", "no-cache, must-revalidate")
        super().end_headers()


class _ExclusiveHTTPServer(ThreadingHTTPServer):
    """
    ThreadingHTTPServer setzt standardmaessig SO_REUSEADDR. Unter
    Windows bedeutet das - anders als unter Linux -, dass sich der
    Socket sogar an einen Port binden darf, auf dem bereits ein anderes
    Programm lauscht: es gibt dann KEINEN Fehler, eingehende
    Verbindungen landen aber zufaellig bei einem der beiden Programme.
    Deshalb hier abgeschaltet und unter Windows zusaetzlich exklusiv
    gebunden, damit ein belegter Port zuverlaessig einen OSError
    ausloest und LocalServer auf den naechsten ausweichen kann.
    """

    allow_reuse_address = False

    def server_bind(self):

        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_EXCLUSIVEADDRUSE,
                1,
            )

        super().server_bind()


class LocalServer:
    """
    Kleiner HTTP-Server fuer src/map/web.

    Versucht zuerst den bevorzugten Port (8000 - bleibt damit fuer
    QtWebEngine dieselbe Origin wie bisher), weicht bei Belegung auf die
    folgenden Ports aus und laesst sich zur Not einen beliebigen freien
    Port vom Betriebssystem geben. Der tatsaechlich verwendete Port
    steht nach start() in self.port bzw. self.url.
    """

    PREFERRED_PORT = 8000
    FALLBACK_ATTEMPTS = 20

    def __init__(self, port=PREFERRED_PORT):
        self.preferred_port = port
        self.port = None
        self.httpd = None

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def _candidate_ports(self):

        for offset in range(self.FALLBACK_ATTEMPTS):
            yield self.preferred_port + offset

        # 0 = das Betriebssystem waehlt einen freien Port
        yield 0

    def start(self):

        web_root = (Path(__file__).parent.parent / "map" / "web").resolve()

        _safe_print(f"WebRoot: {web_root}")
        _safe_print(f"WebRoot existiert: {web_root.exists()}")

        handler = partial(
            _QuietRequestHandler,
            directory=str(web_root),
        )

        last_error = None

        for port in self._candidate_ports():

            try:

                self.httpd = _ExclusiveHTTPServer(
                    ("127.0.0.1", port),
                    handler,
                )

                break

            except OSError as exc:

                last_error = exc

                _safe_print(f"Port {port} nicht verfuegbar: {exc}")

        else:

            _safe_print(
                f"FEHLER beim Starten des lokalen Servers: {last_error}"
            )

            raise last_error

        self.port = self.httpd.server_address[1]

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