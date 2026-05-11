DARK_STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #0a0a0a;
    color: #e0e0e0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

/* ── Bars ── */
QFrame#topBar {
    background-color: #050505;
    border-bottom: 1px solid #161616;
}
QFrame#bottomBar {
    background-color: #050505;
    border-top: 1px solid #161616;
}

/* ── Generic buttons ── */
QPushButton {
    background-color: #131313;
    color: #c8c8c8;
    border: 1px solid #272727;
    border-radius: 5px;
    padding: 6px 16px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #1d1d1d;
    color: #f0f0f0;
    border-color: #3c3c3c;
}
QPushButton:pressed {
    background-color: #080808;
    border-color: #222222;
}
QPushButton:disabled {
    color: #2c2c2c;
    border-color: #171717;
    background-color: #0b0b0b;
}

/* ── Serve button ── */
QPushButton#serveBtn[serverRunning="true"] {
    background-color: #f0f0f0;
    border-color: #ffffff;
    color: #000000;
    font-weight: 600;
}
QPushButton#serveBtn[serverRunning="true"]:hover {
    background-color: #ffffff;
}
QPushButton#serveBtn[serverRunning="false"] {
    background-color: #0d0d0d;
    border-color: #202020;
    color: #606060;
}
QPushButton#serveBtn[serverRunning="false"]:hover {
    background-color: #181818;
    border-color: #343434;
    color: #cccccc;
}

/* ── Data button ── */
QPushButton#dataBtn {
    background-color: #0d0d0d;
    border-color: #202020;
    color: #707070;
    font-size: 12px;
}
QPushButton#dataBtn:hover {
    background-color: #181818;
    color: #e0e0e0;
    border-color: #363636;
}

/* ── Report Now (primary CTA) ── */
QPushButton#reportNowBtn {
    background-color: #f0f0f0;
    border-color: #ffffff;
    color: #000000;
    font-weight: 600;
    font-size: 14px;
    padding: 10px 36px;
    border-radius: 7px;
    min-width: 180px;
}
QPushButton#reportNowBtn:hover {
    background-color: #ffffff;
}
QPushButton#reportNowBtn:pressed {
    background-color: #d8d8d8;
}
QPushButton#reportNowBtn:disabled {
    background-color: #111111;
    border-color: #191919;
    color: #282828;
}

/* ── Settings button ── */
QPushButton#settingsBtn {
    background-color: transparent;
    border: 1px solid #1c1c1c;
    color: #424242;
    padding: 3px 14px;
    font-size: 11px;
    border-radius: 4px;
}
QPushButton#settingsBtn:hover {
    background-color: #111111;
    border-color: #2c2c2c;
    color: #aaaaaa;
}

/* ── Report Specifics button ── */
QPushButton#specificsBtn {
    background-color: transparent;
    border: 1px solid #1e1e1e;
    color: #404040;
    font-size: 11px;
    padding: 4px 14px;
    border-radius: 4px;
}
QPushButton#specificsBtn:hover {
    background-color: #111111;
    border-color: #2e2e2e;
    color: #aaaaaa;
}
QPushButton#specificsBtn[specificsActive="true"] {
    border-color: #2a2a2a;
    color: #787878;
}
QPushButton#specificsBtn[specificsActive="true"]:hover {
    color: #cccccc;
    border-color: #383838;
}

/* ── Report toggle ── */
QPushButton#toggleReportBtn {
    background-color: transparent;
    border: none;
    color: #808080;
    text-align: left;
    font-size: 12px;
    padding: 4px 8px;
    border-radius: 4px;
}
QPushButton#toggleReportBtn:hover {
    color: #dddddd;
    background-color: #111111;
}

/* ── Chat button ── */
QPushButton#chatBtn {
    background-color: #0f0f0f;
    border: 1px solid #232323;
    color: #808080;
    font-size: 11px;
    padding: 5px 14px;
    border-radius: 5px;
}
QPushButton#chatBtn:hover {
    background-color: #1a1a1a;
    color: #e0e0e0;
    border-color: #383838;
}
QPushButton#chatBtn:disabled {
    color: #232323;
    border-color: #171717;
    background-color: #0a0a0a;
}

/* ── Send button ── */
QPushButton#sendBtn {
    background-color: #e0e0e0;
    border-color: #f0f0f0;
    color: #000000;
    font-weight: 600;
    min-width: 70px;
    border-radius: 5px;
}
QPushButton#sendBtn:hover {
    background-color: #f5f5f5;
    border-color: #ffffff;
}
QPushButton#sendBtn:pressed {
    background-color: #c0c0c0;
}
QPushButton#sendBtn:disabled {
    background-color: #111111;
    border-color: #191919;
    color: #282828;
}

/* ── Timer ── */
QLabel#timerLabel {
    color: #f0f0f0;
    font-size: 46px;
    font-weight: bold;
    font-family: "Courier New", monospace;
    letter-spacing: 4px;
}
QLabel#sectionLabel {
    color: #525252;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 3px;
}
QLabel#nextLabel {
    color: #383838;
    font-size: 11px;
    font-family: "Segoe UI", Arial, sans-serif;
}
QLabel#versionLabel {
    color: #2c2c2c;
    font-size: 10px;
    font-family: "Consolas", monospace;
}

/* ── Text areas ── */
QTextEdit#reportText, QTextEdit#chatDisplay {
    background-color: #060606;
    border: 1px solid #1c1c1c;
    border-radius: 5px;
    padding: 12px;
    color: #c8c8c8;
    font-size: 12px;
    font-family: "Consolas", "Courier New", monospace;
    selection-background-color: #242424;
    selection-color: #ffffff;
}
QTextEdit#reportBText {
    background-color: #060606;
    border: none;
    border-radius: 0;
    padding: 10px 14px;
    color: #c8c8c8;
    selection-background-color: #242424;
    selection-color: #ffffff;
}

