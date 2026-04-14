from PySide6.QtCore import QObject, Signal

class MarkerSignals(QObject):
    clicked = Signal(object)
    longHold = Signal(object)