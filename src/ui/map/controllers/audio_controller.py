from PySide6.QtCore import QObject, Signal


class AudioController(QObject):
    playbackFinished = Signal()

    def __init__(self, project_root):
        super().__init__()
        self.player_widget = None
        self.project_root = project_root
        self.current_data = None

    def set_player(self, widget):
        """Attach the AudioPlayerWidget."""
        self.player_widget = widget

        # конец трека
        if hasattr(widget.player, "mediaStatusChanged"):
            widget.player.mediaStatusChanged.connect(self._on_media_status)

        # ручное закрытие плеера (крестик)
        if hasattr(widget, "closed"):
            widget.closed.connect(self._on_closed)

    def play_for_marker(self, data):
        if not self.player_widget:
            return
        if self.current_data is data:
            return

        self.current_data = data

        audio_list = data.get("audio", [])
        if not audio_list:
            return

        name_ru = data.get("name_ru", "")
        name_krl = data.get("name_krl", "")

        if name_krl:
            title = f"{name_krl} ({name_ru})"
        else:
            title = name_ru

        self.player_widget.set_title(title)
        self.player_widget.load_audio_list(audio_list)
        self.player_widget.show()

    def stop(self):
        if self.player_widget:
            self.player_widget.stop()
        self.current_data = None

    def _on_media_status(self, status):
        # QMediaPlayer.EndOfMedia = 7
        if status == 7:
            self.current_data = None
            self.playbackFinished.emit()

    def _on_closed(self):
        # пользователь закрыл плеер вручную
        self.stop()
        self.playbackFinished.emit()
