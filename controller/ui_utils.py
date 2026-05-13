# controller/ui_utils.py

from typing import Optional
from PyQt6.QtCore import QEvent, QObject, Qt, QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
)


def safe_connect(button, handler):
    if button is None:
        return
    try:
        button.clicked.disconnect()
    except Exception:
        pass
    button.clicked.connect(handler)


class _PasswordToggleClickFilter(QObject):
    def __init__(self, toggle_handler, parent=None):
        super().__init__(parent)
        self._toggle_handler = toggle_handler

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.MouseButtonRelease:
            self._toggle_handler()
            event.accept()
            return True
        return super().eventFilter(watched, event)


def attach_password_toggle(line_edit: QLineEdit, eye_widget: Optional[QLabel] = None):
    if line_edit is None:
        return
    line_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def _toggle():
        if line_edit.echoMode() == QLineEdit.EchoMode.Password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)

    if eye_widget is not None:
        try:
            eye_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            eye_widget.setToolTip("Show/Hide Password")
            eye_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            eye_widget.raise_()

            click_filter = _PasswordToggleClickFilter(_toggle, eye_widget)
            eye_widget.installEventFilter(click_filter)
            filters = getattr(line_edit, "_password_toggle_filters", [])
            filters.append(click_filter)
            line_edit._password_toggle_filters = filters
        except Exception:
            pass
        return

    icon_eye = QIcon.fromTheme("view-password")
    action = QAction(icon_eye, "Toggle Password", line_edit)
    action.triggered.connect(_toggle)
    line_edit.addAction(action, QLineEdit.ActionPosition.TrailingPosition)


def apply_portal_table_style(table: Optional[QTableWidget]):
    if table is None:
        return

    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.setWordWrap(False)
    table.setSortingEnabled(False)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    table.setCornerButtonEnabled(False)

    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(44)
    table.verticalHeader().setMinimumSectionSize(40)

    header = table.horizontalHeader()
    header.setHighlightSections(False)
    header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    header.setMinimumSectionSize(120)
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    header.setStretchLastSection(True)

    table.setStyleSheet("""
        QTableWidget {
            background-color: #ffffff;
            alternate-background-color: #f6f8fb;
            border: 1px solid #d9e2ec;
            border-radius: 8px;
            color: #263238;
            font-size: 12px;
            selection-background-color: #d9ebff;
            selection-color: #102a43;
        }
        QTableWidget::item {
            border-bottom: 1px solid #e8eef5;
            padding: 8px 10px;
        }
        QTableWidget::item:selected {
            background-color: #d9ebff;
            color: #102a43;
        }
        QHeaderView::section {
            background-color: #243b53;
            border: none;
            border-right: 1px solid #344e6b;
            color: #ffffff;
            font-weight: 700;
            padding: 10px;
        }
        QHeaderView::section:first {
            border-top-left-radius: 8px;
        }
        QHeaderView::section:last {
            border-top-right-radius: 8px;
            border-right: none;
        }
        QScrollBar:vertical {
            background: #eef3f8;
            border: none;
            margin: 0;
            width: 12px;
        }
        QScrollBar::handle:vertical {
            background: #9fb3c8;
            border-radius: 6px;
            min-height: 30px;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
        }
        QScrollBar:horizontal {
            background: #eef3f8;
            border: none;
            height: 12px;
            margin: 0;
        }
        QScrollBar::handle:horizontal {
            background: #9fb3c8;
            border-radius: 6px;
            min-width: 30px;
        }
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0;
        }
    """)


def apply_portal_tables(window: QMainWindow):
    for table in window.findChildren(QTableWidget):
        apply_portal_table_style(table)


class SwitchableWindow(QMainWindow):
    _nav_lock = False

    def switch_to(self, target: Optional["SwitchableWindow"]):
        if target is None or target is self:
            return
        if SwitchableWindow._nav_lock:
            return

        SwitchableWindow._nav_lock = True
        try:
            target.show()
            target.raise_()
            target.activateWindow()
            self.hide()
        finally:
            QTimer.singleShot(0, lambda: setattr(SwitchableWindow, "_nav_lock", False))


class AdminBaseWindow(SwitchableWindow):
    def connect_sidebar(self):
        apply_portal_tables(self)
        safe_connect(getattr(self.ui, "pushButton", None), lambda: self.switch_to(self.dashboard))
        safe_connect(getattr(self.ui, "pushButton_2", None), lambda: self.switch_to(self.management))
        safe_connect(getattr(self.ui, "pushButton_3", None), lambda: self.switch_to(self.reports))
        safe_connect(getattr(self.ui, "pushButton_4", None), lambda: self.switch_to(self.login))


class RegistrarBaseWindow(SwitchableWindow):
    def connect_sidebar(self):
        apply_portal_tables(self)
        # Bind the core known sidebar items
        safe_connect(getattr(self.ui, "pushButton", None), lambda: self.switch_to(self.dashboard))
        safe_connect(getattr(self.ui, "pushButton_2", None), lambda: self.switch_to(self.enrollment))
        safe_connect(getattr(self.ui, "pushButton_3", None), lambda: self.switch_to(self.management))
        safe_connect(getattr(self.ui, "pushButton_4", None), lambda: self.switch_to(self.login))

        # Dynamically link Payment and Slots so we don't accidentally override the Next buttons
        for btn in self.findChildren(QPushButton):
            text = btn.text().strip().lower()
            if text == "payment":
                safe_connect(btn, lambda: self.switch_to(getattr(self, 'payment', None)))
            elif text == "slots":
                safe_connect(btn, lambda: self.switch_to(getattr(self, 'slots', None)))
