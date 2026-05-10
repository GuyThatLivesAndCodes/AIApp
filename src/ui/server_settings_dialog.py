from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QPushButton, QDialogButtonBox, QGroupBox, QFormLayout,
)
from PyQt5.QtCore import Qt


class ServerSettingsDialog(QDialog):
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Server Settings")
        self.setMinimumWidth(360)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        group = QGroupBox("MESSAGE INGESTION SERVER")
        form = QFormLayout(group)
        form.setSpacing(12)
        form.setContentsMargins(12, 16, 12, 12)

        self._port_spin = QSpinBox()
        self._port_spin.setRange(1, 65535)
        self._port_spin.setValue(self.settings["server"]["port"])
        self._port_spin.setToolTip("Port number for incoming messages (default: 774)")
        form.addRow("Listen Port:", self._port_spin)

        layout.addWidget(group)

        hint = QLabel(
            "Clients send messages to this port in the format:\n"
            "  sender:Name\n"
            "  content:Message text\n"
            "  date:5/9/2026 5:19PM"
        )
        hint.setStyleSheet("color: #556688; font-size: 11px; font-family: 'Courier New';")
        layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self):
        self.settings["server"]["port"] = self._port_spin.value()
        self.accept()
