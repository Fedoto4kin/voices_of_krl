import os

from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QTextBrowser, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
from src.ui.info.touch_dot import TouchDot
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtGui import QBrush, QColor, QPen

from PySide6.QtGui import QPainter
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen
from PySide6.QtWidgets import QLabel

from PySide6.QtGui import QPixmap, QPainter, QColor, QPen
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

def make_mini_marker(active=False, radius=32):
    size = radius + 12  # запас под glow

    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)

    # Цвета как в Marker
    active_color = QColor("#a44546")
    inactive_color = active_color.darker(130)

    color = active_color if active else inactive_color

    # --- Glow для активного маркера ---
    if active:
        for i in range(1, 5):
            alpha = 40 - i * 8
            painter.setPen(QPen(QColor(255, 255, 255, alpha), 2 * i))
            painter.drawEllipse(
                (size - radius) // 2 - i,
                (size - radius) // 2 - i,
                radius + 2 * i,
                radius + 2 * i
            )

    # --- Сам маркер ---
    painter.setBrush(color)
    painter.setPen(QPen(Qt.black, 1))
    painter.drawEllipse(
        (size - radius) // 2,
        (size - radius) // 2,
        radius,
        radius
    )

    painter.end()

    label = QLabel()
    label.setPixmap(pix)
    label.setFixedSize(size, size)
    label.setStyleSheet("background: transparent;")

    return label

