from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLineEdit, QFrame, QInputDialog, QMessageBox,
)
from PyQt5.QtCore import QThread, Qt, pyqtSlot

from database import Database
from ai_engine import ChatTurnWorker

_SEP_THIN  = "─" * 48
_SEP_THICK = "═" * 48


class ChatDialog(QDialog):
    def __init__(self, db: Database, settings: dict, report_text: str, parent=None):
        super().__init__(parent)
        self.db = db
        self.settings = settings
        self._report_text = report_text
        self._generating = False
        self._last_user_msg = ""

        # History must start with a user turn — Anthropic rejects assistant-first.
        self._history: list[dict] = [
            {"role": "user",      "content": "give me a report on the latest messages"},
            {"role": "assistant", "content": report_text},
        ]

        # Held to prevent premature GC; replaced each turn
        self._thread: QThread | None = None
        self._worker: ChatTurnWorker | None = None

        self.setWindowTitle("Chat")
        self.setMinimumSize(680, 540)
        self.resize(740, 600)
        self.setModal(False)

        self._build_ui()
        self._init_transcript()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._display = QTextEdit()
        self._display.setObjectName("chatDisplay")
        self._display.setReadOnly(True)
        root.addWidget(self._display, stretch=1)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #1a1a1a;")
        root.addWidget(divider)

        input_row = QHBoxLayout()
        input_row.setContentsMargins(12, 8, 12, 8)
        input_row.setSpacing(8)

        self._input = QLineEdit()
        self._input.setObjectName("chatInput")
        self._input.setPlaceholderText("Ask a follow-up question…")
        self._input.returnPressed.connect(self._send)
        input_row.addWidget(self._input, stretch=1)

        self._send_btn = QPushButton("Send")
        self._send_btn.setObjectName("sendBtn")
        self._send_btn.clicked.connect(self._send)
        input_row.addWidget(self._send_btn)

        root.addLayout(input_row)

        bottom = QFrame()
        bottom.setStyleSheet("background-color:#050505;border-top:1px solid #111111;")
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

        self._last_user_msg = text
        self._input.clear()
        self._append_user(text)
        self._display.appendPlainText("\nAI:")

        self._generating = True
        self._send_btn.setEnabled(False)
        self._input.setEnabled(False)

        # ---- Canonical PyQt5 worker pattern --------------------------------
        # No parent on either object — deleteLater handles C++ lifetime.
        # Explicit QueuedConnection ensures slots run on the main-thread
        # event loop regardless of when moveToThread was called.
        worker = ChatTurnWorker(self.db, self.settings, list(self._history), text)
        thread = QThread()                       # ← no parent

        worker.moveToThread(thread)

        # Wire up work and cleanup
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)   # C++ cleanup after thread stops
        worker.error.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)   # C++ cleanup

        # Cross-thread UI updates — always queued so they land on main thread
        worker.log_update.connect(self._on_log,     Qt.QueuedConnection)
        worker.finished.connect(self._on_ai_done,   Qt.QueuedConnection)
        worker.error.connect(self._on_ai_error,     Qt.QueuedConnection)

        # Keep strong Python references so GC doesn't collect wrappers
        # before Qt has finished with the underlying C++ objects.
        self._thread = thread
        self._worker = worker

        thread.start()

    # ------------------------------------------------------------------ slots
    # @pyqtSlot ensures Qt's meta-object system routes signals correctly.

    @pyqtSlot(str)
    def _on_log(self, line: str):
        try:
            self._display.appendPlainText(line)
            self._scroll_to_bottom()
        except RuntimeError:
            pass   # widget already destroyed (dialog closed mid-turn)

    @pyqtSlot(str)
    def _on_ai_done(self, response: str):
        try:
            self._history.append({"role": "user",      "content": self._last_user_msg})
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
        except RuntimeError:
            pass

    @pyqtSlot(str)
    def _on_ai_error(self, error: str):
        try:
            self._display.appendPlainText(_SEP_THIN)
            self._display.appendPlainText(f"[error: {error}]")
            self._display.appendPlainText(_SEP_THICK)
            self._scroll_to_bottom()

            self._generating = False
            self._send_btn.setEnabled(True)
            self._input.setEnabled(True)
        except RuntimeError:
            pass

    # ------------------------------------------------------------------ helpers

    def _append_user(self, text: str):
        self._display.appendPlainText("")
        self._display.appendPlainText("You:")
        self._display.appendPlainText(text)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        try:
            sb = self._display.verticalScrollBar()
            sb.setValue(sb.maximum())
        except RuntimeError:
            pass

    # ------------------------------------------------------------------ save / delete

    def _save_chat(self):
        default = f"Chat {datetime.now().strftime('%m/%d %H:%M')}"
        title, ok = QInputDialog.getText(self, "Save Chat", "Title:", text=default)
        if not ok or not title.strip():
            return
        self.db.save_chat(title.strip(), self._display.toPlainText())
        QMessageBox.information(
            self, "Saved",
            f'Chat saved as "{title.strip()}".\nView it in Data → Chats.'
        )

    def _delete_chat(self):
        reply = QMessageBox.question(
            self, "Delete Chat",
            "Close and discard this chat? Unsaved content will be lost.",
            QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel,
        )
        if reply == QMessageBox.Yes:
            self.reject()

    def closeEvent(self, event):
        if self._thread is not None:
            try:
                if self._thread.isRunning():
                    self._thread.quit()
                    self._thread.wait(2000)
            except RuntimeError:
                pass
        event.accept()
