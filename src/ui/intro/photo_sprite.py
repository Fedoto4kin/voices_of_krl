from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt, Signal, QTimer
from PySide6.QtGui import QPixmap
import random


class PhotoSprite(QLabel):
    fadedOut = Signal()

    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)

        self.setPixmap(pixmap)
        self.setScaledContents(False)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(0.0)
        self.fade_in = QPropertyAnimation(self.opacity, b"opacity")
        self.fade_in.setDuration(2000)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_out = QPropertyAnimation(self.opacity, b"opacity")
        self.fade_out.setDuration(2000)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_in.finished.connect(self._on_fade_in_finished)
        self.fade_out.finished.connect(self._on_fade_out_finished)

    def start_cycle(self):
        self.start_fade_in()

    def start_fade_in(self):
        self.fade_out.stop()
        self.fade_in.start()

    def start_fade_out(self):
        self.fade_in.stop()
        self.fade_out.start()

    def _on_fade_in_finished(self):
        duration = random.randint(5500, 6500)
        QTimer.singleShot(duration, self.start_fade_out)

    def _on_fade_out_finished(self):
        self.fadedOut.emit()
