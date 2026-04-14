from PySide6.QtCore import QRectF, QTimer
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget

class SpotifyBarsWidget(QWidget):

    COLOR = "#a44546"

    def __init__(self, parent=None, bars=10):
        super().__init__(parent)
        self.bars = bars
        self.values = [0] * bars
        self.target = [0] * bars

        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._animate)
        self.timer.start()

        self.setFixedWidth(bars * 6 + (bars - 1) * 4)

    def update_real_values(self, fft_values):
        for i in range(self.bars):
            self.target[i] = float(fft_values[i])

    def _animate(self):
        for i in range(self.bars):
            self.values[i] += (self.target[i] - self.values[i]) * 0.25
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        bar_width = 6
        spacing = 4

        for i, v in enumerate(self.values):
            bar_h = v * h
            x = i * (bar_width + spacing)
            y = h - bar_h
            painter.fillRect(QRectF(x, y, bar_width, bar_h), QColor(self.COLOR))
