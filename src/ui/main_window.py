import random
import threading
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame, QMenu, QAction, QSizePolicy,
    QSpacerItem,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QFont

from config import REPORT_INTERVAL_NORMAL, REPORT_INTERVAL_MANUAL_MIN, REPORT_INTERVAL_MANUAL_MAX
from database import Database, load_settings, save_settings
from message_server import MessageServer
from ai_engine import ReportWorker
from notifier import notify_report_ready
from ui.settings_dialog import SettingsDialog
from ui.server_settings_dialog import ServerSettingsDialog
from ui.data_dialog import DataDialog
from ui.connect_dialog import ConnectDialog


class MainWindow(QMainWindow):
    _bring_to_front = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.settings = load_settings()
        self._seconds_left = REPORT_INTERVAL_NORMAL
        self._report_thread: QThread | None = None
        self._generating = False
        self._latest_report = ""
        self._log_lines: list[str] = []

        self._bring_to_front.connect(self._show_window)
        self._build_ui()
        self._setup_server()
        self._start_countdown()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        self.setWindowTitle("AIApp — Relationship & Life Monitor")
        self.setMinimumSize(560, 460)
        self.resize(620, 520)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_top_bar())

        # ---- Content area ----
        content = QWidget()
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 24, 32, 16)
        content_layout.setSpacing(0)

        # timer section
        content_layout.addStretch(1)

        timer_hint = QLabel("NEXT REPORT IN")
        timer_hint.setObjectName("sectionLabel")
        timer_hint.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(timer_hint)

        self._timer_label = QLabel("02:00:00")
        self._timer_label.setObjectName("timerLabel")
        self._timer_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self._timer_label)

        content_layout.addSpacing(24)

        self._report_now_btn = QPushButton("Report Now")
        self._report_now_btn.setObjectName("reportNowBtn")
        self._report_now_btn.clicked.connect(self._on_report_now)
        self._report_now_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self._report_now_btn)
        btn_row.addStretch()
        content_layout.addLayout(btn_row)

        content_layout.addStretch(1)

        # report toggle
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #2d2d55;")
        content_layout.addWidget(divider)
        content_layout.addSpacing(6)

        toggle_row = QHBoxLayout()
        self._toggle_btn = QPushButton("▶  Open Report")
        self._toggle_btn.setObjectName("toggleReportBtn")
        self._toggle_btn.setCheckable(False)
        self._toggle_btn.clicked.connect(self._toggle_report)
        toggle_row.addWidget(self._toggle_btn)
        toggle_row.addStretch()
        content_layout.addLayout(toggle_row)

        self._report_area = QWidget()
        report_area_layout = QVBoxLayout(self._report_area)
        report_area_layout.setContentsMargins(0, 4, 0, 4)
        self._report_text = QTextEdit()
        self._report_text.setObjectName("reportText")
        self._report_text.setReadOnly(True)
        self._report_text.setPlaceholderText("No reports generated yet. Click 'Report Now' to generate one.")
        self._report_text.setMinimumHeight(100)
        self._report_text.setMaximumHeight(180)
        report_area_layout.addWidget(self._report_text)
        self._report_area.hide()
        content_layout.addWidget(self._report_area)

        root.addWidget(content, stretch=1)
        root.addWidget(self._make_bottom_bar())

        # status bar
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

        # Serve button
        self._serve_btn = QPushButton("Serve  ▾")
        self._serve_btn.setObjectName("serveBtn")
        self._serve_btn.setProperty("serverRunning", "false")
        self._serve_btn.setFixedHeight(34)
        self._serve_btn.setMinimumWidth(100)
        self._serve_btn.clicked.connect(self._show_serve_menu)
        layout.addWidget(self._serve_btn)

        layout.addStretch()

        # Data button
        data_btn = QPushButton("Data")
        data_btn.setObjectName("dataBtn")
        data_btn.setFixedHeight(34)
        data_btn.clicked.connect(self._open_data)
        layout.addWidget(data_btn)

        return bar

    def _make_bottom_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("bottomBar")
        bar.setFixedHeight(44)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 12, 0)

        layout.addStretch()
        settings_btn = QPushButton("Settings")
        settings_btn.setObjectName("settingsBtn")
        settings_btn.setFixedHeight(28)
        settings_btn.clicked.connect(self._open_settings)
        layout.addWidget(settings_btn)
        layout.addStretch()

        return bar

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
        self._serve_btn.setText("Serve  ▾")
        self._serve_btn.style().unpolish(self._serve_btn)
        self._serve_btn.style().polish(self._serve_btn)

    def _on_server_error(self, error: str):
        self._status_label.setText(f"Error: {error}")

    def _on_message_received(self, sender: str, content: str, date: str):
        self.db.add_message(sender, content, date)
        self._status_label.setText(f"Message received from {sender}")

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

        if manual:
            interval = random.randint(REPORT_INTERVAL_MANUAL_MIN, REPORT_INTERVAL_MANUAL_MAX)
        else:
            interval = REPORT_INTERVAL_NORMAL
        self._seconds_left = interval
        self._update_timer_display()

        # Open the report panel and show a live log
        if not self._report_area.isVisible():
            self._toggle_report()
        self._report_text.setPlainText("")
        self._log_lines = []

        worker = ReportWorker(self.db, self.settings)
        self._report_thread = QThread()
        worker.moveToThread(self._report_thread)
        self._report_thread.started.connect(worker.run)
        worker.log_update.connect(self._on_log_line)
        worker.finished.connect(self._on_report_done)
        worker.error.connect(self._on_report_error)
        worker.finished.connect(self._report_thread.quit)
        worker.error.connect(self._report_thread.quit)
        self._report_thread.start()
        self._worker_ref = worker  # prevent GC

    def _on_log_line(self, line: str):
        self._log_lines.append(line)
        self._report_text.setPlainText("\n".join(self._log_lines))
        # Scroll to bottom so newest line is visible
        sb = self._report_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_report_done(self, report: str):
        self._latest_report = report
        self.db.add_report(report)
        # Append separator + final report below the tool log
        separator = "─" * 40
        full_text = "\n".join(self._log_lines) + f"\n\n{separator}\n\n{report}"
        self._report_text.setPlainText(full_text)
        sb = self._report_text.verticalScrollBar()
        sb.setValue(sb.maximum())
        self._generating = False
        self._report_now_btn.setEnabled(True)
        self._report_now_btn.setText("Report Now")
        self._status_label.setText(f"Report generated at {datetime.now().strftime('%H:%M:%S')}")

        if self.settings["notifications"].get("enabled", True):
            notify_report_ready(on_click=lambda: self._bring_to_front.emit())

    def _on_report_error(self, error: str):
        self._report_text.setPlainText(f"Error generating report:\n{error}")
        self._generating = False
        self._report_now_btn.setEnabled(True)
        self._report_now_btn.setText("Report Now")
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
