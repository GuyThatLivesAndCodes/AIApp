from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QDialogButtonBox, QGroupBox, QFormLayout,
    QComboBox, QCheckBox, QStackedWidget, QWidget, QTabWidget,
    QRadioButton, QButtonGroup, QListWidget, QListWidgetItem,
)
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtWidgets import QTimeEdit


PROVIDERS = [
    ("Anthropic (Claude)", "anthropic"),
    ("OpenAI (GPT)", "openai"),
    ("xAI (Grok)", "xai"),
    ("Ollama (Local)", "ollama"),
    ("LM Studio (Local)", "lm_studio"),
]


class SettingsDialog(QDialog):
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()
        self._load_values()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # --- AI tab ---
        ai_widget = QWidget()
        ai_layout = QVBoxLayout(ai_widget)
        ai_layout.setSpacing(12)

        provider_group = QGroupBox("AI PROVIDER")
        provider_layout = QVBoxLayout(provider_group)

        self._provider_combo = QComboBox()
        for label, _ in PROVIDERS:
            self._provider_combo.addItem(label)
        provider_layout.addWidget(self._provider_combo)
        ai_layout.addWidget(provider_group)

        # Stacked per-provider config
        self._stack = QStackedWidget()

        # --- Anthropic page ---
        self._anthropic_page = QWidget()
        f = QFormLayout(self._anthropic_page)
        f.setSpacing(10)
        self._anthropic_key = QLineEdit()
        self._anthropic_key.setEchoMode(QLineEdit.Password)
        self._anthropic_key.setPlaceholderText("sk-ant-...")
        self._anthropic_model = QLineEdit()
        self._anthropic_model.setPlaceholderText("claude-opus-4-7")
        f.addRow("API Key:", self._anthropic_key)
        f.addRow("Model:", self._anthropic_model)
        self._stack.addWidget(self._anthropic_page)

        # --- OpenAI page ---
        self._openai_page = QWidget()
        f = QFormLayout(self._openai_page)
        f.setSpacing(10)
        self._openai_key = QLineEdit()
        self._openai_key.setEchoMode(QLineEdit.Password)
        self._openai_key.setPlaceholderText("sk-...")
        self._openai_model = QLineEdit()
        self._openai_model.setPlaceholderText("gpt-4o")
        f.addRow("API Key:", self._openai_key)
        f.addRow("Model:", self._openai_model)
        self._stack.addWidget(self._openai_page)

        # --- xAI page ---
        self._xai_page = QWidget()
        f = QFormLayout(self._xai_page)
        f.setSpacing(10)
        self._xai_key = QLineEdit()
        self._xai_key.setEchoMode(QLineEdit.Password)
        self._xai_key.setPlaceholderText("xai-...")
        self._xai_model = QLineEdit()
        self._xai_model.setPlaceholderText("grok-3")
        f.addRow("API Key:", self._xai_key)
        f.addRow("Model:", self._xai_model)
        self._stack.addWidget(self._xai_page)

        # --- Ollama page ---
        self._ollama_page = QWidget()
        f = QFormLayout(self._ollama_page)
        f.setSpacing(10)
        self._ollama_host = QLineEdit()
        self._ollama_host.setPlaceholderText("localhost")
        self._ollama_port = QSpinBox()
        self._ollama_port.setRange(1, 65535)
        self._ollama_port.setValue(11434)
        self._ollama_model = QLineEdit()
        self._ollama_model.setPlaceholderText("auto-detect")
        f.addRow("Host:", self._ollama_host)
        f.addRow("Port:", self._ollama_port)
        f.addRow("Model:", self._ollama_model)
        note = QLabel("Leave model blank to auto-detect the first available model.")
        note.setStyleSheet("color: #555555; font-size: 11px;")
        note.setWordWrap(True)
        f.addRow(note)
        self._stack.addWidget(self._ollama_page)

        # --- LM Studio page ---
        self._lms_page = QWidget()
        f = QFormLayout(self._lms_page)
        f.setSpacing(10)
        self._lms_host = QLineEdit()
        self._lms_host.setPlaceholderText("localhost")
        self._lms_port = QSpinBox()
        self._lms_port.setRange(1, 65535)
        self._lms_port.setValue(1234)
        self._lms_model = QLineEdit()
        self._lms_model.setPlaceholderText("auto-detect")
        f.addRow("Host:", self._lms_host)
        f.addRow("Port:", self._lms_port)
        f.addRow("Model:", self._lms_model)
        note2 = QLabel("Leave model blank to auto-detect the first available model.")
        note2.setStyleSheet("color: #555555; font-size: 11px;")
        note2.setWordWrap(True)
        f.addRow(note2)
        self._stack.addWidget(self._lms_page)

        ai_layout.addWidget(self._stack)
        ai_layout.addStretch()

        self._provider_combo.currentIndexChanged.connect(self._stack.setCurrentIndex)
        tabs.addTab(ai_widget, "AI")

        # --- Notifications tab ---
        notif_widget = QWidget()
        notif_layout = QVBoxLayout(notif_widget)
        notif_layout.setContentsMargins(12, 12, 12, 12)
        notif_group = QGroupBox("WINDOWS NOTIFICATIONS")
        ng_layout = QVBoxLayout(notif_group)
        self._notif_check = QCheckBox("Show notification when a report is ready")
        ng_layout.addWidget(self._notif_check)
        notif_layout.addWidget(notif_group)
        notif_layout.addStretch()
        tabs.addTab(notif_widget, "Notifications")

        # --- Schedule tab ---
        sched_widget = QWidget()
        sched_layout = QVBoxLayout(sched_widget)
        sched_layout.setContentsMargins(12, 12, 12, 12)
        sched_layout.setSpacing(10)

        sched_group = QGroupBox("REPORT SCHEDULE")
        sg_layout = QVBoxLayout(sched_group)
        sg_layout.setSpacing(8)

        hint = QLabel("The AI will generate a report automatically at each scheduled time.")
        hint.setStyleSheet("color: #555555; font-size: 11px;")
        hint.setWordWrap(True)
        sg_layout.addWidget(hint)

        self._sched_list = QListWidget()
        self._sched_list.setMaximumHeight(130)
        sg_layout.addWidget(self._sched_list)

        add_row = QHBoxLayout()
        self._time_edit = QTimeEdit()
        self._time_edit.setDisplayFormat("hh:mm AP")
        self._time_edit.setTime(QTime(7, 0))
        add_btn = QPushButton("Add")
        add_btn.setFixedWidth(60)
        add_btn.clicked.connect(self._add_schedule_time)
        remove_btn = QPushButton("Remove")
        remove_btn.setFixedWidth(70)
        remove_btn.clicked.connect(self._remove_schedule_time)
        add_row.addWidget(self._time_edit)
        add_row.addWidget(add_btn)
        add_row.addStretch()
        add_row.addWidget(remove_btn)
        sg_layout.addLayout(add_row)

        sched_layout.addWidget(sched_group)
        sched_layout.addStretch()
        tabs.addTab(sched_widget, "Schedule")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_values(self):
        ai = self.settings["ai"]
        provider_keys = [p[1] for p in PROVIDERS]
        idx = provider_keys.index(ai.get("provider", "anthropic"))
        self._provider_combo.setCurrentIndex(idx)
        self._stack.setCurrentIndex(idx)

        self._anthropic_key.setText(ai.get("anthropic_api_key", ""))
        self._anthropic_model.setText(ai.get("anthropic_model", "claude-opus-4-7"))
        self._openai_key.setText(ai.get("openai_api_key", ""))
        self._openai_model.setText(ai.get("openai_model", "gpt-4o"))
        self._xai_key.setText(ai.get("xai_api_key", ""))
        self._xai_model.setText(ai.get("xai_model", "grok-3"))
        self._ollama_host.setText(ai.get("ollama_host", "localhost"))
        self._ollama_port.setValue(ai.get("ollama_port", 11434))
        self._ollama_model.setText(ai.get("ollama_model", ""))
        self._lms_host.setText(ai.get("lm_studio_host", "localhost"))
        self._lms_port.setValue(ai.get("lm_studio_port", 1234))
        self._lms_model.setText(ai.get("lm_studio_model", ""))

        self._notif_check.setChecked(self.settings["notifications"].get("enabled", True))

        self._sched_list.clear()
        for t in self.settings.get("schedule", []):
            self._sched_list.addItem(t)

    def _save(self):
        provider_keys = [p[1] for p in PROVIDERS]
        self.settings["ai"]["provider"] = provider_keys[self._provider_combo.currentIndex()]

        self.settings["ai"]["anthropic_api_key"] = self._anthropic_key.text().strip()
        self.settings["ai"]["anthropic_model"] = self._anthropic_model.text().strip() or "claude-opus-4-7"
        self.settings["ai"]["openai_api_key"] = self._openai_key.text().strip()
        self.settings["ai"]["openai_model"] = self._openai_model.text().strip() or "gpt-4o"
        self.settings["ai"]["xai_api_key"] = self._xai_key.text().strip()
        self.settings["ai"]["xai_model"] = self._xai_model.text().strip() or "grok-3"
        self.settings["ai"]["ollama_host"] = self._ollama_host.text().strip() or "localhost"
        self.settings["ai"]["ollama_port"] = self._ollama_port.value()
        self.settings["ai"]["ollama_model"] = self._ollama_model.text().strip()
        self.settings["ai"]["lm_studio_host"] = self._lms_host.text().strip() or "localhost"
        self.settings["ai"]["lm_studio_port"] = self._lms_port.value()
        self.settings["ai"]["lm_studio_model"] = self._lms_model.text().strip()

        self.settings["notifications"]["enabled"] = self._notif_check.isChecked()

        schedule = []
        for i in range(self._sched_list.count()):
            schedule.append(self._sched_list.item(i).text())
        self.settings["schedule"] = schedule

        self.accept()

    def _add_schedule_time(self):
        t = self._time_edit.time()
        t_str = f"{t.hour():02d}:{t.minute():02d}"
        existing = [self._sched_list.item(i).text() for i in range(self._sched_list.count())]
        if t_str not in existing:
            self._sched_list.addItem(t_str)
            self._sched_list.sortItems()

    def _remove_schedule_time(self):
        row = self._sched_list.currentRow()
        if row >= 0:
            self._sched_list.takeItem(row)
