import sys
import os

# Allow imports from src/ when running as a script or frozen executable
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.styles import DARK_STYLESHEET
from ui.main_window import MainWindow


def main():
    # Enable HiDPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("AIApp")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AIApp")
    app.setStyleSheet(DARK_STYLESHEET)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
