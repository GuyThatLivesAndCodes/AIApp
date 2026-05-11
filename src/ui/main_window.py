import random
import re
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame, QMenu, QAction, QSizePolicy, QTabWidget,
    QInputDialog,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont


def _md_to_html(text: str) -> str:
    """Convert basic Markdown to HTML suitable for QTextEdit rich-text display."""
    def inline(s: str) -> str:
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"__(.+?)__",      r"<b>\1</b>", s)
        s = re.sub(r"\*(.+?)\*",      r"<em>\1</em>", s)
        s = re.sub(r"_(.+?)_",        r"<em>\1</em>", s)
        s = re.sub(r"`(.+?)`",        r'<code style="font-family:monospace;">\1</code>', s)
        return s

    lines = text.split("\n")
    html: list[str] = []
    in_ul = False

    def close_ul():
        nonlocal in_ul
        if in_ul:
            html.append("</ul>")
            in_ul = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("### "):
            close_ul()
            html.append(f'<h3 style="margin:6px 0 2px;color:#d4d4d4;font-size:11pt;">{inline(stripped[4:])}</h3>')
        elif stripped.startswith("## "):
            close_ul()
            html.append(f'<h2 style="margin:10px 0 4px;color:#e8e8e8;font-size:13pt;">{inline(stripped[3:])}</h2>')
        elif stripped.startswith("# "):
            close_ul()
            html.append(f'<h1 style="margin:14px 0 6px;color:#f0f0f0;font-size:15pt;">{inline(stripped[2:])}</h1>')
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_ul:
                html.append('<ul style="margin:4px 0;padding-left:20px;">')
                in_ul = True
            html.append(f'<li style="margin:2px 0;">{inline(stripped[2:])}</li>')
        elif stripped.startswith("---") or stripped.startswith("***"):
            close_ul()
            html.append('<hr style="border:none;border-top:1px solid #2a2a2a;margin:8px 0;">')
        elif stripped == "":
            close_ul()
            html.append("<br>")
        else:
            close_ul()
            html.append(f'<p style="margin:3px 0;">{inline(stripped)}</p>')

    close_ul()
    return "\n".join(html)

from config import REPORT_INTERVAL_NORMAL, REPORT_INTERVAL_MANUAL_MIN, REPORT_INTERVAL_MANUAL_MAX, APP_VERSION
from database import Database, load_settings, save_settings
from message_server import MessageServer
from ai_engine import ReportWorker
from notifier import notify_report_ready
from ui.settings_dialog import SettingsDialog
from ui.server_settings_dialog import ServerSettingsDialog
from ui.data_dialog import DataDialog
from ui.connect_dialog import ConnectDialog
from ui.chat_dialog import ChatDialog
from ui.context_dialog import ContextDialog


