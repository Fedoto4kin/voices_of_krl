import os

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QPinchGesture, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtSvgWidgets import QGraphicsSvgItem, QSvgWidget
from PySide6.QtGui import QPainter, QColor, QPixmap
from PySide6.QtCore import Qt, QEvent, Signal, QTimer

from src.ui.map.managers.marker_manager import MarkerManager
from src.ui.map.controllers.audio_controller import AudioController
from src.ui.map.marker.simple_marker import Marker


class MapView(QGraphicsView):

    pointSelected = Signal(object)

    def __init__(self, svg_path, project_root):
        super().__init__()

        self.project_root = project_root
        self.viewport().setCursor(Qt.BlankCursor)

        self.viewport().setCursor(Qt.BlankCursor)
        self.viewport().installEventFilter(self)
        self._cursor_timer = QTimer(self)
        self._cursor_timer.timeout.connect(lambda: self.viewport().setCursor(Qt.BlankCursor))
        self._cursor_timer.start(30)

        self.viewport().installEventFilter(self)

        # -----------------------------
        #  SCENE + SVG MAP
        # -----------------------------
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.svg_item = QGraphicsSvgItem(svg_path)
        self.scene.addItem(self.svg_item)

        # -----------------------------
        #  MANAGERS
        # -----------------------------
        self.marker_manager = MarkerManager(self.scene)
        self.audio_controller = AudioController(self.project_root)

        # Connect managers
        self.marker_manager.markerActivated.connect(self._on_marker_activated)
        self.audio_controller.playbackFinished.connect(self.marker_manager.deactivate_all)

        # -----------------------------
        #  VIEW CONFIG
        # -----------------------------
        self.setBackgroundBrush(QColor("#3d3d3d"))
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAttribute(Qt.WA_AcceptTouchEvents, True)

        self.min_scale = None
        self.max_scale = 4.2

        self.grabGesture(Qt.PinchGesture)
        self.grabGesture(Qt.TapAndHoldGesture)

    # -----------------------------
    #  PUBLIC API
    # -----------------------------
    def load_markers(self, points):
        self.marker_manager.load_markers(points)

    def set_audio_player_widget(self, widget):
        self.audio_controller.set_player(widget)

    # -----------------------------
    #  MANAGER CALLBACK
    # -----------------------------
    def _on_marker_activated(self, data):
        """Called when MarkerManager activates a marker."""
        self.audio_controller.play_for_marker(data)
        self.pointSelected.emit(data)

    # -----------------------------
    #  GESTURES
    # -----------------------------
    def event(self, event):
        if event.type() == QEvent.Gesture:
            return self.gestureEvent(event)
        return super().event(event)

    def eventFilter(self, obj, event):
        if obj is self.viewport():
            et = event.type()
            if et in (
                QEvent.MouseButtonPress,
                QEvent.MouseButtonRelease,
                QEvent.HoverMove,
                QEvent.HoverEnter,
                QEvent.HoverLeave,
                QEvent.TouchBegin,
                QEvent.TouchUpdate,
                QEvent.TouchEnd,
                QEvent.Gesture,
                QEvent.GestureOverride,
                QEvent.Wheel,
            ):
                self.viewport().setCursor(Qt.BlankCursor)
                return False
        return super().eventFilter(obj, event)


    def gestureEvent(self, event):
        tap_hold = event.gesture(Qt.TapAndHoldGesture)
        if tap_hold:
            self.handleTapAndHold(tap_hold)

        pinch = event.gesture(Qt.PinchGesture)
        if pinch:
            self.handlePinch(pinch)

        return True

    def handleTapAndHold(self, gesture):
        if gesture.state() != Qt.GestureFinished:
            return

        global_pos = gesture.hotSpot().toPoint()
        view_pos = self.mapFromGlobal(global_pos)
        scene_pos = self.mapToScene(view_pos)

        for item in self.scene.items(scene_pos):
            if isinstance(item, Marker):
                item.signals.longHold.emit(item.data)
                break

    # -----------------------------
    #  ZOOM
    # -----------------------------
    def initial_fit(self):
        self.fitInView(self.svg_item, Qt.KeepAspectRatio)
        self.min_scale = self.transform().m11()

    def wheelEvent(self, event):
        zoom_in = 1.15
        zoom_out = 1 / zoom_in
        current = self.transform().m11()

        if event.angleDelta().y() > 0:
            if current < self.max_scale:
                self.scale(zoom_in, zoom_in)
        else:
            if current > self.min_scale:
                self.scale(zoom_out, zoom_out)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self.min_scale is None:
            return

        current_center = self.mapToScene(self.viewport().rect().center())
        current_scale = self.transform().m11()

        old_transform = self.transform()
        self.fitInView(self.svg_item, Qt.KeepAspectRatio)
        new_min_scale = self.transform().m11()
        self.setTransform(old_transform)

        self.min_scale = new_min_scale

        if current_scale < self.min_scale:
            self.fitInView(self.svg_item, Qt.KeepAspectRatio)
        else:
            self.centerOn(current_center)

    def handlePinch(self, pinch):
        if pinch.changeFlags() & QPinchGesture.ChangeFlags.ScaleFactorChanged:
            scale_factor = pinch.scaleFactor()

            current_scale = self.transform().m11()
            new_scale = current_scale * scale_factor

            if self.min_scale is not None:
                if new_scale < self.min_scale:
                    scale_factor = self.min_scale / current_scale
                elif new_scale > self.max_scale:
                    scale_factor = self.max_scale / current_scale

            self.scale(scale_factor, scale_factor)
