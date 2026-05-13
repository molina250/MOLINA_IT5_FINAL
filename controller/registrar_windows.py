# controller/registrar_windows.py

import mysql.connector
from PyQt6.QtWidgets import QMessageBox, QPushButton, QSizePolicy, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QRect, QTimer

from model.dashboard import get_registrar_dashboard_counts
from model.registrars import authenticate_registrar, create_registrar_account

from controller.ui_loader import (
    Ui_RegistrarLogin,
    Ui_CreateAccount,
    Ui_RegistrarDashboard,
    Ui_Slots,
    _try_import_ui
)
from controller.ui_utils import RegistrarBaseWindow, SwitchableWindow, safe_connect, attach_password_toggle
from controller.graphs import StrandEnrollmentGraph, AvailableSlotsGraph
from controller import app_state

# Dynamic loading for Slots UI
Ui_Slots = _try_import_ui("slots_ui")


def _create_graph_host(parent, object_name, geometry):
    host = QWidget(parent)
    host.setObjectName(object_name)
    host.setGeometry(geometry)
    host.setStyleSheet("background: transparent; border: none;")
    host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    host.show()
    host.raise_()
    return host, layout


class RegistrarLoginWindow(SwitchableWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_RegistrarLogin()
        self.ui.setupUi(self)

        # Setup UI password toggle if available
        if hasattr(self.ui, 'lineEdit_2'):
            attach_password_toggle(self.ui.lineEdit_2, getattr(self.ui, 'label_8', None))

        # Connect Primary Login Button safely
        if hasattr(self.ui, 'btnLogin'):
            safe_connect(self.ui.btnLogin, self.handle_login)
        elif hasattr(self.ui, 'pushButton'):  # Fallback for default UI name
            safe_connect(self.ui.pushButton, self.handle_login)

        # Find and connect the "Create Account" and "Admin" buttons by text
        # This prevents crashes if the UI buttons are named differently
        self._connect_navigation_buttons()

    def _connect_navigation_buttons(self):
        for btn in self.findChildren(QPushButton):
            text = btn.text().strip().lower()
            if "create" in text and "account" in text:
                safe_connect(btn, self.go_to_create_account)
            elif "admin" in text:
                safe_connect(btn, self.go_to_admin_login)

    def go_to_create_account(self):
        # Look for the variable, preventing crashes if app_wiring missed it
        target = getattr(self, 'create_account', getattr(self, 'create_account_win', None))
        if target:
            self.switch_to(target)
        else:
            QMessageBox.critical(self, "Wiring Error", "Create Account window is not linked. Update app_wiring.py.")

    def go_to_admin_login(self):
        # Look for the Admin Login variable
        target = getattr(self, 'admin_login', None)
        if target:
            self.switch_to(target)
        else:
            QMessageBox.critical(self, "Wiring Error", "Admin Login window is not linked. Update app_wiring.py.")

    def handle_login(self):
        username = self.ui.lineEdit.text().strip() if hasattr(self.ui, 'lineEdit') else ""
        password = self.ui.lineEdit_2.text().strip() if hasattr(self.ui, 'lineEdit_2') else ""

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both your Registrar ID and Password.")
            return

        try:
            registrar_db_id = authenticate_registrar(username, password)
            if registrar_db_id is not None:
                # Store session
                app_state.CURRENT_REGISTRAR_DB_ID = registrar_db_id
                if hasattr(self.ui, 'lineEdit_2'):
                    self.ui.lineEdit_2.clear()

                    # Switch to dashboard
                target_dashboard = getattr(self, 'dashboard', getattr(self, 'registrar_dashboard', None))
                if target_dashboard:
                    self.switch_to(target_dashboard)
                else:
                    QMessageBox.warning(self, "Wiring Error", "Registrar Dashboard is not linked.")
            else:
                QMessageBox.critical(self, "Login Failed", "Invalid Registrar ID or Password.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not connect to database:\n{e}")


class CreateAccountWindow(SwitchableWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_CreateAccount()
        self.ui.setupUi(self)

        # Connect main buttons safely
        if hasattr(self.ui, 'pushButton'):
            safe_connect(self.ui.pushButton, self.handle_registration)
        if hasattr(self.ui, 'pushButton_2'):
            safe_connect(self.ui.pushButton_2, self.go_back)

    def handle_registration(self):
        name = self.ui.lineEdit.text().strip() if hasattr(self.ui, 'lineEdit') else ""
        contact = self.ui.lineEdit_2.text().strip() if hasattr(self.ui, 'lineEdit_2') else ""
        email = self.ui.lineEdit_3.text().strip() if hasattr(self.ui, 'lineEdit_3') else ""
        reg_id = self.ui.lineEdit_4.text().strip() if hasattr(self.ui, 'lineEdit_4') else ""
        password = self.ui.lineEdit_5.text().strip() if hasattr(self.ui, 'lineEdit_5') else ""

        # Validate inputs - check each field individually
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter your Full Name.")
            return

        if not email:
            QMessageBox.warning(self, "Input Error", "Please enter your Email Address.")
            return

        if not reg_id:
            QMessageBox.warning(self, "Input Error", "Please enter your Registrar ID.")
            return

        if not password:
            QMessageBox.warning(self, "Input Error", "Please enter a Password.")
            return

        # Validate email format (must contain @ and have domain)
        if '@' not in email or '.' not in email.split('@')[-1]:
            QMessageBox.warning(self, "Input Error",
                                f"'{email}' is not a valid email address. Please enter a valid email (e.g., name@example.com).")
            return

        # Validate password length
        if len(password) < 4:
            QMessageBox.warning(self, "Input Error", "Password must be at least 4 characters long.")
            return

        try:
            create_registrar_account(name, contact, email, reg_id, password)

            QMessageBox.information(self, "Success", "Registrar account created successfully!")
            admin_dashboard = getattr(self, "admin_dashboard", None)
            if admin_dashboard and hasattr(admin_dashboard, "refresh_dashboard"):
                admin_dashboard.refresh_dashboard()
            admin_management = getattr(self, "admin_management", None)
            if admin_management and hasattr(admin_management, "load_registrars"):
                admin_management.load_registrars()

            # Clear fields after creation
            for attr in ['lineEdit', 'lineEdit_2', 'lineEdit_3', 'lineEdit_4', 'lineEdit_5']:
                if hasattr(self.ui, attr):
                    getattr(self.ui, attr).clear()

            self.go_back()

        except mysql.connector.Error as err:
            if err.errno == 1062:
                if 'email' in str(err).lower():
                    QMessageBox.critical(self, "Registration Error",
                                         "This email is already registered. Please use a different email.")
                else:
                    QMessageBox.critical(self, "Registration Error",
                                         "This Registrar ID is already taken. Please use a different ID.")
            elif err.errno == 1048:
                QMessageBox.critical(self, "Registration Error",
                                     "All fields are required. Please fill in all information.")
            else:
                QMessageBox.critical(self, "Database Error", f"An error occurred:\n{err}")

    def go_back(self):
        # Safely determine where to return
        target_login = getattr(self, 'registrar', getattr(self, 'login', None))
        target_admin = getattr(self, 'admin_management', None)

        if target_login and not target_login.isVisible():
            self.switch_to(target_login)
        elif target_admin:
            self.switch_to(target_admin)
        else:
            self.close()


class RegistrarDashboardWindow(RegistrarBaseWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_RegistrarDashboard()
        self.ui.setupUi(self)

        if hasattr(self.ui, 'btnVerified'): safe_connect(self.ui.btnVerified, lambda: self.switch_to(self.management))
        if hasattr(self.ui, 'btnToFollow'): safe_connect(self.ui.btnToFollow, lambda: self.switch_to(self.management))
        if hasattr(self.ui, 'btnEnrolled'): safe_connect(self.ui.btnEnrolled, lambda: self.switch_to(self.management))
        self._prepare_count_cards()

        self.dashboard_timer = QTimer(self)
        self.dashboard_timer.setInterval(2000)
        self.dashboard_timer.timeout.connect(self.refresh_counts)
        self.dashboard_timer.start()
        self.refresh_counts()
        self.setup_graphs()

    def _prepare_count_cards(self):
        card_geometry = {
            "btnVerified": QRect(20, 70, 251, 55),
            "btnToFollow": QRect(50, 70, 281, 55),
            "btnEnrolled": QRect(30, 70, 261, 55),
        }
        for name, geometry in card_geometry.items():
            widget = getattr(self.ui, name, None)
            if widget is None:
                continue
            widget.setGeometry(geometry)
            widget.setStyleSheet("""
                QPushButton {
                    background-color: #eaeaea;
                    border: none;
                    color: #102a43;
                    font-size: 34px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    color: #1565c0;
                }
            """)

    def refresh_counts(self):
        try:
            counts = get_registrar_dashboard_counts()
        except Exception:
            counts = {"verified": 0, "to_follow": 0, "enrolled": 0}

        self._set_count_cards(counts)

    def _set_count_cards(self, counts):
        card_map = {
            "btnVerified": counts["verified"],
            "btnToFollow": counts["to_follow"],
            "btnEnrolled": counts["enrolled"],
        }
        for name, value in card_map.items():
            widget = getattr(self.ui, name, None)
            if widget is None:
                continue
            widget.setText(str(value))
            widget.setCursor(Qt.CursorShape.PointingHandCursor)
            widget.setToolTip("Open Management")

    def setup_graphs(self):
        if hasattr(self.ui, 'centralwidget'):
            self.graph_host, graph_layout = _create_graph_host(
                self.ui.centralwidget,
                "enrolledStudentsGraphHost",
                QRect(270, 395, 1340, 465)
            )
            self.graph = StrandEnrollmentGraph(self.graph_host)
            graph_layout.addWidget(self.graph)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_counts()
        if hasattr(self, 'graph'):
            self.graph.load_and_draw_data()


class RegistrarSlotsWindow(RegistrarBaseWindow):
    def __init__(self):
        super().__init__()
        if Ui_Slots:
            self.ui = Ui_Slots()
            self.ui.setupUi(self)
            self.setup_graphs()
        else:
            self.close()

    def setup_graphs(self):
        if hasattr(self.ui, 'centralwidget'):
            self.graph_host, graph_layout = _create_graph_host(
                self.ui.centralwidget,
                "availableSlotsGraphHost",
                QRect(270, 155, 1340, 705)
            )
            self.graph = AvailableSlotsGraph(self.graph_host)
            graph_layout.addWidget(self.graph)

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'graph'):
            self.graph.load_and_draw_data()
