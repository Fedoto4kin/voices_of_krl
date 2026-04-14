from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, Signal


class TouchDot(QWidget):

    clicked = Signal()

    def __init__(self, size=6, color=QColor("#a44546"), parent=None):
        super().__init__(parent)

        self._progress = 0.0
        self.dot_size = size
        self.color = color

        # Максимальный радиус волны
        self.max_radius = size * 6

        # Увеличенная область отрисовки
        self.setFixedSize(self.max_radius * 2, self.max_radius * 2)

        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        # Анимация ripple
        self.anim = QPropertyAnimation(self, b"progress")
        self.anim.setDuration(1500)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setLoopCount(-1)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()

    # --- Свойство progress (0 → 1) ---
    def getProgress(self):
        return self._progress

    def setProgress(self, value):
        self._progress = value
        self.update()

    progress = Property(float, getProgress, setProgress)

    # --- Рисование ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = self.rect().center()

        # 1. Центральная точка
        painter.setBrush(self.color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, self.dot_size, self.dot_size)

        # 2. Расширяющееся кольцо
        radius = self.max_radius * self._progress
        opacity = 1.0 - self._progress  # исчезает к краю

        painter.setOpacity(opacity)

        pen = QPen(self.color)
        pen.setWidth(3)  # толщина кольца
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        painter.drawEllipse(center, radius, radius)

    def mousePressEvent(self, event):
        self.clicked.emit()
