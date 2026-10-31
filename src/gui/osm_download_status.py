"""Visible per-worker download diagnostics; no download scheduling lives here."""
from urllib.parse import urlsplit

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextCharFormat
from PySide6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.gui.train_progress import TrainProgress
from src.i18n import tr


def format_download_event(event):
    """Format plain text so server errors cannot inject markup into the UI."""
    fields = dict(event)
    fields['server'] = urlsplit(event.get('server', '')).netloc
    fields['next_server'] = urlsplit(event.get('next_server', '')).netloc
    state = event['state']
    if state == 'error':
        reasons = {
            429: tr('Server überlastet (HTTP 429)'),
            500: tr('Interner Serverfehler (HTTP 500)'),
            502: tr('Fehler am Server-Gateway (HTTP 502)'),
            503: tr('Server nicht verfügbar (HTTP 503)'),
            504: tr('Zeitüberschreitung am Server (HTTP 504)'),
        }
        if event.get('http_status') in reasons:
            fields['error'] = reasons[event['http_status']]
        elif event.get('error_type') in ('Timeout', 'ReadTimeout', 'ConnectTimeout'):
            fields['error'] = tr('Zeitüberschreitung bei der Verbindung')
        elif event.get('error_type') == 'ConnectionError':
            fields['error'] = tr('Verbindung fehlgeschlagen')
    prefix = tr('Spur {lane} · Kachel {tile} · Versuch {attempt}').format(lane=fields['lane'], tile=fields['tile'], attempt=fields['attempt'])
    if state == 'queued':
        detail = tr('{server}: wartet auf einen freien Anfrageplatz').format(server=fields['server'])
    elif state == 'request':
        detail = tr('{server}: Anfrage läuft').format(server=fields['server'])
    elif state == 'error':
        detail = tr('{server}: Fehler — {error}').format(server=fields['server'], error=fields['error'])
    elif state == 'switch':
        detail = tr('Serverwechsel: {server} → {next_server}').format(server=fields['server'], next_server=fields['next_server'])
    elif state in ('retry', 'countdown'):
        detail = tr('Alle Server versucht; neuer Durchgang in {seconds} s').format(seconds=fields['seconds'])
    elif state == 'complete':
        detail = tr('{server}: erfolgreich, Kachel gespeichert').format(server=fields['server'])
    elif state == 'throttled':
        detail = tr('Überlastungsbremse: höchstens eine Serveranfrage gleichzeitig')
    else:
        detail = state
    return prefix + ' — ' + detail


# Farben im Verlauf: Erfolg gruen, Probleme orange, Fehler rot.
COLOR_OK = '#6fcf7f'
COLOR_WARN = '#f0a030'
COLOR_ERROR = '#ff6b6b'


def event_color(state):
    """Textfarbe fuer einen Ereignis-Zustand (None = Standardfarbe)."""

    if state == 'complete':
        return COLOR_OK
    if state == 'error':
        return COLOR_ERROR
    if state in ('switch', 'throttled', 'cooldown', 'retry'):
        return COLOR_WARN
    return None


