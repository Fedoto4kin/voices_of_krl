from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, Signal, QTimer

import os

from src.utilites.audio.audio_analyzer import AudioAnalyzer
from .track_row import TrackRow


class AudioPlayerWidget(QFrame):

    closed = Signal()
    userActivity = Signal()
    playingStarted = Signal()
    playingStopped = Signal()


    def __init__(self, project_root):
        super().__init__()

        self.project_root = project_root
        self.setObjectName("audioPlayer")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)

        # --- Header ---
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel("Фрагменты речи")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(62, 62)
        self.btn_close.setStyleSheet("""
            QPushButton {
                font-size: 28px;
                border-radius: 10px;
                background-color: black;
                color: white;
            }
            QPushButton:pressed {
                background: #0c0c0c;
            }
        """)
        self.btn_close.clicked.connect(self._on_close)

        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.btn_close)

        self.layout.addLayout(header)

        self.setStyleSheet("""
            #audioPlayer {
                background: #2b2b2b;
                color: white;
                border-radius: 20px;
                border: 2px solid #f0f0f0;
            }
        """)

        # --- Audio engine ---
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        # Автопереход + idle‑сброс при PlayingState
        self.player.mediaStatusChanged.connect(self._on_media_status)
        self.player.playbackStateChanged.connect(self._on_state_changed)

        self.analyzer = None

        self.rows = []
        self.audio_list = []
        self.current_index = -1

    # ----------------------------------------------------
    # Загрузка списка треков
    # ----------------------------------------------------

    def load_audio_list(self, audio_list):
        for row in self.rows:
            row.setParent(None)

        self.rows = []
        self.audio_list = audio_list

        for i, entry in enumerate(audio_list):
            row = TrackRow(i, entry["title"])
            row.playRequested.connect(self.play_track)
            row.pauseRequested.connect(self.pause_track)
            self.rows.append(row)
            self.layout.addWidget(row)

        header_h = 60
        row_h = 100
        margin = 30
        natural_h = header_h + len(self.rows) * row_h + margin
        self.setFixedHeight(natural_h)

        if audio_list:
            self.play_track(0)

    def set_title(self, title):
        self.title_label.setText(title)

    # ----------------------------------------------------
    # Управление треками
    # ----------------------------------------------------

    def play_track(self, index):
        self.userActivity.emit()   # ← пользователь нажал play

        if index < 0 or index >= len(self.audio_list):
            return

        self.current_index = index
        entry = self.audio_list[index]
        audio_path = os.path.join(self.project_root, "assets", "data", "audio", entry["file"])

        # Анализатор
        self.analyzer = AudioAnalyzer(
            audio_path,
            callback=lambda rms, fft: self.rows[index].update_fft(rms, fft),
            bars=10
        )
        self.analyzer.start()

        self.player.setSource(QUrl.fromLocalFile(audio_path))
        self.player.play()

        for i, row in enumerate(self.rows):
            row.setPlaying(i == index)

    def pause_track(self, index):
        self.userActivity.emit()   # ← пользователь нажал pause

        if index == self.current_index:
            self.player.pause()
            if 0 <= index < len(self.rows):
                self.rows[index].setPlaying(False)

    # ----------------------------------------------------
    # Автопереход между треками
    # ----------------------------------------------------

    def _on_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            next_index = self.current_index + 1

            if next_index < len(self.audio_list):
                idx = next_index
                QTimer.singleShot(1600, lambda i=idx: self._play_if_still_valid(i))
            else:
                if 0 <= self.current_index < len(self.rows):
                    self.rows[self.current_index].setPlaying(False)
                self.player.stop()
                self.current_index = -1

    def _play_if_still_valid(self, index):
        if self.current_index == -1:
            return
        if index != self.current_index + 1:
            return
        if index >= len(self.audio_list):
            return

        # Автопереход НЕ является пользовательским действием
        # idle сбросится автоматически через PlayingState
        self.play_track(index)

    # ----------------------------------------------------
    # Idle‑интеграция: сброс таймера, пока аудио играет
    # ----------------------------------------------------

    def _on_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self.playingStarted.emit()
        else:
            self.playingStopped.emit()



    # ----------------------------------------------------
    # Закрытие плеера
    # ----------------------------------------------------

    def _on_close(self):
        self.userActivity.emit()   # ← пользователь закрыл плеер
        self.stop()
        self.hide()
        self.closed.emit()

    # ----------------------------------------------------
    # Остановка
    # ----------------------------------------------------

    def stop(self):
        self.player.stop()
        if hasattr(self, "analyzer") and self.analyzer:
            self.analyzer.stop()

        for row in self.rows:
            row.setPlaying(False)

        self.current_index = -1
