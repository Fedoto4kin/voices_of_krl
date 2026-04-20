from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal
import random

from src.ui.player.spotify_bars_widget import SpotifyBarsWidget


class TrackRow(QWidget):
    playRequested = Signal(int)
    pauseRequested = Signal(int)

    COLOR_NORMAL = "#6d2324"
    COLOR_PRESSED = "#a44546"
    BTN_STYLE_TEMPLATE = """
        QPushButton {{
            font-size: 24px;
            border-radius: 10px;
            background: {bg};
            color: white;
            border: 2px solid rgba(0,0,0,0);
        }}
        QPushButton:pressed {{
            background: {pressed};
        }}
    """

    def __init__(self, index, title):
        super().__init__()
        self.index = index
        self.is_playing = False
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.btn = QPushButton("▶")
        self.btn.setFixedSize(62, 62)
        self.btn.setStyleSheet(
            self.BTN_STYLE_TEMPLATE.format(
                bg=self.COLOR_NORMAL,
                pressed=self.COLOR_PRESSED
            )
        )

        self.btn.clicked.connect(self.toggle)
        self.label = QLabel(title)
        self.label.setStyleSheet("font-size: 22px;")
        self.wave = SpotifyBarsWidget(bars=10)
        self.wave.setFixedHeight(40)
        layout.addWidget(self.wave)

        layout.addWidget(self.btn)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.wave)

    # ----------------------------------------------------

    def toggle(self):
        if self.is_playing:
            self.pauseRequested.emit(self.index)
        else:
            self.playRequested.emit(self.index)

    # ----------------------------------------------------

    def setPlaying(self, playing):
        self.is_playing = playing
        self.btn.setText("◼" if playing else "▶")

        if playing:
            # активная кнопка = цвет pressed
            self.btn.setStyleSheet(
                self.BTN_STYLE_TEMPLATE.format(
                    bg=self.COLOR_PRESSED,
                    pressed=self.COLOR_PRESSED
                )
            )
            self.wave.show()
        else:
            # обычная кнопка
            self.btn.setStyleSheet(
                self.BTN_STYLE_TEMPLATE.format(
                    bg=self.COLOR_NORMAL,
                    pressed=self.COLOR_PRESSED
                )
            )
            self.wave.hide()


    # ----------------------------------------------------

    def _fade_in(self):
        self.fade_anim.stop()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

    def _fade_out(self):
        self.fade_anim.stop()
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.start()

    def update_fft(self, rms, fft):
        self.wave.update_real_values(fft)
