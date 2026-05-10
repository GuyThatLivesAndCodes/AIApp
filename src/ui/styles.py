DARK_STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #0a0a0a;
    color: #e0e0e0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

/* Top / bottom bars */
QFrame#topBar, QFrame#bottomBar {
    background-color: #050505;
    border: none;
}

/* Generic push buttons */
QPushButton {
    background-color: #111111;
    color: #cccccc;
    border: 1px solid #2a2a2a;
    border-radius: 5px;
    padding: 6px 16px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #1c1c1c;
    color: #ffffff;
    border-color: #444444;
}
QPushButton:pressed {
    background-color: #080808;
}
QPushButton:disabled {
    color: #333333;
    border-color: #1a1a1a;
    background-color: #0d0d0d;
}

/* Serve button */
QPushButton#serveBtn[serverRunning="true"] {
    background-color: #f0f0f0;
    border-color: #ffffff;
    color: #000000;
    font-weight: bold;
}
QPushButton#serveBtn[serverRunning="false"] {
    background-color: #111111;
    border-color: #2a2a2a;
    color: #777777;
}
QPushButton#serveBtn:hover {
    background-color: #ffffff;
    color: #000000;
}

QPushButton#dataBtn {
    background-color: #111111;
    border-color: #2a2a2a;
    color: #aaaaaa;
}
QPushButton#dataBtn:hover {
    background-color: #1c1c1c;
    color: #ffffff;
    border-color: #444444;
}

/* Report Now / primary action */
QPushButton#reportNowBtn {
    background-color: #f0f0f0;
    border-color: #ffffff;
    color: #000000;
    font-weight: bold;
    font-size: 14px;
    padding: 10px 32px;
    border-radius: 6px;
    min-width: 180px;
}
QPushButton#reportNowBtn:hover {
    background-color: #ffffff;
}
QPushButton#reportNowBtn:disabled {
    background-color: #111111;
    border-color: #1a1a1a;
    color: #333333;
}

QPushButton#settingsBtn {
    background-color: transparent;
    border: 1px solid #1e1e1e;
    color: #555555;
    padding: 4px 18px;
}
QPushButton#settingsBtn:hover {
    background-color: #111111;
    border-color: #333333;
    color: #cccccc;
}

QPushButton#toggleReportBtn {
    background-color: transparent;
    border: none;
    color: #aaaaaa;
    text-align: left;
    font-size: 13px;
    padding: 4px 8px;
}
QPushButton#toggleReportBtn:hover {
    color: #ffffff;
}

QPushButton#chatBtn {
    background-color: #111111;
    border: 1px solid #2a2a2a;
    color: #aaaaaa;
    font-size: 12px;
    padding: 5px 14px;
    border-radius: 5px;
}
QPushButton#chatBtn:hover {
    background-color: #1c1c1c;
    color: #ffffff;
    border-color: #444444;
}
QPushButton#chatBtn:disabled {
    color: #2a2a2a;
    border-color: #1a1a1a;
}

QPushButton#sendBtn {
    background-color: #e0e0e0;
    border-color: #ffffff;
    color: #000000;
    font-weight: bold;
    min-width: 70px;
}
QPushButton#sendBtn:hover {
    background-color: #ffffff;
}
QPushButton#sendBtn:disabled {
    background-color: #111111;
    border-color: #1a1a1a;
    color: #333333;
}

/* Timer */
QLabel#timerLabel {
    color: #ffffff;
    font-size: 48px;
    font-weight: bold;
    font-family: "Courier New", monospace;
}
QLabel#timerHintLabel {
    color: #333333;
    font-size: 12px;
}
QLabel#sectionLabel {
    color: #444444;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 2px;
}

/* Report / chat text areas */
QTextEdit#reportText, QTextEdit#chatDisplay {
    background-color: #050505;
    border: 1px solid #1a1a1a;
    border-radius: 5px;
    padding: 12px;
    color: #cccccc;
    font-size: 13px;
    font-family: "Consolas", "Courier New", monospace;
}

/* Status bar */
QLabel#statusLabel {
    color: #333333;
    font-size: 11px;
    padding: 2px 8px;
}

/* Inputs */
QLineEdit, QSpinBox, QComboBox {
    background-color: #050505;
    border: 1px solid #222222;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e0e0e0;
    selection-background-color: #2a2a2a;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #555555;
}
QLineEdit#chatInput {
    background-color: #0d0d0d;
    border: 1px solid #222222;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 13px;
}
QLineEdit#chatInput:focus {
    border-color: #444444;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #555555;
    width: 0;
    height: 0;
    margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: #0d0d0d;
    border: 1px solid #222222;
    selection-background-color: #1e1e1e;
    color: #e0e0e0;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #1a1a1a;
    background-color: #0a0a0a;
}
QTabBar::tab {
    background-color: #050505;
    color: #444444;
    border: 1px solid #1a1a1a;
    border-bottom: none;
    padding: 6px 16px;
}
QTabBar::tab:selected {
    background-color: #0a0a0a;
    color: #e0e0e0;
    border-color: #333333;
}
QTabBar::tab:hover {
    color: #aaaaaa;
}

/* Tables */
QTableWidget {
    background-color: #050505;
    alternate-background-color: #0a0a0a;
    gridline-color: #1a1a1a;
    color: #cccccc;
    border: 1px solid #1a1a1a;
}
QTableWidget::item:selected {
    background-color: #1e1e1e;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #0d0d0d;
    color: #555555;
    border: none;
    border-right: 1px solid #1a1a1a;
    padding: 6px 8px;
    font-weight: bold;
    letter-spacing: 1px;
    font-size: 11px;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #050505;
    width: 6px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #222222;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #444444;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background-color: #050505;
    height: 6px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #222222;
    border-radius: 3px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* Menus */
QMenu {
    background-color: #0d0d0d;
    border: 1px solid #222222;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    border-radius: 3px;
    color: #cccccc;
}
QMenu::item:selected {
    background-color: #1e1e1e;
    color: #ffffff;
}
QMenu::item:disabled {
    color: #333333;
}
QMenu::separator {
    height: 1px;
    background-color: #1a1a1a;
    margin: 4px 0;
}

/* Dialog buttons */
QDialogButtonBox QPushButton {
    min-width: 80px;
}

/* Group boxes */
QGroupBox {
    border: 1px solid #1a1a1a;
    border-radius: 5px;
    margin-top: 12px;
    padding-top: 8px;
    color: #444444;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
}

/* Checkbox / Radio */
QCheckBox, QRadioButton {
    color: #aaaaaa;
    spacing: 8px;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #2a2a2a;
    border-radius: 3px;
    background-color: #050505;
}
QCheckBox::indicator:checked {
    background-color: #e0e0e0;
    border-color: #ffffff;
}
QRadioButton::indicator { border-radius: 8px; }
QRadioButton::indicator:checked {
    background-color: #e0e0e0;
    border-color: #ffffff;
}

/* Labels */
QLabel { color: #aaaaaa; }

/* List widget */
QListWidget {
    background-color: #050505;
    border: 1px solid #1a1a1a;
    color: #cccccc;
}
QListWidget::item:selected {
    background-color: #1e1e1e;
    color: #ffffff;
}
QListWidget::item:hover {
    background-color: #111111;
}

/* Splitter */
QSplitter::handle { background-color: #1a1a1a; }

/* Status bar */
QStatusBar { background-color: #050505; border-top: 1px solid #111111; }
"""
