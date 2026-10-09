"""
Fortschrittsfenster fuer den Abruf der DGM1-Kacheln ueber hoehendaten.de.

Der Abruf laeuft in einem Hintergrund-Thread (Dgm1FetchJob), damit das Studio
nicht einfriert: Der Dienst erlaubt nur etwa 20 Kacheln pro Minute, eine grosse
Karte braucht deshalb eine halbe Stunde. Bereits geladene Kacheln liegen im
Zwischenspeicher und werden beim naechsten Mal uebersprungen.
"""

from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from src.heightmap.dgm1_dem import MIN_REQUEST_INTERVAL_S, Dgm1FetchJob
from src.i18n import tr


class Dgm1FetchDialog(QDialog):
    """Laedt die fehlenden DGM1-Kacheln und zeigt Fortschritt und Abbruch-Knopf."""

    def __init__(
        self,
        parent,
        selection,
        cache_dir: Path,
        job=None,
        title: str = tr("DGM1-Kacheln laden"),
        note: str | None = None,
        seconds_per_tile: float = MIN_REQUEST_INTERVAL_S,
    ):
        """Ohne job laedt das Fenster DGM1-Kacheln. Fuer andere Quellen (swissALTI3D) wird ein
        Auftrag mit derselben Schnittstelle uebergeben (done, total, text, finished, error,
        summary, start, cancel), dazu Titel, Hinweistext und die geschaetzte Zeit je Kachel."""

        super().__init__(parent)

        self.setWindowTitle(title)
        self.setMinimumWidth(460)

        self.error = None
        self.summary = None

        self._seconds_per_tile = seconds_per_tile

        self._job = job if job is not None else Dgm1FetchJob(selection, cache_dir)

        layout = QVBoxLayout(self)

        self.label = QLabel(tr("Starte..."))
        layout.addWidget(self.label)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        layout.addWidget(self.bar)

        self.note = QLabel(
            note
            if note is not None
            else (
                tr("Der Dienst hoehendaten.de erlaubt etwa 20 Kacheln pro Minute. "
                "Bereits geladene Kacheln werden übersprungen. Du kannst jederzeit "
                "abbrechen und später weitermachen.")
            )
        )
        self.note.setWordWrap(True)
        layout.addWidget(self.note)

        row = QHBoxLayout()
        row.addStretch(1)

        self.cancel_button = QPushButton(tr("Abbrechen"))
        self.cancel_button.clicked.connect(self._on_cancel)
        row.addWidget(self.cancel_button)

        layout.addLayout(row)

        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._poll)

    def run(self) -> bool:
        """Startet den Abruf, zeigt das Fenster und liefert True, wenn alles geladen ist."""

        self._job.start()
        self._timer.start()

        accepted = self.exec() == QDialog.Accepted

        return accepted and self.error is None

    def _on_cancel(self):
        self.cancel_button.setEnabled(False)
        self.label.setText(tr("Breche ab..."))
        self._job.cancel()

    def reject(self):
        # Esc oder Schliessen-Kreuz: wie Abbrechen, das Fenster schliesst,
        # sobald der Abruf wirklich gestoppt ist.
        self._on_cancel()

    def _poll(self):

        job = self._job

        if job.finished:
            self._timer.stop()

            if job.error:
                self.error = job.error
                super().reject()
            else:
                self.summary = job.summary
                super().accept()

            return

        if job.total > 0:
            self.bar.setValue(int(job.done * 100 / job.total))
            remaining_min = (job.total - job.done) * self._seconds_per_tile / 60.0
            self.label.setText(
                tr("{text}  (höchstens noch etwa {remaining_min:.0f} Min.)").format(text=job.text, remaining_min=remaining_min)
            )
        else:
            self.label.setText(job.text)
