from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QTextEdit, QListWidget,
    QListWidgetItem, QPushButton, QHBoxLayout, QSplitter, QMessageBox,
)
from PyQt5.QtCore import Qt

from database import Database

_DELETE_STYLE = (
    "QPushButton{background:#0d0d0d;border:1px solid #2a2a2a;color:#555555;}"
    "QPushButton:hover{background:#1c0000;border-color:#660000;color:#ff6666;}"
    "QPushButton:disabled{background:#0d0d0d;border-color:#1a1a1a;color:#222222;}"
)


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
        self._msg_table.setSelectionMode(QTableWidget.ExtendedSelection)  # multi-select
        self._msg_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._msg_table.setAlternatingRowColors(True)
        self._msg_table.verticalHeader().setVisible(False)
        self._msg_table.itemSelectionChanged.connect(self._on_msg_selection_changed)
        msg_layout.addWidget(self._msg_table)

        self._msg_detail = QTextEdit()
        self._msg_detail.setReadOnly(True)
        self._msg_detail.setObjectName("reportText")
        self._msg_detail.setMaximumHeight(90)
        self._msg_detail.setPlaceholderText("Select a message to see full content…")
        msg_layout.addWidget(self._msg_detail)

        # action row: count label + delete button
        msg_action_row = QHBoxLayout()
        self._msg_count_label = QLabel()
        self._msg_count_label.setStyleSheet("color: #555555; font-size: 11px;")
        msg_action_row.addWidget(self._msg_count_label)
        msg_action_row.addStretch()
        self._delete_btn = QPushButton("Delete Selected")
        self._delete_btn.setEnabled(False)
        self._delete_btn.setStyleSheet(_DELETE_STYLE)
        self._delete_btn.clicked.connect(self._delete_selected)
        msg_action_row.addWidget(self._delete_btn)
        msg_layout.addLayout(msg_action_row)

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
        self._rep_count_label.setStyleSheet("color: #555555; font-size: 11px;")
        rep_layout.addWidget(self._rep_count_label)

        tabs.addTab(rep_widget, "Reports")

        # ---- Chats tab ----
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(0, 8, 0, 0)

        chat_splitter = QSplitter(Qt.Horizontal)

        self._chat_list = QListWidget()
        self._chat_list.setMaximumWidth(260)
        self._chat_list.itemSelectionChanged.connect(self._show_chat_detail)
        chat_splitter.addWidget(self._chat_list)

        self._chat_detail = QTextEdit()
        self._chat_detail.setReadOnly(True)
        self._chat_detail.setObjectName("chatDisplay")
        self._chat_detail.setPlaceholderText("Select a saved chat to read it…")
        chat_splitter.addWidget(self._chat_detail)
        chat_splitter.setStretchFactor(1, 3)
        chat_layout.addWidget(chat_splitter)

        chat_action_row = QHBoxLayout()
        self._chat_count_label = QLabel()
        self._chat_count_label.setStyleSheet("color: #555555; font-size: 11px;")
        chat_action_row.addWidget(self._chat_count_label)
        chat_action_row.addStretch()
        self._delete_chat_btn = QPushButton("Delete Chat")
        self._delete_chat_btn.setEnabled(False)
        self._delete_chat_btn.setStyleSheet(_DELETE_STYLE)
        self._delete_chat_btn.clicked.connect(self._delete_selected_chat)
        chat_action_row.addWidget(self._delete_chat_btn)
        chat_layout.addLayout(chat_action_row)

        tabs.addTab(chat_widget, "Chats")

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
        self._msg_detail.clear()
        messages = self.db.get_all_messages()
        self._msg_table.setRowCount(0)
        for row_idx, msg in enumerate(messages):
            self._msg_table.insertRow(row_idx)
            id_item = QTableWidgetItem(str(msg["id"]))
            id_item.setData(Qt.UserRole, msg["id"])   # store int id for deletion
            self._msg_table.setItem(row_idx, 0, id_item)
            self._msg_table.setItem(row_idx, 1, QTableWidgetItem(msg["sender"]))
            self._msg_table.setItem(row_idx, 2, QTableWidgetItem(msg["date"]))
            preview = msg["content"][:80] + ("…" if len(msg["content"]) > 80 else "")
            item = QTableWidgetItem(preview)
            item.setData(Qt.UserRole, msg["content"])
            self._msg_table.setItem(row_idx, 3, item)
        self._msg_count_label.setText(f"{len(messages)} messages stored")

        self._rep_list.clear()
        self._reports_data = []
        reports = self.db.get_all_reports()
        for r in reports:
            item = QListWidgetItem(r["generated_at"][:16])
            self._rep_list.addItem(item)
            self._reports_data.append(r["content"])
        self._rep_count_label.setText(f"{len(reports)} reports generated")

        # chats
        self._chat_list.clear()
        self._chats_data: list[dict] = self.db.get_all_chats()
        for c in self._chats_data:
            self._chat_list.addItem(f"{c['title']}  [{c['created_at'][:16]}]")
        self._chat_count_label.setText(f"{len(self._chats_data)} saved chats")
        self._delete_chat_btn.setEnabled(False)

    def _show_chat_detail(self):
        row = self._chat_list.currentRow()
        if 0 <= row < len(self._chats_data):
            self._chat_detail.setPlainText(self._chats_data[row]["transcript"])
            self._delete_chat_btn.setEnabled(True)
        else:
            self._delete_chat_btn.setEnabled(False)

    def _delete_selected_chat(self):
        row = self._chat_list.currentRow()
        if not (0 <= row < len(self._chats_data)):
            return
        chat = self._chats_data[row]
        reply = QMessageBox.question(
            self, "Delete Chat",
            f"Permanently delete \"{chat['title']}\"?",
            QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel,
        )
        if reply == QMessageBox.Yes:
            self.db.delete_chat(chat["id"])
            self._chat_detail.clear()
            self._load_data()

    def _on_msg_selection_changed(self):
        selected_rows = self._msg_table.selectionModel().selectedRows()
        count = len(selected_rows)
        self._delete_btn.setEnabled(count > 0)
        if count == 1:
            self._delete_btn.setText("Delete Selected  (1)")
        elif count > 1:
            self._delete_btn.setText(f"Delete Selected  ({count})")
        else:
            self._delete_btn.setText("Delete Selected")
        self._show_message_detail()

    def _show_message_detail(self):
        selected = self._msg_table.selectedItems()
        if not selected:
            self._msg_detail.clear()
            return
        row = selected[0].row()
        content_item = self._msg_table.item(row, 3)
        if content_item:
            full = content_item.data(Qt.UserRole)
            sender = self._msg_table.item(row, 1).text()
            date = self._msg_table.item(row, 2).text()
            self._msg_detail.setPlainText(f"From: {sender}\nDate: {date}\n\n{full}")

    def _delete_selected(self):
        selected_rows = self._msg_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        ids = [self._msg_table.item(r.row(), 0).data(Qt.UserRole) for r in selected_rows]
        n = len(ids)
        noun = "message" if n == 1 else "messages"

        reply = QMessageBox.question(
            self,
            "Delete Messages",
            f"Permanently delete {n} {noun}? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )
        if reply != QMessageBox.Yes:
            return

        self.db.delete_messages(ids)
        self._load_data()

    def _show_report_detail(self):
        row = self._rep_list.currentRow()
        if 0 <= row < len(self._reports_data):
            self._rep_detail.setPlainText(self._reports_data[row])