class OsmDownloadStatus(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(tr('OSM-Download: Server und Verlauf'), parent)
        self.setObjectName('osmDownloadStatus')
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        body = QWidget(self)
        layout = QVBoxLayout(body)
        self.summary = QLabel(body)
        self.summary.setTextFormat(Qt.PlainText)
        layout.addWidget(self.summary)
        self.cache_info = QLabel(body)
        self.cache_info.setTextFormat(Qt.PlainText)
        self.cache_info.setWordWrap(True)
        self.cache_info.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.cache_info)
        self.lanes = {}
        for lane in (1, 2):
            label = QLabel(body)
            label.setWordWrap(True)
            label.setTextFormat(Qt.PlainText)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.lanes[lane] = label
            layout.addWidget(label)
        self.train = TrainProgress(body)
        layout.addWidget(self.train)
        self.history = QPlainTextEdit(body)
        self.history.setReadOnly(True)
        self.history.setMaximumBlockCount(500)
        self.history.setMinimumHeight(90)
        layout.addWidget(self.history)
        self.setWidget(body)
        self._body = body
        self._build_title_bar()

    def _build_title_bar(self):
        """Eigene Titelleiste mit Pfeil zum Ein- und Ausklappen."""

        bar = QWidget(self)
        row = QHBoxLayout(bar)
        row.setContentsMargins(6, 2, 6, 2)
        self._collapse_button = QToolButton(bar)
        self._collapse_button.setCheckable(True)
        self._collapse_button.setAutoRaise(True)
        self._collapse_button.setArrowType(Qt.DownArrow)
        self._collapse_button.setToolTip(tr("Verlauf ein- oder ausklappen"))
        self._collapse_button.toggled.connect(self.set_collapsed)
        row.addWidget(self._collapse_button)
        row.addWidget(QLabel(self.windowTitle(), bar))
        row.addStretch()
        self.setTitleBarWidget(bar)

    def set_collapsed(self, collapsed):
        """Blendet den Inhalt aus, nur die Titelleiste bleibt."""

        self._body.setVisible(not collapsed)
        self._collapse_button.setArrowType(
            Qt.RightArrow if collapsed else Qt.DownArrow
        )
        if self._collapse_button.isChecked() != collapsed:
            self._collapse_button.setChecked(collapsed)

    def _append_history(self, text, color=None):
        """Haengt eine Zeile (als reiner Text) an, optional farbig."""

        fmt = QTextCharFormat()
        if color:
            fmt.setForeground(QColor(color))
        cursor = self.history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        if not self.history.document().isEmpty():
            cursor.insertBlock()
        cursor.insertText(text, fmt)

    def start(self):
        self.history.clear()
        self.cache_info.clear()
        self.set_collapsed(False)
        self.train.reset()
        self.summary.setText(tr('OSM-Download wird vorbereitet…'))
        for lane, label in self.lanes.items():
            label.setText(tr('Spur {lane}: bereit').format(lane=lane))
        self.show()

    def set_progress(self, done, total):
        self.summary.setText(tr('OSM: {done} von {total} Kacheln fertig').format(done=done, total=total))
        self.train.set_progress(done, total)

    def set_cache_status(self, status):
        initial = tr("Beim Start: {cached} vollständig im Cache · {partial} teilweise vorhanden · {new} neu zu laden").format(
            cached=status['cached'], partial=status['initial_partial'], new=status['initial_new'])
        remaining = tr("Noch zu ergänzen: {partial} · Noch vollständig zu laden: {new}").format(
            partial=status['partial'], new=status['new'])
        self.cache_info.setText(initial + "\n" + remaining)
        self.set_progress(status['done'], status['total'])
        if status['done'] == status['cached']:
            needed = min(2, status['partial'] + status['new'])
            for lane in range(needed + 1, 3):
                self.lanes[lane].setText(tr("Spur {lane}: nicht benötigt – keine weitere Kachel offen").format(lane=lane))

    def update_event(self, event):
        text = format_download_event(event)
        self.lanes[event['lane']].setText(text)
        if event['state'] != 'countdown':
            scroll = self.history.verticalScrollBar()
            at_bottom = scroll.value() >= scroll.maximum() - 4
            previous = scroll.value()
            self._append_history(
                event['time'] + '  ' + text,
                event_color(event['state']),
            )
            scroll.setValue(scroll.maximum() if at_bottom else previous)

    def set_phase(self, text):
        self.summary.setText(text)
        self._append_history(text)

    def finish(self, message, color=COLOR_OK):
        self.summary.setText(message)
        self._append_history(message, color)
        if color == COLOR_OK:
            self.train.finish()
        for lane, label in self.lanes.items():
            label.setText(tr('Spur {lane}: Download beendet.').format(lane=lane))
