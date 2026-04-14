import json
import os

from PySide6.QtCore import QTimer, Qt, QEvent
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from src.ui.player.audio_player_widget import AudioPlayerWidget
from src.ui.map.map_view import MapView
from src.ui.intro.intro_screen_widget import IntroScreenWidget
from src.ui.info.info_overlay import InfoOverlay
from PySide6.QtDBus import QDBusConnection, QDBusMessage


class MainWindow(QMainWindow):

    IDLE_TIMEOUT_MINUTES = 5

    def __init__(self, project_root):
        super().__init__()

        self.project_root = project_root
        self.setWindowTitle("Голоса Тверской Карелии")
        icon_path = os.path.join(self.project_root, "assets", "map", "point.svg")
        self.setWindowIcon(QIcon(icon_path))

        self.setCursor(Qt.BlankCursor)
        self._inhibit_cookie = None
        self.inhibit_sleep()

        # --- STACKED WIDGET ---
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        # --- Intro screen ---
        self.intro = IntroScreenWidget(self.project_root)
        self.intro.startRequested.connect(self.show_map_scene)

        # --- MapView ---
        svg_path = os.path.join(project_root, "assets", "map", "tver_region.svg")
        self.view = MapView(svg_path, self.project_root)
        self.view.pointSelected.connect(self.on_point_selected)

        # --- Overlay ---
        self.info_overlay = InfoOverlay(self, self.project_root)
        self.info_overlay.hide()
        self.info_overlay.setGeometry(self.rect())

        # Добавляем экраны в стек
        self.stack.addWidget(self.intro)   # index 0
        self.stack.addWidget(self.view)    # index 1

        # --- Idle timer ---
        self.idle_timer = QTimer(self)
        self.idle_timer.setInterval(self.IDLE_TIMEOUT_MINUTES * 60 * 1000)
        self.idle_timer.timeout.connect(self.on_idle_timeout)
        self.idle_timer.start()
        self.installEventFilter(self)
        self.stack.setCurrentWidget(self.intro)

        # --- Load points ---
        QTimer.singleShot(0, self.view.initial_fit)
        QTimer.singleShot(0, lambda: self.view.load_markers(self.load_points_json()))
        self.active_marker = None

        # --- Audio player ---
        self.player = AudioPlayerWidget(self.project_root)
        self.player.setParent(self)
        self.player.hide()
        self.view.set_audio_player_widget(self.player)
        self.player.closed.connect(self.on_player_closed)
        self.player.userActivity.connect(self.on_user_activity)
        self.player.playingStarted.connect(self.on_audio_playing)
        self.player.playingStopped.connect(self.on_audio_stopped)
        self.audio_is_playing = False
        # Position player
        w = self.width()
        h = self.height()
        margin_x = int(w * 0.1)
        margin_y = int(h * 0.1)
        self.player.move(margin_x, margin_y)
        self.player.raise_()

        # Idle integration
        self.player.userActivity.connect(self.on_user_activity)

    # ---------------------------------------------------------
    # SCREEN SWITCHING
    # ---------------------------------------------------------

    def show_map_scene(self):
        self.stack.setCurrentWidget(self.view)
        self.player.raise_()
        self.info_overlay.show()
        self.info_overlay.raise_()

    # ---------------------------------------------------------
    # IDLE TIMER
    # ---------------------------------------------------------

    def reset_idle_timer(self):
        if not self.audio_is_playing:
            self.idle_timer.start()

    def on_idle_timeout(self):
        # Остановить аудио
        self.player.stop()
        self.player.hide()
        self.view.marker_manager.deactivate_all()
        self.active_marker = None
        self.stack.setCurrentWidget(self.intro)
        self.info_overlay.hide()

    def on_user_activity(self):
        if not self.audio_is_playing:
            self.reset_idle_timer()

    # ---------------------------------------------------------
    # EVENT FILTER
    # ---------------------------------------------------------

    def eventFilter(self, obj, event):
        et = event.type()

        if et in (
            QEvent.MouseButtonPress,
            QEvent.MouseButtonRelease,
            QEvent.TouchBegin,
            QEvent.TouchUpdate,
            QEvent.TouchEnd,
            QEvent.Gesture,
            QEvent.GestureOverride,
            QEvent.Wheel,
            QEvent.KeyPress,
            QEvent.KeyRelease,
        ):
             if not self.audio_is_playing:
                self.reset_idle_timer()

        return super().eventFilter(obj, event)

    # ---------------------------------------------------------
    # RESIZE
    # ---------------------------------------------------------

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "player"):
            w = self.width()
            h = self.height()
            margin_x = int(w * 0.03)
            margin_y = int(h * 0.05)
            player_width = int(w * 0.36)
            self.player.setFixedWidth(player_width)
            available_height = h - margin_y - 20
            self.player.setMaximumHeight(available_height)
            self.player.adjustSize()
            self.player.move(margin_x, margin_y)
        if hasattr(self, "info_overlay"):
            self.info_overlay.setGeometry(self.rect())

    # ---------------------------------------------------------
    # DATA
    # ---------------------------------------------------------

    def load_points_json(self):
        json_path = os.path.join(
            self.project_root,
            "assets",
            "data",
            "points.json"
        )
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def init_markers(self):
        self.view.load_markers(self.points)

    # ---------------------------------------------------------
    # MAP INTERACTION
    # ---------------------------------------------------------

    def on_point_selected(self, data):
        clicked_marker = None
        for m in self.view.markers:
            if m.name == data["name_ru"]:
                clicked_marker = m
                break

        if clicked_marker is None:
            return

        if self.active_marker and self.active_marker is not clicked_marker:
            self.active_marker.resetState()

        clicked_marker.setActive()
        self.active_marker = clicked_marker

        for m in self.view.markers:
            if m is not clicked_marker:
                m.setInactive()

        if data.get("audio"):
            self.player.show()
            self.player.set_title(data["name_ru"])
            self.player.load_audio_list(data["audio"])
            self.player.raise_()

    # ---------------------------------------------------------
    # AUDIO PLAYER
    # ---------------------------------------------------------

    def on_player_closed(self):
        self.player.stop()
        if self.active_marker:
            self.active_marker.resetState()
            self.active_marker = None
        for m in self.view.markers:
            m.setInactive()

    def on_audio_playing(self):
        self.audio_is_playing = True
        self.idle_timer.stop()

    def on_audio_stopped(self):
        self.audio_is_playing = False
        self.reset_idle_timer()

    # ---------------------------------------------------------
    # SYSTEM SLEEP INHIBIT
    # ---------------------------------------------------------

    def inhibit_sleep(self):
        msg = QDBusMessage.createMethodCall(
            "org.freedesktop.ScreenSaver",
            "/org/freedesktop/ScreenSaver",
            "org.freedesktop.ScreenSaver",
            "Inhibit"
        )
        msg.setArguments(["KRL-Kiosk", "Kiosk mode active"])
        reply = QDBusConnection.sessionBus().call(msg)

        if reply.type() == QDBusMessage.ReplyMessage:
            self._inhibit_cookie = reply.arguments()[0]
            print("Sleep/screensaver inhibited:", self._inhibit_cookie)
        else:
            print("Failed to inhibit screensaver")

    def uninhibit_sleep(self):
        if self._inhibit_cookie is None:
            return

        msg = QDBusMessage.createMethodCall(
            "org.freedesktop.ScreenSaver",
            "/org/freedesktop/ScreenSaver",
            "org.freedesktop.ScreenSaver",
            "UnInhibit"
        )
        msg.setArguments([self._inhibit_cookie])
        QDBusConnection.sessionBus().call(msg)
