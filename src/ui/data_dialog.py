from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QTextEdit, QListWidget,
    QListWidgetItem, QPushButton, QHBoxLayout, QSplitter,
)
from PyQt5.QtCore import Qt

from database import Database


class DataDialog(QDialog):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Data Viewer")
        self.setMinimumSize(800, 520)
        self.setModal(True)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # ---- Messages tab ----
        msg_widget = QWidget()
        msg_layout = QVBoxLayout(msg_widget)
        msg_layout.setContentsMargins(0, 8, 0, 0)

        self._msg_table = QTableWidget(0, 4)
        self._msg_table.setHorizontalHeaderLabels(["ID", "Sender", "Date", "Content"])
        self._msg_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._msg_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._msg_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._msg_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._msg_table.setAlternatingRowColors(True)
        self._msg_table.verticalHeader().setVisible(False)
        self._msg_table.itemSelectionChanged.connect(self._show_message_detail)
        msg_layout.addWidget(self._msg_table)

        self._msg_detail = QTextEdit()
        self._msg_detail.setReadOnly(True)
        self._msg_detail.setObjectName("reportText")
        self._msg_detail.setMaximumHeight(100)
        self._msg_detail.setPlaceholderText("Select a message to see full content…")
        msg_layout.addWidget(self._msg_detail)

        self._msg_count_label = QLabel()
        self._msg_count_label.setStyleSheet("color: #556688; font-size: 11px;")
        msg_layout.addWidget(self._msg_count_label)

        tabs.addTab(msg_widget, "Messages")

        # ---- Reports tab ----
        rep_widget = QWidget()
        rep_layout = QVBoxLayout(rep_widget)
        rep_layout.setContentsMargins(0, 8, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        self._rep_list = QListWidget()
        self._rep_list.setMaximumWidth(260)
        self._rep_list.itemSelectionChanged.connect(self._show_report_detail)
        splitter.addWidget(self._rep_list)

        self._rep_detail = QTextEdit()
        self._rep_detail.setReadOnly(True)
        self._rep_detail.setObjectName("reportText")
        self._rep_detail.setPlaceholderText("Select a report to read it…")
        splitter.addWidget(self._rep_detail)

        splitter.setStretchFactor(1, 3)
        rep_layout.addWidget(splitter)

        self._rep_count_label = QLabel()
        self._rep_count_label.setStyleSheet("color: #556688; font-size: 11px;")
        rep_layout.addWidget(self._rep_count_label)

        tabs.addTab(rep_widget, "Reports")

        # ---- Refresh / close buttons ----
        btn_bar = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_data)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_bar.addWidget(refresh_btn)
        btn_bar.addStretch()
        btn_bar.addWidget(close_btn)
        layout.addLayout(btn_bar)

    def _load_data(self):
        # messages
        messages = self.db.get_all_messages()
        self._msg_table.setRowCount(0)
        for row_idx, msg in enumerate(messages):
            self._msg_table.insertRow(row_idx)
            self._msg_table.setItem(row_idx, 0, QTableWidgetItem(str(msg["id"])))
            self._msg_table.setItem(row_idx, 1, QTableWidgetItem(msg["sender"]))
            self._msg_table.setItem(row_idx, 2, QTableWidgetItem(msg["date"]))
            preview = msg["content"][:80] + ("…" if len(msg["content"]) > 80 else "")
            item = QTableWidgetItem(preview)
            item.setData(Qt.UserRole, msg["content"])
            self._msg_table.setItem(row_idx, 3, item)
        self._msg_count_label.setText(f"{len(messages)} messages stored")

        # reports
        self._rep_list.clear()
        self._reports_data = []
        reports = self.db.get_all_reports()
        for r in reports:
            item = QListWidgetItem(r["generated_at"][:16])
            self._rep_list.addItem(item)
            self._reports_data.append(r["content"])
        self._rep_count_label.setText(f"{len(reports)} reports generated")

    def _show_message_detail(self):
        selected = self._msg_table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        content_item = self._msg_table.item(row, 3)
        if content_item:
            full = content_item.data(Qt.UserRole)
            sender = self._msg_table.item(row, 1).text()
            date = self._msg_table.item(row, 2).text()
            self._msg_detail.setPlainText(f"From: {sender}\nDate: {date}\n\n{full}")

    def _show_report_detail(self):
        row = self._rep_list.currentRow()
        if 0 <= row < len(self._reports_data):
            self._rep_detail.setPlainText(self._reports_data[row])
