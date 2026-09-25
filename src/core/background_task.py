"""
Langsame Vorgaenge (Netzwerk-Downloads, grosse numpy-Rechnungen) ohne
eingefrorenes Fenster ausfuehren.

run_in_background() startet die Funktion in einem eigenen Thread und
ruft danach on_success(ergebnis) bzw. on_error(exception) wieder im
GUI-Thread auf - dort darf dann ganz normal auf Widgets und die
Karte (runJavaScript) zugegriffen werden. Die Hintergrund-Funktion
selbst darf das NICHT.

Bewusst threading.Thread(daemon=True) statt QThreadPool: ein noch
laufender Download (bis zu 60 s pro Overpass-Server) soll das Beenden
des Programms nicht blockieren.
"""

import logging
import threading
from typing import Any, Callable

from PySide6.QtCore import QObject, Qt, Signal, Slot

logger = logging.getLogger(__name__)

# Haelt die Relay-Objekte am Leben, bis ihr Ergebnis zugestellt wurde.
_active: set["_Relay"] = set()


class _Relay(QObject):
    """
    Lebt im GUI-Thread. Die Signale werden aus dem Hintergrund-Thread
    ausgeloest und per QueuedConnection an die eigenen Slots - also im
    GUI-Thread - zugestellt.
    """

    _succeeded = Signal(object)
    _failed = Signal(object)

    def __init__(self, on_success, on_error):
        super().__init__()

        self._on_success = on_success
        self._on_error = on_error

        self._succeeded.connect(self._deliver_success, Qt.QueuedConnection)
        self._failed.connect(self._deliver_error, Qt.QueuedConnection)

    @Slot(object)
    def _deliver_success(self, result):

        _active.discard(self)

        self._on_success(result)

    @Slot(object)
    def _deliver_error(self, exc):

        _active.discard(self)

        if self._on_error is not None:
            self._on_error(exc)


def run_in_background(
    fn: Callable[[], Any],
    on_success: Callable[[Any], None],
    on_error: Callable[[BaseException], None] | None = None,
    name: str = "background-task",
) -> None:
    """
    Fuehrt fn() in einem Hintergrund-Thread aus. Muss aus dem
    GUI-Thread aufgerufen werden.
    """

    relay = _Relay(on_success, on_error)
    _active.add(relay)

    def _run():

        try:
            result = fn()
        except Exception as exc:
            logger.exception("Hintergrund-Vorgang '%s' fehlgeschlagen", name)
            relay._failed.emit(exc)
            return

        relay._succeeded.emit(result)

    threading.Thread(target=_run, name=name, daemon=True).start()