/* ── Status bar ── */
QLabel#statusLabel {
    color: #747474;
    font-size: 11px;
    padding: 2px 8px;
}
QStatusBar {
    background-color: #050505;
    border-top: 1px solid #141414;
}
QStatusBar::item { border: none; }

/* ── Inputs ── */
QLineEdit, QSpinBox, QComboBox {
    background-color: #070707;
    border: 1px solid #222222;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e0e0e0;
    selection-background-color: #2a2a2a;
}
QLineEdit:hover, QSpinBox:hover, QComboBox:hover {
    border-color: #2e2e2e;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #484848;
    background-color: #090909;
}
QLineEdit#chatInput {
    background-color: #0a0a0a;
    border: 1px solid #222222;
    border-radius: 5px;
    padding: 8px 14px;
    font-size: 13px;
    color: #e0e0e0;
}
QLineEdit#chatInput:focus {
    border-color: #484848;
    background-color: #0d0d0d;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #555555;
    width: 0;
    height: 0;
    margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: #0d0d0d;
    border: 1px solid #222222;
    selection-background-color: #1e1e1e;
    color: #e0e0e0;
    outline: none;
}

/* ── Tabs ── */
QTabWidget::pane {
    border: 1px solid #1c1c1c;
    background-color: #0a0a0a;
}
QTabBar::tab {
    background-color: #060606;
    color: #404040;
    border: 1px solid #1a1a1a;
    border-bottom: none;
    padding: 7px 18px;
    font-size: 12px;
}
QTabBar::tab:selected {
    background-color: #0a0a0a;
    color: #e0e0e0;
    border-color: #282828;
    border-bottom: 1px solid #0a0a0a;
}
QTabBar::tab:hover:!selected {
    color: #888888;
    background-color: #0c0c0c;
}

/* ── Tables ── */
QTableWidget {
    background-color: #060606;
    alternate-background-color: #0c0c0c;
    gridline-color: #181818;
    color: #c8c8c8;
    border: 1px solid #1c1c1c;
    selection-background-color: #1e1e1e;
}
QTableWidget::item:selected {
    background-color: #1e1e1e;
    color: #f0f0f0;
}
QTableWidget::item:hover:!selected {
    background-color: #131313;
}
QHeaderView::section {
    background-color: #0b0b0b;
    color: #484848;
    border: none;
    border-right: 1px solid #181818;
    border-bottom: 1px solid #1c1c1c;
    padding: 7px 10px;
    font-weight: bold;
    letter-spacing: 1px;
    font-size: 10px;
}

/* ── Scrollbars ── */
QScrollBar:vertical {
    background-color: #050505;
    width: 6px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #262626;
    border-radius: 3px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background-color: #484848;
}
QScrollBar::handle:vertical:pressed {
    background-color: #606060;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background-color: #050505;
    height: 6px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #262626;
    border-radius: 3px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #484848;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Menus ── */
QMenu {
    background-color: #0e0e0e;
    border: 1px solid #242424;
    padding: 4px;
}
QMenu::item {
    padding: 7px 20px;
    border-radius: 3px;
    color: #c8c8c8;
    font-size: 12px;
}
QMenu::item:selected {
    background-color: #1e1e1e;
    color: #f0f0f0;
}
QMenu::item:disabled {
    color: #333333;
}
QMenu::separator {
    height: 1px;
    background-color: #1c1c1c;
    margin: 4px 0;
}

/* ── Dialog buttons ── */
QDialogButtonBox QPushButton {
    min-width: 80px;
}

/* ── Group boxes ── */
QGroupBox {
    border: 1px solid #1c1c1c;
    border-radius: 5px;
    margin-top: 14px;
    padding-top: 10px;
    color: #4a4a4a;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 8px;
}

/* ── Checkbox / Radio ── */
QCheckBox, QRadioButton {
    color: #aaaaaa;
    spacing: 8px;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid #2c2c2c;
    border-radius: 3px;
    background-color: #080808;
}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border-color: #484848;
}
QCheckBox::indicator:checked {
    background-color: #e0e0e0;
    border-color: #f0f0f0;
}
QRadioButton::indicator { border-radius: 8px; }
QRadioButton::indicator:checked {
    background-color: #e0e0e0;
    border-color: #f0f0f0;
}

/* ── Labels ── */
QLabel { color: #aaaaaa; }

/* ── List widget ── */
QListWidget {
    background-color: #060606;
    border: 1px solid #1c1c1c;
    color: #c8c8c8;
    outline: none;
}
QListWidget::item {
    padding: 4px 8px;
}
QListWidget::item:selected {
    background-color: #1e1e1e;
    color: #f0f0f0;
}
QListWidget::item:hover:!selected {
    background-color: #111111;
}

/* ── Splitter ── */
QSplitter::handle {
    background-color: #141414;
    width: 1px;
}

/* ── Context panel ── */
QFrame#contextPanel {
    background-color: #070707;
    border-right: 1px solid #161616;
}
QTextEdit#contextDisplay {
    background-color: #070707;
    border: none;
    color: #606060;
    font-size: 11px;
    font-family: "Segoe UI", Arial, sans-serif;
    padding: 2px 0px;
    selection-background-color: #1e1e1e;
}
QPushButton#editContextBtn {
    background-color: transparent;
    border: 1px solid #1e1e1e;
    color: #404040;
    font-size: 11px;
    padding: 4px 12px;
    border-radius: 4px;
}
QPushButton#editContextBtn:hover {
    background-color: #111111;
    color: #aaaaaa;
    border-color: #2c2c2c;
}
"""
