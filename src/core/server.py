from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading


class LocalServer:
    def __init__(self, port=8000):
        self.port = port
        self.httpd = None

    def start(self):
        web_root = (Path(__file__).parent.parent / "map" / "web").resolve()

        print(f"WebRoot: {web_root}")

        handler = partial(
            SimpleHTTPRequestHandler,
            directory=str(web_root),
        )

        self.httpd = ThreadingHTTPServer(
            ("127.0.0.1", self.port),
            handler,
        )

        thread = threading.Thread(
            target=self.httpd.serve_forever,
            daemon=True,
        )

        thread.start()

        print(f"HTTP Server läuft auf http://127.0.0.1:{self.port}")

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()