DARK_STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #1e1e2e;
    color: #e0e0e0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

/* Top / bottom bars */
QFrame#topBar, QFrame#bottomBar {
    background-color: #16162a;
    border: none;
}

/* Generic push buttons */
QPushButton {
    background-color: #2d2d3f;
    color: #e0e0e0;
    border: 1px solid #3d3d55;
    border-radius: 6px;
    padding: 6px 16px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #3a3a52;
    border-color: #4a9eff;
}
QPushButton:pressed {
    background-color: #252538;
}
QPushButton:disabled {
    color: #555577;
    border-color: #2d2d3f;
}

/* Blue action buttons */
QPushButton#serveBtn[serverRunning="true"] {
    background-color: #1a6bbf;
    border-color: #4a9eff;
    color: #ffffff;
    font-weight: bold;
}
QPushButton#serveBtn[serverRunning="false"] {
    background-color: #3a3a52;
    border-color: #3d3d55;
    color: #aaaacc;
}
QPushButton#serveBtn:hover {
    background-color: #2277cc;
}

QPushButton#dataBtn {
    background-color: #2d2d3f;
    border-color: #3d3d55;
}
QPushButton#dataBtn:hover {
    background-color: #3a3a52;
    border-color: #4a9eff;
}

QPushButton#reportNowBtn {
    background-color: #1a6bbf;
    border-color: #4a9eff;
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
    padding: 10px 32px;
    border-radius: 8px;
    min-width: 180px;
}
QPushButton#reportNowBtn:hover {
    background-color: #2277cc;
}
QPushButton#reportNowBtn:disabled {
    background-color: #2d2d3f;
    border-color: #3d3d55;
    color: #555577;
}

QPushButton#settingsBtn {
    background-color: transparent;
    border: 1px solid #3d3d55;
    color: #aaaacc;
    padding: 4px 18px;
}
QPushButton#settingsBtn:hover {
    background-color: #2d2d3f;
    border-color: #4a9eff;
    color: #e0e0e0;
}

QPushButton#toggleReportBtn {
    background-color: transparent;
    border: none;
    color: #4a9eff;
    text-align: left;
    font-size: 13px;
    padding: 4px 8px;
}
QPushButton#toggleReportBtn:hover {
    color: #80bfff;
}

/* Timer labels */
QLabel#timerLabel {
    color: #4a9eff;
    font-size: 48px;
    font-weight: bold;
    font-family: "Courier New", monospace;
}
QLabel#timerHintLabel {
    color: #6666aa;
    font-size: 12px;
}
QLabel#sectionLabel {
    color: #888899;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
}

/* Report area */
QTextEdit#reportText {
    background-color: #16162a;
    border: 1px solid #2d2d55;
    border-radius: 6px;
    padding: 12px;
    color: #ccccee;
    font-size: 13px;
    line-height: 1.5;
}

/* Status bar */
QLabel#statusLabel {
    color: #556688;
    font-size: 11px;
    padding: 2px 8px;
}

/* Inputs */
QLineEdit, QSpinBox, QComboBox {
    background-color: #16162a;
    border: 1px solid #3d3d55;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e0e0e0;
    selection-background-color: #1a6bbf;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #4a9eff;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #aaaacc;
    width: 0;
    height: 0;
    margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: #1e1e2e;
    border: 1px solid #3d3d55;
    selection-background-color: #2d4468;
    color: #e0e0e0;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #2d2d55;
    background-color: #1e1e2e;
}
QTabBar::tab {
    background-color: #16162a;
    color: #888899;
    border: 1px solid #2d2d55;
    border-bottom: none;
    padding: 6px 16px;
}
QTabBar::tab:selected {
    background-color: #1e1e2e;
    color: #e0e0e0;
    border-color: #4a9eff;
}

/* Tables */
QTableWidget {
    background-color: #16162a;
    alternate-background-color: #1a1a2e;
    gridline-color: #2d2d55;
    color: #e0e0e0;
    border: 1px solid #2d2d55;
}
QTableWidget::item:selected {
    background-color: #2d4468;
}
QHeaderView::section {
    background-color: #252538;
    color: #aaaacc;
    border: none;
    border-right: 1px solid #2d2d55;
    padding: 6px 8px;
    font-weight: bold;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #16162a;
    width: 8px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #3d3d55;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #4a9eff;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* Menus */
QMenu {
    background-color: #1e1e2e;
    border: 1px solid #3d3d55;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    border-radius: 4px;
    color: #e0e0e0;
}
QMenu::item:selected {
    background-color: #2d4468;
}
QMenu::item:disabled {
    color: #444466;
}
QMenu::separator {
    height: 1px;
    background-color: #2d2d55;
    margin: 4px 0;
}

/* Dialog buttons */
QDialogButtonBox QPushButton {
    min-width: 80px;
}

/* Group boxes */
QGroupBox {
    border: 1px solid #2d2d55;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
    color: #888899;
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
    color: #ccccee;
    spacing: 8px;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #3d3d55;
    border-radius: 3px;
    background-color: #16162a;
}
QCheckBox::indicator:checked {
    background-color: #1a6bbf;
    border-color: #4a9eff;
}
QRadioButton::indicator {
    border-radius: 8px;
}
QRadioButton::indicator:checked {
    background-color: #1a6bbf;
    border-color: #4a9eff;
}

/* Splitter */
QSplitter::handle {
    background-color: #2d2d55;
}

/* Label */
QLabel {
    color: #ccccee;
}
"""
