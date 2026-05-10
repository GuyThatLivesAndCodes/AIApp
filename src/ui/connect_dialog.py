from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QTextEdit, QApplication,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


_CURL = """\
curl -X POST http://localhost:{port}/message \\
  -H "Content-Type: application/json" \\
  -d '{{"sender":"Liam","content":"yo sarah broke up wit that guy","date":"5/9/2026 5:19PM"}}'"""

_POWERSHELL = """\
Invoke-RestMethod `
  -Uri "http://localhost:{port}/message" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{{"sender":"Liam","content":"yo sarah broke up wit that guy","date":"5/9/2026 5:19PM"}}'"""

_PYTHON = """\
import requests

requests.post(
    "http://localhost:{port}/message",
    json={{
        "sender": "Liam",
        "content": "yo sarah broke up wit that guy",
        "date": "5/9/2026 5:19PM",
    }},
)"""

_JAVASCRIPT = """\
fetch("http://localhost:{port}/message", {{
  method: "POST",
  headers: {{ "Content-Type": "application/json" }},
  body: JSON.stringify({{
    sender: "Liam",
    content: "yo sarah broke up wit that guy",
    date: "5/9/2026 5:19PM",
  }}),
}});"""

_NODE = """\
// Node.js built-in fetch (v18+) or install node-fetch
const res = await fetch("http://localhost:{port}/message", {{
  method: "POST",
  headers: {{ "Content-Type": "application/json" }},
  body: JSON.stringify({{
    sender: "Liam",
    content: "yo sarah broke up wit that guy",
    date: "5/9/2026 5:19PM",
  }}),
}});
console.log(await res.json());"""

_SCHEMA = """\
POST http://localhost:{port}/message
Content-Type: application/json

{{
  "sender":  "string — who sent the message",
  "content": "string — the message text",
  "date":    "string — e.g. 5/9/2026 5:19PM"
}}

Responses:
  200  {{"status":"ok","sender":"..."}}
  400  {{"error":"sender, content and date are required"}}
  404  {{"error":"use POST /message"}}

Health check:
  GET http://localhost:{port}/health  →  {{"status":"AIApp message server running"}}"""


TABS = [
    ("Schema", _SCHEMA),
    ("curl", _CURL),
    ("PowerShell", _POWERSHELL),
    ("Python", _PYTHON),
    ("JavaScript", _JAVASCRIPT),
    ("Node.js", _NODE),
]


class ConnectDialog(QDialog):
    def __init__(self, port: int, parent=None):
        super().__init__(parent)
        self.port = port
        self.setWindowTitle("How to Send Messages")
        self.setMinimumSize(620, 400)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QLabel(
            f"Server is running on  <b style='color:#4a9eff;'>http://localhost:{self.port}</b>"
        )
        header.setTextFormat(Qt.RichText)
        header.setStyleSheet("font-size:14px; padding-bottom:4px;")
        layout.addWidget(header)

        sub = QLabel("Send a <b>POST</b> request to <code>/message</code> with a JSON body for each message.")
        sub.setTextFormat(Qt.RichText)
        sub.setStyleSheet("color:#888899; font-size:12px;")
        layout.addWidget(sub)

        tabs = QTabWidget()
        layout.addWidget(tabs, stretch=1)

        mono = QFont("Courier New", 10)

        for tab_name, template in TABS:
            code = template.format(port=self.port)
            w = QWidget()
            wl = QVBoxLayout(w)
            wl.setContentsMargins(0, 8, 0, 0)
            wl.setSpacing(6)

            te = QTextEdit()
            te.setReadOnly(True)
            te.setPlainText(code)
            te.setFont(mono)
            te.setObjectName("reportText")
            wl.addWidget(te)

            copy_btn = QPushButton("Copy")
            copy_btn.setFixedWidth(80)
            copy_btn.clicked.connect(lambda _, c=code: QApplication.clipboard().setText(c))
            copy_row = QHBoxLayout()
            copy_row.addStretch()
            copy_row.addWidget(copy_btn)
            wl.addLayout(copy_row)

            tabs.addTab(w, tab_name)

        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(90)
        close_btn.clicked.connect(self.accept)
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_row.addWidget(close_btn)
        layout.addLayout(close_row)
