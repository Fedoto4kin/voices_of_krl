import os

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt, QEasingCurve
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtCore import QPropertyAnimation

from src.ui.intro.background_layer import BackgroundLayer


class IntroScreenWidget(QWidget):
    startRequested = Signal()

    def __init__(self, project_root, parent=None):
        super().__init__(parent)

        self.project_root = project_root

        self.setObjectName("IntroScreenWidget")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            #IntroScreenWidget {
                background-color: black;
            }
            QLabel {
                color: white;
            }
        """)

        # --- 1. layout ---
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)

        # --- 2. Text ---
        self.title = QLabel("TVERIN KARIELAN IÄNET")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 46px; font-weight: 600;")

        self.title_ru = QLabel("(Голоса Тверской Карелии)")
        self.title_ru.setAlignment(Qt.AlignCenter)
        self.title_ru.setStyleSheet("""
            font-size: 22px;
            font-style: italic;
            color: #bbbbbb;
        """)

        self.subtitle = QLabel("Коснитесь экрана чтобы услышать карельскую речь")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("font-size: 24px;")

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.title_ru)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.subtitle)

        # --- 3. SVG-icon ---
        icon_path = os.path.join(self.project_root, "assets", "map", "point.svg")
        self.icon = QSvgWidget(icon_path, self)
        self.icon.setFixedSize(68, 68)
        self.layout.addSpacing(16)
        self.layout.addWidget(self.icon, alignment=Qt.AlignCenter)
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(0)
        glow.setOffset(0, 0)
        glow.setColor(Qt.white)
        self.icon.setGraphicsEffect(glow)
        from PySide6.QtGui import QColor
        glow.setColor(QColor(255, 255, 255, 200))
        self.glow_in = QPropertyAnimation(glow, b"blurRadius")
        self.glow_in.setStartValue(2)
        self.glow_in.setEndValue(55)   # шире, чем 42
        self.glow_in.setDuration(2200)
        self.glow_in.setEasingCurve(QEasingCurve.InOutQuad)
        self.glow_out = QPropertyAnimation(glow, b"blurRadius")
        self.glow_out.setStartValue(55)
        self.glow_out.setEndValue(2)
        self.glow_out.setDuration(2200)
        self.glow_out.setEasingCurve(QEasingCurve.InOutQuad)

        self.glow_in.finished.connect(self.glow_out.start)
        self.glow_out.finished.connect(self.glow_in.start)

        self.glow_in.start()

        self.bg = BackgroundLayer(project_root=project_root, parent=self)
        self.bg.lower()
        self.bg.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg.resize(self.size())

        title_rect = self.title.geometry()
        title_ru_rect = self.title_ru.geometry()
        subtitle_rect = self.subtitle.geometry()
        icon_rect = self.icon.geometry()

        forbidden = (
            title_rect
            .united(title_ru_rect)
            .united(subtitle_rect)
            .united(icon_rect)
        )

        self.bg.set_forbidden_rect(forbidden)

    def mousePressEvent(self, event):
        self.startRequested.emit()
        super().mousePressEvent(event)
