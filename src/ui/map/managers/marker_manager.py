from PySide6.QtCore import QObject, Signal
from src.ui.map.marker.simple_marker import Marker


class MarkerManager(QObject):
    markerActivated = Signal(object)   # emits marker.data

    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.markers = []
        self.active_marker = None

    # -----------------------------
    #  MARKER CREATION
    # -----------------------------
    def load_markers(self, points):
        """Create markers from JSON and add them to the scene."""
        for p in points:
            marker = Marker(data=p, radius=62)
            marker.signals.clicked.connect(self._on_marker_clicked)
            marker.signals.longHold.connect(self._on_marker_long_hold)

            self.scene.addItem(marker)
            self.markers.append(marker)

    # -----------------------------
    #  MARKER ACTIVATION LOGIC
    # -----------------------------
    def activate_marker(self, marker):
        """Activate a marker and deactivate the previous one."""
        if self.active_marker is marker:
            return

        if self.active_marker:
            self.active_marker.setInactive()

        marker.setActive()
        self.active_marker = marker

        # Emit data for external systems (audio, UI, etc.)
        self.markerActivated.emit(marker.data)

    def activate_by_data(self, data):
        """Find marker by its data and activate it."""
        marker = self._find_marker_by_data(data)
        if marker:
            self.activate_marker(marker)

    def deactivate_all(self):
        """Reset all markers (e.g., when audio stops)."""
        if self.active_marker:
            self.active_marker.setInactive()
            self.active_marker = None

    # -----------------------------
    #  INTERNAL SIGNAL HANDLERS
    # -----------------------------
    def _on_marker_clicked(self, data):
        self.activate_by_data(data)

    def _on_marker_long_hold(self, data):
        self.activate_by_data(data)

    # -----------------------------
    #  UTILITIES
    # -----------------------------
    def _find_marker_by_data(self, data):
        for m in self.markers:
            if m.data is data:
                return m
        return None
