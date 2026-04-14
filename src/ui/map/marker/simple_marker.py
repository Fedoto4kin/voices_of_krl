from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QGraphicsDropShadowEffect
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtCore import Qt, QObject

from src.ui.map.marker.marker_signal import MarkerSignals


class Marker(QGraphicsEllipseItem, QObject):
    ACTIVE_COLOR = QColor("#a44546")

    def __init__(self, data, radius=62, **kwargs):
        """
        point_data — from JSON:
        {
            "name": "...",
            "x": ...,
            "y": ...,
            "audio": [...],
            "images": [...],
            ...
        }
        """
        QObject.__init__(self)
        QGraphicsEllipseItem.__init__(self,
                                      -radius/2,
                                      -radius/2,
                                      radius,
                                      radius)

        self.signals = MarkerSignals()
        self.data = data
        self.name = data["name_ru"] # todo: replace with name_krl
        self.base_radius = radius
        self.active_color = self.ACTIVE_COLOR
        self.inactive_color = self.ACTIVE_COLOR.darker(130)
        self.setBrush(QBrush(self.inactive_color))
        self.setPen(QPen(Qt.black, 1))

        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setPos(data["x"], data["y"])
        self.setZValue(100)


    # -----------------------------------
    #  DOUBLE TAP
    # -----------------------------------
    def mouseDoubleClickEvent(self, event):
        self.signals.clicked.emit(self.data)
        super().mouseDoubleClickEvent(event)

    # -----------------------------------
    #  VISUAL STATE
    # -----------------------------------
    def setActive(self):
        self.setScale(1.2)
        self.setZValue(1000)

        self.setBrush(QBrush(self.active_color))
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(30)
        glow.setOffset(0, 0)
        glow.setColor(QColor('white'))
        self.setGraphicsEffect(glow)

    def setInactive(self):
        self.setScale(1.0)
        self.setZValue(0)
        self.setBrush(QBrush(self.inactive_color))

        effect = self.graphicsEffect()
        if effect:
            effect.setEnabled(False)
            effect.deleteLater()

        self.setGraphicsEffect(None)
        self.prepareGeometryChange()
        self.update()

    def resetState(self):
        self.setInactive()

    def boundingRect(self):
        r = super().boundingRect()
        return r.adjusted(-30, -30, 30, 30)
