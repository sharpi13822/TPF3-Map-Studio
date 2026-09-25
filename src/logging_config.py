"""
Zentrales Logging fuer TPF3-Map-Studio.

Schreibt alles in eine rotierende Logdatei unter
~/.tpf2_map_studio/logs/ (derselbe Basisordner wie der DEM-Cache) -
auch aus der per PyInstaller mit console=False gebauten exe, in der es
kein sichtbares stdout/stderr gibt. Damit koennen Nutzer bei Problemen
einfach die Logdatei schicken (Hilfe > Log-Ordner öffnen).

Bestehende print()-Aufrufe muessen dafuer NICHT umgeschrieben werden:
sys.stdout/sys.stderr werden durch einen Stream ersetzt, der jede Zeile
ins Log weiterreicht (und - falls vorhanden, also beim normalen
Python-Start - weiterhin auch auf der Konsole ausgibt).

Bewusst nur Standardbibliothek: setup_logging() wird in main.py VOR dem
ersten PySide6-Import aufgerufen.
"""

import logging
import logging.handlers
import sys
import threading
from pathlib import Path

LOG_DIR = Path.home() / ".tpf2_map_studio" / "logs"
LOG_FILE = LOG_DIR / "tpf3-map-studio.log"

_MAX_BYTES = 2 * 1024 * 1024
_BACKUP_COUNT = 3

_reentry = threading.local()

_log_path: Path | None = None


class _LogStream:
    """
    Ersatz fuer sys.stdout/sys.stderr: sammelt geschriebenen Text bis
    zum Zeilenende und gibt jede vollstaendige Zeile an den Logger
    weiter. Der Original-Stream (falls es einen gibt) bekommt den Text
    zusaetzlich unveraendert.
    """

    def __init__(self, logger: logging.Logger, level: int, original):
        self._logger = logger
        self._level = level
        self._original = original
        self._buffer = ""
        self._lock = threading.Lock()

    def write(self, text):

        if self._original is not None:
            try:
                self._original.write(text)
            except Exception:
                pass

        # Falls der Log-Handler selbst scheitert, schreibt logging die
        # Fehlermeldung nach sys.stderr - also wieder hierher. Ohne
        # diese Sperre wuerde das endlos rekursiv weiterlaufen.
        if getattr(_reentry, "active", False):
            return len(text)

        with self._lock:
            self._buffer += text
            *lines, self._buffer = self._buffer.split("\n")

        _reentry.active = True

        try:
            for line in lines:
                if line.strip():
                    self._logger.log(self._level, line.rstrip())
        finally:
            _reentry.active = False

        return len(text)

    def flush(self):

        if self._original is not None:
            try:
                self._original.flush()
            except Exception:
                pass

    def isatty(self):
        return False

    @property
    def encoding(self):
        return "utf-8"


def _log_uncaught(exc_type, exc_value, exc_tb):

    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    logging.getLogger("uncaught").critical(
        "Unbehandelte Ausnahme",
        exc_info=(exc_type, exc_value, exc_tb),
    )


def _log_uncaught_thread(args):

    logging.getLogger("uncaught").critical(
        f"Unbehandelte Ausnahme im Thread {args.thread.name if args.thread else '?'}",
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
    )


def setup_logging() -> Path | None:
    """
    Richtet Datei-Logging ein und leitet stdout/stderr ins Log um.
    Gibt den Pfad der Logdatei zurueck (None, falls der Ordner nicht
    angelegt werden konnte - dann laeuft das Programm trotzdem weiter,
    nur eben ohne Logdatei). Mehrfache Aufrufe sind wirkungslos.
    """

    global _log_path

    if isinstance(sys.stdout, _LogStream):
        return _log_path

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    log_path = None

    try:

        LOG_DIR.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )

        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(threadName)s %(name)s: %(message)s"
            )
        )

        root.addHandler(file_handler)

        log_path = LOG_FILE

    except OSError:
        pass

    # Die Streams werden nach dem Handler ersetzt - ein StreamHandler
    # auf sys.stderr wuerde sonst in sich selbst zurueckschreiben.
    sys.stdout = _LogStream(
        logging.getLogger("stdout"),
        logging.INFO,
        sys.stdout,
    )

    sys.stderr = _LogStream(
        logging.getLogger("stderr"),
        logging.ERROR,
        sys.stderr,
    )

    sys.excepthook = _log_uncaught
    threading.excepthook = _log_uncaught_thread

    logging.getLogger(__name__).info(
        "=== TPF3-Map-Studio gestartet (frozen=%s, Python %s) ===",
        getattr(sys, "frozen", False),
        sys.version.split()[0],
    )

    _log_path = log_path

    return log_path


def install_qt_message_handler():
    """
    Leitet Qt-eigene Meldungen (qWarning usw., z.B. von QtWebEngine)
    ebenfalls ins Log. Erst nach dem PySide6-Import aufrufbar.
    """

    from PySide6.QtCore import QtMsgType, qInstallMessageHandler

    logger = logging.getLogger("qt")

    levels = {
        QtMsgType.QtDebugMsg: logging.DEBUG,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL,
    }

    def handler(msg_type, context, message):
        logger.log(levels.get(msg_type, logging.INFO), message)

    qInstallMessageHandler(handler)