class InfoOverlay(QWidget):
    def __init__(self, parent, project_root):
        super().__init__(parent)
        self.touch_dot = None
        self.cta_label = None
        self.card_layout = None
        self.card = None
        self.project_root = project_root
        self.build_ui()
        self.card.installEventFilter(self)

    # todo: split method
    def build_ui(self):
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 40, 0, 40)
        # --- Карточка ---
        self.card = QFrame()
        self.card.setObjectName("infoCard")
        self.setStyleSheet("background-color: rgba(0, 0, 0, 128);")
        self.card.setStyleSheet("""
            #infoCard {
                background: rgba(43, 43, 43, 191);
                color: white;
                border-radius: 20px;
                border: 2px solid rgba(240, 240, 240, 180);
            }
            QLabel {
                background: transparent;
            }
        """)
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(30, 30, 30, 30)
        self.card_layout.setSpacing(10)

        # --- Заголовок ---
        title = QLabel("Голоса Тверской Карелии")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: 700;
            color: white;
            margin-bottom: 18px;
        """)
        self.card_layout.addWidget(title)
        intro = QLabel(
            "Перед вами интерактивная карта Тверской области — пространство, "
            "где звучит живая карельская речь."
        )
        intro.setWordWrap(True)
        intro.setAlignment(Qt.AlignCenter)
        intro.setStyleSheet("""
            font-size: 20px;
            line-height: 150%;
            color: white;
            margin-bottom: 12px;
        """)
        self.card_layout.addWidget(intro)

        # --- Карточка действия: Наденьте наушники ---
        headphones_card = QFrame()
        headphones_card.setObjectName("actionCard")
        headphones_card.setStyleSheet("""
            #actionCard {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 14px;
            }
        """)
        row = QHBoxLayout(headphones_card)
        row.setContentsMargins(20, 20, 20, 20)
        row.setSpacing(16)
        # SVG‑иконка наушников
        icon = QSvgWidget(os.path.join(self.project_root, "assets", "info", "headphones.svg"))
        icon.setFixedSize(36, 36)
        icon.setStyleSheet("background: transparent;")
        row.addWidget(icon, alignment=Qt.AlignCenter)
        # Текст
        text = QLabel("Наденьте наушники")
        text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        text.setWordWrap(True)
        text.setStyleSheet("""
            font-size: 19px;
            font-weight: 600;
            color: white;
        """)
        row.addWidget(text, stretch=1)

        self.card_layout.addWidget(headphones_card)

        # --- Карточка действия: Перемещайтесь по карте ---
        gestures_card = QFrame()
        gestures_card.setObjectName("actionCard")
        gestures_card.setStyleSheet("""
            #actionCard {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 14px;
            }
        """)

        outer = QVBoxLayout(gestures_card)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(20)

        # --- Заголовок в одну строку (иконка + текст) ---
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        # SVG иконка точки карты
        icon2 = QSvgWidget(os.path.join(self.project_root, "assets", "map", "point.svg"))
        icon2.setFixedSize(36, 36)   # масштаб под размер текста
        icon2.setStyleSheet("background: transparent;")
        row2.addWidget(icon2, alignment=Qt.AlignCenter)

        text2 = QLabel("Перемещайтесь по карте, используя жесты")
        text2.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        text2.setWordWrap(True)
        text2.setStyleSheet("""
            font-size: 19px;
            font-weight: 600;
            color: white;
        """)
        row2.addWidget(text2, stretch=1)

        outer.addLayout(row2)

        icons_row = QHBoxLayout()
        icons_row.setSpacing(52)

        def make_gesture_column(svg_name: str, caption: str) -> QWidget:
            w = QWidget()
            w.setStyleSheet("background: transparent;")   # ← убираем фон
            col = QVBoxLayout(w)
            col.setSpacing(6)

            icon = QSvgWidget(os.path.join(self.project_root, "assets", "info", svg_name))
            icon.setFixedSize(64, 64)
            icon.setStyleSheet("background: transparent;")  # ← убираем фон
            col.addWidget(icon, alignment=Qt.AlignCenter)

            lbl = QLabel(caption)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("""
                font-size: 16px;
                color: white;
                background: transparent;
            """)
            col.addWidget(lbl)

            return w

        icons_row.addWidget(make_gesture_column("one-finger-move.svg", "Перемещение"))
        icons_row.addWidget(make_gesture_column("pinch_close.svg", "Приближение"))
        icons_row.addWidget(make_gesture_column("pinch_open.svg", "Отдаление"))

        icons_row.addStretch(1)
        outer.addLayout(icons_row)
        self.card_layout.addWidget(gestures_card)


        # --- Карточка действия: Выбирайте точку на карте ---
        select_card = QFrame()
        select_card.setObjectName("actionCard")
        select_card.setStyleSheet("""
            #actionCard {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 14px;
            }
        """)
        
        outer = QVBoxLayout(select_card)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(20)
        
        # --- Заголовок (мини‑маркер + текст) ---
        row = QHBoxLayout()
        row.setSpacing(16)
        
        marker_icon = make_mini_marker()
        row.addWidget(marker_icon, alignment=Qt.AlignCenter)
        
        title = QLabel("Выбирайте точку на карте")
        title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        title.setWordWrap(True)
        title.setStyleSheet("""
            font-size: 19px;
            font-weight: 600;
            color: white;
        """)
        row.addWidget(title, stretch=1)
        
        outer.addLayout(row)
        
        # --- Ряд жестов (двойной тап + удержание) ---
        gestures_row = QHBoxLayout()
        gestures_row.setSpacing(48)
        
        def make_gesture_column(svg_name: str, caption: str) -> QWidget:
            w = QWidget()
            w.setStyleSheet("background: transparent;")
            col = QVBoxLayout(w)
            col.setSpacing(6)
        
            icon = QSvgWidget(os.path.join(self.project_root, "assets", "info", svg_name))
            icon.setFixedSize(64, 64)
            icon.setStyleSheet("background: transparent;")
            col.addWidget(icon, alignment=Qt.AlignCenter)
        
            lbl = QLabel(caption)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 16px; color: white;")
            col.addWidget(lbl)

            return w

        gestures_row.addWidget(make_gesture_column("one_finger_double_touch.svg", "Двойное касание"))
        gestures_row.addWidget(make_gesture_column("one_finger_hold.svg", "Удержание"))
        gestures_row.addStretch(1)

        outer.addLayout(gestures_row)
        self.card_layout.addWidget(select_card)

        # --- Карточка действия: Откроется проигрыватель ---
        player_card = QFrame()
        player_card.setObjectName("actionCard")
        player_card.setStyleSheet("""
            #actionCard {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 14px;
            }
        """)

        row = QHBoxLayout(player_card)
        row.setContentsMargins(20, 20, 20, 20)
        row.setSpacing(16)

        # Активный мини‑маркер
        icon = make_mini_marker(active=True, radius=32)
        row.addWidget(icon, alignment=Qt.AlignCenter)

        text = QLabel("Откроется проигрыватель и автоматически начнёт воспроизведение")
        text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        text.setWordWrap(True)
        text.setStyleSheet("""
            font-size: 19px;
            font-weight: 600;
            color: white;
        """)
        row.addWidget(text, stretch=1)

        self.card_layout.addWidget(player_card)

        footer_row = QHBoxLayout()
        footer_row.setSpacing(24)

        # --- Пустое пространство ---
        empty = QWidget()
        empty.setFixedSize(64, 64)
        empty.setStyleSheet("background: transparent;")
        footer_row.addWidget(empty, alignment=Qt.AlignCenter)

        # --- TouchDot ---
        self.touch_dot = TouchDot(size=14)
        self.touch_dot.clicked.connect(self.hide)
        footer_row.addWidget(self.touch_dot, alignment=Qt.AlignCenter)

        # --- Лого ---
        logo = QLabel()
        pix = QPixmap(os.path.join(self.project_root, "assets", "info", "vepkar_logo.png"))
        pix = pix.scaledToHeight(36, Qt.SmoothTransformation)
        logo.setPixmap(pix)

        # --- QR ---
        qr = QSvgWidget(os.path.join(self.project_root, "assets", "info", "dictorpus.qr.svg"))
        qr.setFixedSize(64, 64)

        logo_column = QWidget()
        logo_column.setStyleSheet("background: transparent;")

        col_layout = QVBoxLayout(logo_column)
        col_layout.setContentsMargins(0, 0, 0, 0)
        col_layout.setSpacing(6)

        col_layout.addStretch(1)
        col_layout.addWidget(logo, alignment=Qt.AlignCenter)
        col_layout.addWidget(qr, alignment=Qt.AlignCenter)

        footer_row.addWidget(logo_column, alignment=Qt.AlignRight)

        self.card_layout.addLayout(footer_row)

        # --- Source текст ---
        self.cta_label = QLabel("Карта подготовлена на основе материалов <b>Открытого корпуса вепсского и карельского языков</b>")
        self.cta_label.setAlignment(Qt.AlignCenter)
        self.cta_label.setStyleSheet("""
            font-family: 'Courier New', monospace;
            font-size: 18px;
            color: rgba(255, 255, 255, 0.75);
            background: transparent;
        """)
        self.card_layout.addWidget(self.cta_label)

        # Записи (с) Antonovka Records. (лого) "По-карельски понимаю. Музыка тверских карел"

        layout.addWidget(self.card, alignment=Qt.AlignHCenter)
        self.update_card_size()

    def update_card_size(self):
        """Устанавливает ширину карточки = 85% ширины окна."""
        if not self.parent():
            return

        parent_w = self.parent().width()
        parent_h = self.parent().height()

        target_w = int(parent_w * 0.65)
        max_w = 1500
        self.card.setMinimumWidth(min(target_w, max_w))
        self.card.setMaximumWidth(min(target_w, max_w))
        self.card.setMinimumHeight(int(parent_h * 0.80))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_card_size()
