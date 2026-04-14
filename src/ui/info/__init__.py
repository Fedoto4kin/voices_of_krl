from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

class InfoOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Полупрозрачный фон
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")

        # Основной контейнер
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Карточка (как плеер, но большая)
        self.card = QFrame()
        self.card.setObjectName("infoCard")
        self.card.setStyleSheet("""
            #infoCard {
                background: #2b2b2b;
                color: white;
                border-radius: 20px;
                border: 2px solid #f0f0f0;
            }
        """)

        # Внутренний текст-заглушка
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)

        self.label = QLabel("Здесь будет информация о проекте, жестах и источниках данных.")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px;")

        card_layout.addWidget(self.label)

        layout.addWidget(self.card)

    # Закрытие при любом касании
    def mousePressEvent(self, event):
        self.hide()

    def mouseMoveEvent(self, event):
        self.hide()

    def mouseReleaseEvent(self, event):
        self.hide()
