import sys
import os
import traceback
import logging
from pathlib import Path

# Allow imports from src/ when running as a script or frozen executable
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.styles import DARK_STYLESHEET
from ui.main_window import MainWindow

# Write unhandled exceptions to a log file so crashes are diagnosable
_log_dir = Path.home() / "AIApp"
_log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(_log_dir / "crash.log"),
    level=logging.ERROR,
    format="%(asctime)s\n%(message)s\n",
)


def _excepthook(exc_type, exc_value, exc_tb):
    logging.error("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _excepthook


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