class MainWindow(QMainWindow):
    _bring_to_front = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.settings = load_settings()
        self._seconds_left = REPORT_INTERVAL_NORMAL
        self._report_thread: QThread | None = None
        self._generating = False
        self._latest_report = ""      # report_a — casual summary
        self._latest_report_b = ""   # report_b — detailed markdown
        self._log_lines: list[str] = []

        self._chat_dlg: ChatDialog | None = None   # keep ref to prevent GC of Python wrapper

        self._bring_to_front.connect(self._show_window)
        self._build_ui()
        self._setup_server()
        self._start_countdown()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        self.setWindowTitle("AIApp — Relationship & Life Monitor")
        self.setMinimumSize(780, 480)
        self.resize(900, 540)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_top_bar())

        # ---- Content area: context panel (left) + timer/report (right) ----
        content = QWidget()
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_hbox = QHBoxLayout(content)
        content_hbox.setContentsMargins(0, 0, 0, 0)
        content_hbox.setSpacing(0)

        content_hbox.addWidget(self._make_context_panel())

        right = QWidget()
        right.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(32, 24, 32, 16)
        right_layout.setSpacing(0)

        # Timer section
        right_layout.addStretch(1)

        self._timer_hint = QLabel("NEXT REPORT IN")
        self._timer_hint.setObjectName("sectionLabel")
        self._timer_hint.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self._timer_hint)

        self._timer_label = QLabel("02:00:00")
        self._timer_label.setObjectName("timerLabel")
        self._timer_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self._timer_label)

        self._next_label = QLabel("")
        self._next_label.setObjectName("nextLabel")
        self._next_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self._next_label)

        right_layout.addSpacing(20)

        self._report_now_btn = QPushButton("Report Now")
        self._report_now_btn.setObjectName("reportNowBtn")
        self._report_now_btn.clicked.connect(self._on_report_now)
        self._report_now_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self._report_now_btn)
        btn_row.addStretch()
        right_layout.addLayout(btn_row)

        right_layout.addSpacing(10)

        self._specifics_btn = QPushButton("＋  Report Specifics")
        self._specifics_btn.setObjectName("specificsBtn")
        self._specifics_btn.clicked.connect(self._open_report_specifics)
        self._specifics_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        specifics_row = QHBoxLayout()
        specifics_row.addStretch()
        specifics_row.addWidget(self._specifics_btn)
        specifics_row.addStretch()
        right_layout.addLayout(specifics_row)
        self._refresh_specifics_btn()

        right_layout.addStretch(1)

        # Report toggle
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #181818;")
        right_layout.addWidget(divider)
        right_layout.addSpacing(6)

        toggle_row = QHBoxLayout()
        self._toggle_btn = QPushButton("▶  Open Report")
        self._toggle_btn.setObjectName("toggleReportBtn")
        self._toggle_btn.setCheckable(False)
        self._toggle_btn.clicked.connect(self._toggle_report)
        toggle_row.addWidget(self._toggle_btn)
        toggle_row.addStretch()
        right_layout.addLayout(toggle_row)

        self._report_area = QWidget()
        report_area_layout = QVBoxLayout(self._report_area)
        report_area_layout.setContentsMargins(0, 4, 0, 4)
        report_area_layout.setSpacing(6)

        self._report_tabs = QTabWidget()
        self._report_tabs.setMinimumHeight(120)
        self._report_tabs.setMaximumHeight(220)

        # Tab A — casual summary (monospace chat font)
        tab_a = QWidget()
        tab_a_layout = QVBoxLayout(tab_a)
        tab_a_layout.setContentsMargins(0, 4, 0, 0)
        self._report_text = QTextEdit()
        self._report_text.setObjectName("reportText")
        self._report_text.setReadOnly(True)
        self._report_text.setPlaceholderText("No reports generated yet. Click 'Report Now' to generate one.")
        tab_a_layout.addWidget(self._report_text)
        self._report_tabs.addTab(tab_a, "Summary")

        # Tab B — detailed markdown report (Times New Roman, rich text)
        tab_b = QWidget()
        tab_b_layout = QVBoxLayout(tab_b)
        tab_b_layout.setContentsMargins(0, 4, 0, 0)
        self._report_b_text = QTextEdit()
        self._report_b_text.setObjectName("reportBText")
        self._report_b_text.setReadOnly(True)
        self._report_b_text.setAcceptRichText(True)
        self._report_b_text.setPlaceholderText("Detailed report will appear here after generation.")
        _serif = QFont("Times New Roman", 11)
        self._report_b_text.setFont(_serif)
        self._report_b_text.document().setDefaultFont(_serif)
        tab_b_layout.addWidget(self._report_b_text)
        self._report_tabs.addTab(tab_b, "Detailed")

        report_area_layout.addWidget(self._report_tabs)

        chat_row = QHBoxLayout()
        chat_row.addStretch()
        self._chat_btn = QPushButton("Start Chat")
        self._chat_btn.setObjectName("chatBtn")
        self._chat_btn.setEnabled(False)
        self._chat_btn.clicked.connect(self._open_chat)
        chat_row.addWidget(self._chat_btn)
        report_area_layout.addLayout(chat_row)

        self._report_area.hide()
        right_layout.addWidget(self._report_area)

        content_hbox.addWidget(right, stretch=1)
        root.addWidget(content, stretch=1)
        root.addWidget(self._make_bottom_bar())

        self._status_label = QLabel("Server not running")
        self._status_label.setObjectName("statusLabel")
        self.statusBar().addWidget(self._status_label)

    def _make_top_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("topBar")
        bar.setFixedHeight(52)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        self._serve_btn = QPushButton("○  Serve  ▾")
        self._serve_btn.setObjectName("serveBtn")
        self._serve_btn.setProperty("serverRunning", "false")
        self._serve_btn.setFixedHeight(34)
        self._serve_btn.setMinimumWidth(120)
        self._serve_btn.clicked.connect(self._show_serve_menu)
        layout.addWidget(self._serve_btn)

        layout.addStretch()

        data_btn = QPushButton("Data")
        data_btn.setObjectName("dataBtn")
        data_btn.setFixedHeight(34)
        data_btn.clicked.connect(self._open_data)
        layout.addWidget(data_btn)

        return bar

    def _make_bottom_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("bottomBar")
        bar.setFixedHeight(40)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)

        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setObjectName("versionLabel")
        layout.addWidget(version_label)

        layout.addStretch()

        settings_btn = QPushButton("Settings")
        settings_btn.setObjectName("settingsBtn")
        settings_btn.setFixedHeight(26)
        settings_btn.clicked.connect(self._open_settings)
        layout.addWidget(settings_btn)

        return bar

    # ------------------------------------------------------------------ context panel

    def _make_context_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("contextPanel")
        panel.setFixedWidth(210)
        panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 20, 14, 14)
        layout.setSpacing(6)

        header = QLabel("YOUR CONTEXT")
        header.setObjectName("sectionLabel")
        layout.addWidget(header)

        layout.addSpacing(6)

        self._context_display = QTextEdit()
        self._context_display.setObjectName("contextDisplay")
        self._context_display.setReadOnly(True)
        layout.addWidget(self._context_display, stretch=1)

        edit_btn = QPushButton("Edit Context")
        edit_btn.setObjectName("editContextBtn")
        edit_btn.clicked.connect(self._open_context_editor)
        layout.addWidget(edit_btn)

        self._refresh_context_display()
        return panel

    def _refresh_context_display(self):
        user = self.settings.get("user", {})
        name = user.get("name", "").strip()
        ctx = user.get("context", {})
        friends = ctx.get("friends", [])
        family  = ctx.get("family",  [])
        crushes = ctx.get("crushes", [])
        custom  = ctx.get("custom",  "").strip()

        lines = []
        if name:
            lines.append(f"// {name}")
            lines.append("")

        for label, names in [("friends", friends), ("family", family), ("crushes", crushes)]:
            if names:
                lines.append(label)
                for n in names:
                    lines.append(f"  {n}")
                lines.append("")

        if custom:
            if lines:
                lines.append("─" * 18)
            preview = custom[:220]
            if len(custom) > 220:
                preview += "…"
            lines.append(preview)

        if not lines:
            lines = [
                "nothing set yet.",
                "",
                "click Edit Context",
                "to add info about",
                "yourself and your",
                "relationships.",
            ]

        self._context_display.setPlainText("\n".join(lines))

    # ------------------------------------------------------------------ serve menu

    def _show_serve_menu(self):
        menu = QMenu(self)
        server_running = self._server.running

        if server_running:
            stop_action = QAction("Stop", self)
            stop_action.triggered.connect(self._stop_server)
            menu.addAction(stop_action)
        else:
            start_action = QAction("Start", self)
            start_action.triggered.connect(self._start_server)
            menu.addAction(start_action)

        menu.addSeparator()

        connect_action = QAction("How to Connect…", self)
        connect_action.triggered.connect(self._open_connect_help)
        menu.addAction(connect_action)

        menu.addSeparator()

        settings_action = QAction("Settings", self)
        if server_running:
            settings_action.setEnabled(False)
        else:
            settings_action.triggered.connect(self._open_server_settings)
        menu.addAction(settings_action)

        pos = self._serve_btn.mapToGlobal(self._serve_btn.rect().bottomLeft())
        menu.exec_(pos)

    # ------------------------------------------------------------------ server

    def _setup_server(self):
        self._server = MessageServer(self.settings["server"]["port"])
        self._server.message_received.connect(self._on_message_received)
        self._server.status_changed.connect(self._on_server_status)
        self._server.error_occurred.connect(self._on_server_error)

    def _start_server(self):
        port = self.settings["server"]["port"]
        self._server.start(port)

    def _stop_server(self):
        self._server.stop()

    def _on_server_status(self, running: bool, text: str):
        self._status_label.setText(text)
        state = "true" if running else "false"
        self._serve_btn.setProperty("serverRunning", state)
        self._serve_btn.setText("●  Running  ▾" if running else "○  Serve  ▾")
        self._serve_btn.style().unpolish(self._serve_btn)
        self._serve_btn.style().polish(self._serve_btn)

    def _on_server_error(self, error: str):
        self._status_label.setText(f"Error: {error}")

    def _on_message_received(self, sender: str, content: str, date: str, conversation: str):
        if self.db.message_exists(sender, content, date, conversation):
            self._status_label.setText(f"Duplicate skipped from {sender} ({conversation})")
            return
        self.db.add_message(sender, content, date, conversation)
        self._status_label.setText(f"Message received from {sender} ({conversation})")

    # ------------------------------------------------------------------ countdown

    def _start_countdown(self):
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(1000)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start()
        self._update_timer_display()

    def _tick(self):
        if self._generating:
            return
        if self._seconds_left > 0:
            self._seconds_left -= 1
            self._update_timer_display()
        else:
            self._trigger_report(manual=False)

    def _update_timer_display(self):
        h = self._seconds_left // 3600
        m = (self._seconds_left % 3600) // 60
        s = self._seconds_left % 60
        self._timer_label.setText(f"{h:02d}:{m:02d}:{s:02d}")
        next_time = datetime.now() + timedelta(seconds=self._seconds_left)
        self._next_label.setText(f"at {next_time.strftime('%H:%M')}")

    # ------------------------------------------------------------------ report

    def _on_report_now(self):
        if self._generating:
            return
        self._trigger_report(manual=True)

    def _trigger_report(self, manual: bool):
        self._generating = True
        self._report_now_btn.setEnabled(False)
        self._report_now_btn.setText("Generating…")
        self._status_label.setText("Generating report…")
        self._timer_hint.setText("GENERATING REPORT")
        self._next_label.setText("")

        if manual:
            interval = random.randint(REPORT_INTERVAL_MANUAL_MIN, REPORT_INTERVAL_MANUAL_MAX)
        else:
            interval = REPORT_INTERVAL_NORMAL
        self._seconds_left = interval
        self._update_timer_display()

        if not self._report_area.isVisible():
            self._toggle_report()
        self._report_text.setPlainText("")
        self._report_b_text.setPlainText("")
        self._log_lines = []
        self._report_tabs.setCurrentIndex(0)   # show Summary tab during generation

        worker = ReportWorker(self.db, self.settings)
        thread = QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit, Qt.DirectConnection)
        worker.error.connect(thread.quit,    Qt.DirectConnection)
        thread.finished.connect(thread.deleteLater)
        worker.log_update.connect(self._on_log_line,   Qt.QueuedConnection)
        worker.finished.connect(self._on_report_done,  Qt.QueuedConnection)
        worker.error.connect(self._on_report_error,    Qt.QueuedConnection)
        self._report_thread = thread
        self._worker_ref = worker   # keeps worker alive; GC'd when replaced
        thread.start()

    @pyqtSlot(str)
    def _on_log_line(self, line: str):
        self._log_lines.append(line)
        self._report_text.setPlainText("\n".join(self._log_lines))
        sb = self._report_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    @pyqtSlot(str, str)
    def _on_report_done(self, report_a: str, report_b: str):
        self._latest_report = report_a
        self._latest_report_b = report_b
        self.db.add_report(report_a, report_b)

        # Summary tab: log lines + casual report_a
        separator = "─" * 40
        full_text = "\n".join(self._log_lines) + f"\n\n{separator}\n\n{report_a}"
        self._report_text.setPlainText(full_text)
        sb = self._report_text.verticalScrollBar()
        sb.setValue(sb.maximum())

        # Detailed tab: markdown report_b rendered as HTML
        if report_b:
            html = _md_to_html(report_b)
            self._report_b_text.setHtml(
                f'<html><body style="font-family:\'Times New Roman\',serif;'
                f'font-size:12pt;color:#cccccc;background:#060606;">'
                f'{html}</body></html>'
            )
            sb2 = self._report_b_text.verticalScrollBar()
            sb2.setValue(0)
        else:
            self._report_b_text.setPlainText(report_a)

        self._generating = False
        self._report_now_btn.setEnabled(True)
        self._report_now_btn.setText("Report Now")
        self._chat_btn.setEnabled(True)
        self._timer_hint.setText("NEXT REPORT IN")
        self._update_timer_display()
        self._status_label.setText(f"Report generated at {datetime.now().strftime('%H:%M:%S')}")

        if self.settings["notifications"].get("enabled", True):
            notify_report_ready(on_click=lambda: self._bring_to_front.emit())

    @pyqtSlot(str)
    def _on_report_error(self, error: str):
        self._report_text.setPlainText(f"Error generating report:\n{error}")
        self._generating = False
        self._report_now_btn.setEnabled(True)
        self._report_now_btn.setText("Report Now")
        self._timer_hint.setText("NEXT REPORT IN")
        self._update_timer_display()
        self._status_label.setText(f"Report error: {error[:60]}")

    # ------------------------------------------------------------------ report toggle

    def _toggle_report(self):
        if self._report_area.isVisible():
            self._report_area.hide()
            self._toggle_btn.setText("▶  Open Report")
        else:
            self._report_area.show()
            self._toggle_btn.setText("▼  Close Report")

    # ------------------------------------------------------------------ dialogs

    def _open_chat(self):
        if not self._latest_report:
            return
        # Store reference to prevent Python GC of the wrapper while the dialog is open.
        # Without this, the C++ parent keeps the dialog alive but the Python wrapper
        # (and its bound slots) can be collected, silently breaking signal connections.
        self._chat_dlg = ChatDialog(self.db, self.settings, self._latest_report, self)
        self._chat_dlg.finished.connect(self._on_chat_closed)
        self._chat_dlg.show()

    @pyqtSlot()
    def _on_chat_closed(self):
        self._chat_dlg = None

    def _open_connect_help(self):
        dlg = ConnectDialog(self.settings["server"]["port"], self)
        dlg.exec_()

    def _open_settings(self):
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec_():
            save_settings(self.settings)

    def _open_server_settings(self):
        dlg = ServerSettingsDialog(self.settings, self)
        if dlg.exec_():
            save_settings(self.settings)
            self._server.port = self.settings["server"]["port"]

    def _open_data(self):
        dlg = DataDialog(self.db, self)
        dlg.exec_()

    def _open_report_specifics(self):
        current = self.settings.get("report_instructions", "")
        text, ok = QInputDialog.getMultiLineText(
            self,
            "Report Specifics",
            "What should the AI focus on or dig into?\n"
            "These instructions are added to every report until you clear them.",
            current,
        )
        if ok:
            self.settings["report_instructions"] = text.strip()
            save_settings(self.settings)
            self._refresh_specifics_btn()

    def _refresh_specifics_btn(self):
        active = bool(self.settings.get("report_instructions", "").strip())
        self._specifics_btn.setText("●  Report Specifics" if active else "＋  Report Specifics")
        self._specifics_btn.setProperty("specificsActive", "true" if active else "false")
        self._specifics_btn.style().unpolish(self._specifics_btn)
        self._specifics_btn.style().polish(self._specifics_btn)

    def _open_context_editor(self):
        dlg = ContextDialog(self.db, self.settings, self)
        if dlg.exec_():
            save_settings(self.settings)
            self._refresh_context_display()

    def _show_window(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()
        if not self._report_area.isVisible():
            self._toggle_report()

    # ------------------------------------------------------------------ close

    def closeEvent(self, event):
        self._server.stop()
        save_settings(self.settings)
        event.accept()
