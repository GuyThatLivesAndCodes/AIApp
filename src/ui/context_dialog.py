from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialogButtonBox, QGroupBox, QFormLayout,
    QTextEdit, QTabWidget, QWidget,
)
from PyQt5.QtCore import Qt

from database import Database


class ContextDialog(QDialog):
    def __init__(self, db: Database, settings: dict, parent=None):
        super().__init__(parent)
        self.db = db
        self.settings = settings
        self.setWindowTitle("Your Context")
        self.setMinimumSize(500, 560)
        self.setModal(True)
        self._build_ui()
        self._load_values()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # User name
        name_group = QGroupBox("YOUR NAME")
        name_form = QFormLayout(name_group)
        name_form.setContentsMargins(12, 16, 12, 12)
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g. Alex  — helps AI recognise when messages mention you")
        name_form.addRow("Name:", self._name_edit)
        layout.addWidget(name_group)

        # Sender hint from DB
        senders = self.db.get_senders()
        known = f"People in your messages: {', '.join(senders)}" if senders else "No messages received yet."

        # Relationship tabs
        tabs = QTabWidget()
        self._cat_edits: dict[str, QTextEdit] = {}

        categories = [
            ("friends",  "Friends",  "Close friends whose news matters to you"),
            ("family",   "Family",   "Family members"),
            ("crushes",  "Crushes",  "People you're romantically interested in"),
        ]

        for key, label, hint in categories:
            w = QWidget()
            wl = QVBoxLayout(w)
            wl.setContentsMargins(8, 10, 8, 8)
            wl.setSpacing(6)

            te = QTextEdit()
            te.setObjectName("reportText")
            te.setPlaceholderText(f"One name per line:\n{label.rstrip('s')}\nAnother {label.rstrip('s')}")
            te.setMaximumHeight(140)
            wl.addWidget(te)

            hint_label = QLabel(known)
            hint_label.setStyleSheet("color: #555555; font-size: 11px;")
            hint_label.setWordWrap(True)
            wl.addWidget(hint_label)
            wl.addStretch()

            self._cat_edits[key] = te
            tabs.addTab(w, label)

        layout.addWidget(tabs)

        # Custom context
        about_group = QGroupBox("ABOUT YOU  (optional)")
        about_layout = QVBoxLayout(about_group)
        about_layout.setContentsMargins(12, 16, 12, 12)

        self._custom_edit = QTextEdit()
        self._custom_edit.setObjectName("reportText")
        self._custom_edit.setPlaceholderText(
            "Anything the AI should know to give better context:\n"
            "e.g. I'm 24, software developer, single, looking to date.\n"
            "My main concern right now is whether Sarah likes me back.\n"
            "Financial situation: doing ok, saving for an apartment."
        )
        self._custom_edit.setMinimumHeight(110)
        about_layout.addWidget(self._custom_edit)

        layout.addWidget(about_group)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_values(self):
        user = self.settings.get("user", {})
        self._name_edit.setText(user.get("name", ""))
        ctx = user.get("context", {})
        for key, te in self._cat_edits.items():
            te.setPlainText("\n".join(ctx.get(key, [])))
        self._custom_edit.setPlainText(ctx.get("custom", ""))

    def _save(self):
        if "user" not in self.settings:
            self.settings["user"] = {}
        self.settings["user"]["name"] = self._name_edit.text().strip()

        ctx = self.settings["user"].setdefault("context", {})
        for key, te in self._cat_edits.items():
            ctx[key] = [n.strip() for n in te.toPlainText().splitlines() if n.strip()]
        ctx["custom"] = self._custom_edit.toPlainText().strip()
        self.accept()
