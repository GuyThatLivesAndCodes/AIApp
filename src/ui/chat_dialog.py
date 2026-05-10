from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QFrame, QInputDialog, QMessageBox,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QFont, QKeyEvent

from database import Database
from ai_engine import ChatTurnWorker

_SEP_THIN = "─" * 48
_SEP_THICK = "═" * 48


class _EnterLineEdit(QLineEdit):
    """QLineEdit that fires returnPressed but allows Shift+Enter as literal newline."""
    pass  # QLineEdit already emits returnPressed on Enter; Shift+Enter ignored (fine for single-line)


class ChatDialog(QDialog):
    def __init__(self, db: Database, settings: dict, report_text: str, parent=None):
        super().__init__(parent)
        self.db = db
        self.settings = settings
        self._report_text = report_text
        self._generating = False
        self._thread: QThread | None = None
        self._worker = None

        # Conversation history: list of {"role": "user"|"assistant", "content": str}
        # Starts with the report as the AI's opening message.
        self._history: list[dict] = [{"role": "assistant", "content": report_text}]

        self.setWindowTitle("Chat")
        self.setMinimumSize(680, 540)
        self.resize(740, 600)
        self.setModal(False)   # non-modal so user can still see the main window

        self._build_ui()
        self._init_transcript()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- Transcript ----
        self._display = QTextEdit()
        self._display.setObjectName("chatDisplay")
        self._display.setReadOnly(True)
        mono = QFont("Consolas", 11)
        self._display.setFont(mono)
        root.addWidget(self._display, stretch=1)

        # ---- Divider ----
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #1a1a1a;")
        root.addWidget(divider)

        # ---- Input row ----
        input_row = QHBoxLayout()
        input_row.setContentsMargins(12, 8, 12, 8)
        input_row.setSpacing(8)

        self._input = _EnterLineEdit()
        self._input.setObjectName("chatInput")
        self._input.setPlaceholderText("Ask a follow-up question…")
        self._input.returnPressed.connect(self._send)
        input_row.addWidget(self._input, stretch=1)

        self._send_btn = QPushButton("Send")
        self._send_btn.setObjectName("sendBtn")
        self._send_btn.clicked.connect(self._send)
        input_row.addWidget(self._send_btn)

        root.addLayout(input_row)

        # ---- Bottom bar ----
        bottom = QFrame()
        bottom.setStyleSheet("background-color: #050505; border-top: 1px solid #111111;")
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(12, 6, 12, 6)

        delete_btn = QPushButton("Delete Chat")
        delete_btn.setStyleSheet(
            "QPushButton{background:#0d0d0d;border:1px solid #2a2a2a;color:#555555;}"
            "QPushButton:hover{background:#1c0000;border-color:#660000;color:#ff6666;}"
        )
        delete_btn.clicked.connect(self._delete_chat)
        bottom_layout.addWidget(delete_btn)

        bottom_layout.addStretch()

        save_btn = QPushButton("Save Chat")
        save_btn.clicked.connect(self._save_chat)
        bottom_layout.addWidget(save_btn)

        root.addWidget(bottom)

    def _init_transcript(self):
        self._display.setPlainText(
            "── report " + "─" * 38 + "\n\n"
            + self._report_text + "\n\n"
            + _SEP_THICK
        )
        self._scroll_to_bottom()

    # ------------------------------------------------------------------ send

    def _send(self):
        if self._generating:
            return
        text = self._input.text().strip()
        if not text:
            return

        self._input.clear()
        self._append_user(text)

        self._generating = True
        self._send_btn.setEnabled(False)
        self._input.setEnabled(False)

        worker = ChatTurnWorker(self.db, self.settings, list(self._history), text)
        self._thread = QThread()
        worker.moveToThread(self._thread)
        self._thread.started.connect(worker.run)
        worker.log_update.connect(self._on_log)
        worker.finished.connect(self._on_ai_done)
        worker.error.connect(self._on_ai_error)
        worker.finished.connect(self._thread.quit)
        worker.error.connect(self._thread.quit)
        self._thread.start()
        self._worker = worker

        # Stage the pending AI header now so the user sees activity immediately
        self._append_raw("\nAI:")
        self._ai_response_started = False

    # ------------------------------------------------------------------ stream

    def _on_log(self, line: str):
        self._display.appendPlainText(line)
        self._scroll_to_bottom()

    def _on_ai_done(self, response: str):
        self._history.append({"role": "user", "content": self._input.text()})  # already cleared
        # Find last user message that we appended before clearing the input
        # It was appended via _append_user() which stored it in _last_user_msg
        self._history[-1] = {"role": "user", "content": self._last_user_msg}
        self._history.append({"role": "assistant", "content": response})

        self._display.appendPlainText(_SEP_THIN)
        self._display.appendPlainText("")
        self._display.appendPlainText(response)
        self._display.appendPlainText("")
        self._display.appendPlainText(_SEP_THICK)
        self._scroll_to_bottom()

        self._generating = False
        self._send_btn.setEnabled(True)
        self._input.setEnabled(True)
        self._input.setFocus()

    def _on_ai_error(self, error: str):
        self._display.appendPlainText(_SEP_THIN)
        self._display.appendPlainText(f"[error: {error}]")
        self._display.appendPlainText(_SEP_THICK)
        self._scroll_to_bottom()

        self._generating = False
        self._send_btn.setEnabled(True)
        self._input.setEnabled(True)

    # ------------------------------------------------------------------ helpers

    def _append_user(self, text: str):
        self._last_user_msg = text
        self._display.appendPlainText("")
        self._display.appendPlainText("You:")
        self._display.appendPlainText(text)
        self._scroll_to_bottom()

    def _append_raw(self, text: str):
        self._display.appendPlainText(text)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        sb = self._display.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ------------------------------------------------------------------ save / delete

    def _save_chat(self):
        default_title = f"Chat {datetime.now().strftime('%m/%d %H:%M')}"
        title, ok = QInputDialog.getText(
            self, "Save Chat", "Title for this chat:", text=default_title
        )
        if not ok or not title.strip():
            return
        transcript = self._display.toPlainText()
        self.db.save_chat(title.strip(), transcript)
        QMessageBox.information(self, "Saved", f'Chat saved as "{title.strip()}".\nView it in Data → Chats.')

    def _delete_chat(self):
        reply = QMessageBox.question(
            self, "Delete Chat",
            "Close and discard this chat? Any unsaved content will be lost.",
            QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel,
        )
        if reply == QMessageBox.Yes:
            self.reject()
