from PySide6.QtWidgets import QApplication
import sys
import os

from src.ui.main_window import MainWindow

if __name__ == "__main__":

    app = QApplication(sys.argv)
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    window = MainWindow(PROJECT_ROOT)
    window.showFullScreen()

    sys.exit(app.exec())
