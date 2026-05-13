# controller/admin_windows.py

from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtWidgets import (
    QMessageBox, QTableWidgetItem, QFileDialog, QDialog, QHeaderView, QPushButton
)

from model.dashboard import get_admin_dashboard_counts
from model.registrars import list_registrars, update_registrar_account
from model.admin_records import get_report_rows, get_enrollment_report_rows
from model.pdf_exports import export_strand_report_pdf, export_enrollment_report_pdf

from controller.ui_loader import (
    Ui_AdminLogin,
    Ui_AdminDashboard,
    Ui_AdminManagement,
    Ui_AdminReports,
    _try_import_ui
)
from controller.ui_utils import AdminBaseWindow, SwitchableWindow, safe_connect, attach_password_toggle
from controller.dialogs import RegistrarDetailsDialog

# Dynamically load the new Enrollment Reports UI
Ui_EnrollmentReports = _try_import_ui("enrollmentReports_ui")


class AdminLoginWindow(SwitchableWindow):
    def __init__(self):
        super().__init__()
        if Ui_AdminLogin is None:
            QMessageBox.critical(self, "Missing UI", "AdminLogin_ui.py not found.")
            return

        self.ui = Ui_AdminLogin()
        self.ui.setupUi(self)

        self.ADMIN_USERNAME = "Alexander2500"
        self.ADMIN_PASSWORD = "12345"

        line_edit_pw = getattr(self.ui, "lineEdit_2", None)
        line_edit_user = getattr(self.ui, "lineEdit", None)
        eye_label = getattr(self.ui, "label_8", None)

        if line_edit_pw:
            attach_password_toggle(line_edit_pw, eye_label)
            # Allow pressing Enter to login
            line_edit_pw.returnPressed.connect(self.login)
        if line_edit_user:
            line_edit_user.returnPressed.connect(self.login)

        # --- BUG FIX: ROBUST BUTTON BINDING ---
        # Finds buttons by their actual text to prevent variable name mix-ups from Qt Designer
        for btn in self.findChildren(QPushButton):
            text = btn.text().strip().lower()
            if "registrar" in text or "back" in text:
                safe_connect(btn, self.go_back)
            elif "login" in text:
                safe_connect(btn, self.login)

    def login(self):
        u_edit = getattr(self.ui, "lineEdit", None)
        p_edit = getattr(self.ui, "lineEdit_2", None)
        if not u_edit or not p_edit:
            return

        user = u_edit.text().strip()
        pwd = p_edit.text().strip()

        if user == self.ADMIN_USERNAME and pwd == self.ADMIN_PASSWORD:
            u_edit.clear()
            p_edit.clear()
            if hasattr(self, 'dashboard') and self.dashboard:
                self.dashboard.refresh_dashboard()
            self.switch_to(getattr(self, 'dashboard', None))
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid Admin Credentials.")

    def go_back(self):
        u_edit = getattr(self.ui, "lineEdit", None)
        p_edit = getattr(self.ui, "lineEdit_2", None)
        if u_edit: u_edit.clear()
        if p_edit: p_edit.clear()

        if hasattr(self, 'registrar_login') and self.registrar_login:
            self.switch_to(self.registrar_login)


class AdminDashboardWindow(AdminBaseWindow):
    def __init__(self):
        super().__init__()
        if Ui_AdminDashboard is None:
            QMessageBox.critical(self, "Missing UI", "AdminDashboard_ui.py not found.")
            return

        self.ui = Ui_AdminDashboard()
        self.ui.setupUi(self)
        count_label = getattr(self.ui, "label_10", None)
        if count_label:
            count_label.setGeometry(QRect(20, 65, 130, 50))
            count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            count_label.setStyleSheet("""
                QLabel {
                    background-color: #eaeaea;
                    border: none;
                    color: #102a43;
                    font-size: 30px;
                    font-weight: 700;
                }
            """)
        self.dashboard_timer = QTimer(self)
        self.dashboard_timer.setInterval(2000)
        self.dashboard_timer.timeout.connect(self.refresh_dashboard)
        self.dashboard_timer.start()
        self.refresh_dashboard()

    def connect_sidebar(self):
        super().connect_sidebar()
        for btn_name in ["pushButton_5", "pushButton_6"]:
            btn = getattr(self.ui, btn_name, None)
            if btn and "Enrollment" in btn.text():
                safe_connect(btn, lambda: self.switch_to(getattr(self, 'enrollment_reports', None)))

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_dashboard()

    def refresh_dashboard(self):
        try:
            counts = get_admin_dashboard_counts()
            reg_count = counts["registrars"]
            enrolled_count = counts["enrolled_students"]

            lbl_reg = getattr(self.ui, "label_12", None)
            lbl_reg_fallback = getattr(self.ui, "label_10", None)
            lbl_stu = getattr(self.ui, "label_14", None)

            if lbl_reg: lbl_reg.setText(str(reg_count))
            if lbl_reg_fallback: lbl_reg_fallback.setText(str(reg_count))
            if lbl_stu: lbl_stu.setText(str(enrolled_count))
        except Exception:
            pass


class AdminManagementWindow(AdminBaseWindow):
    def __init__(self):
        super().__init__()
        if Ui_AdminManagement is None:
            QMessageBox.critical(self, "Missing UI", "adminManagement_ui.py not found.")
            return

        self.ui = Ui_AdminManagement()
        self.ui.setupUi(self)

        self.table = getattr(self.ui, "tableWidget", None)
        self.search_bar = getattr(self.ui, "textEdit", None)
        if self.table:
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Name", "ID", "Email", "Contact Number"])
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
            self.table.cellDoubleClicked.connect(self.on_row_double_clicked)

        if self.search_bar:
            self.search_bar.textChanged.connect(self.perform_search)

        self.load_registrars()

    def connect_sidebar(self):
        super().connect_sidebar()
        for btn_name in ["pushButton_5", "pushButton_6"]:
            btn = getattr(self.ui, btn_name, None)
            if btn and "Enrollment" in btn.text():
                safe_connect(btn, lambda: self.switch_to(getattr(self, 'enrollment_reports', None)))

    def showEvent(self, event):
        super().showEvent(event)
        self.load_registrars()

    def load_registrars(self):
        if not self.table:
            return

        try:
            self.registrar_data = list_registrars()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load registrars:\n{e}")
            return

        self.table.setRowCount(len(self.registrar_data))
        for r, row in enumerate(self.registrar_data):
            self.table.setItem(r, 0, QTableWidgetItem(row.get("full_name", "")))
            self.table.setItem(r, 1, QTableWidgetItem(row.get("registrar_id", "")))
            self.table.setItem(r, 2, QTableWidgetItem(row.get("email", "")))
            self.table.setItem(r, 3, QTableWidgetItem(row.get("contact_number", "")))

        self.perform_search()

    def perform_search(self):
        if not self.table or not self.search_bar:
            return

        if hasattr(self.search_bar, "toPlainText"):
            search_text = self.search_bar.toPlainText().lower().strip()
        else:
            search_text = self.search_bar.text().lower().strip()

        for row in range(self.table.rowCount()):
            row_text = " ".join(
                self.table.item(row, col).text().lower()
                for col in range(self.table.columnCount())
                if self.table.item(row, col)
            )
            self.table.setRowHidden(row, bool(search_text and search_text not in row_text))

    def on_row_double_clicked(self, row: int, col: int):
        if not self.registrar_data or row >= len(self.registrar_data):
            return

        reg_data = self.registrar_data[row]
        dlg = RegistrarDetailsDialog(self, reg_data)
        result = dlg.exec()

        if result == QDialog.DialogCode.Accepted:
            updated = dlg.get_updated_data()
            try:
                update_registrar_account(reg_data['registrar_id'], updated)
                QMessageBox.information(self, "Success", "Registrar details updated.")
                self.load_registrars()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update:\n{e}")
        elif result == 2:
            QMessageBox.information(self, "Removed", "Registrar account removed.")
            self.load_registrars()


class AdminReportsWindow(AdminBaseWindow):
    def __init__(self):
        super().__init__()
        if Ui_AdminReports is None:
            QMessageBox.critical(self, "Missing UI", "adminReports_ui.py not found.")
            return

        self.ui = Ui_AdminReports()
        self.ui.setupUi(self)

        self.table = getattr(self.ui, "tableWidget", None)
        if self.table:
            self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)

        btn_print = getattr(self.ui, "pushButton_5", None)
        if btn_print:
            safe_connect(btn_print, self.download_pdf)

        self.load_reports()

    def connect_sidebar(self):
        super().connect_sidebar()
        for btn_name in ["pushButton_5", "pushButton_6"]:
            btn = getattr(self.ui, btn_name, None)
            if btn and "Enrollment" in btn.text():
                safe_connect(btn, lambda: self.switch_to(getattr(self, 'enrollment_reports', None)))

    def showEvent(self, event):
        super().showEvent(event)
        self.load_reports()

    def load_reports(self):
        if not self.table:
            return

        try:
            self.report_data = get_report_rows()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to fetch reports:\n{e}")
            return

        self.table.setRowCount(len(self.report_data))
        for r, row in enumerate(self.report_data):
            self.table.setItem(r, 0, QTableWidgetItem(row.get("strand", "")))
            self.table.setItem(r, 1, QTableWidgetItem(str(row.get("daily", 0))))
            self.table.setItem(r, 2, QTableWidgetItem(str(row.get("weekly", 0))))
            self.table.setItem(r, 3, QTableWidgetItem(str(row.get("monthly", 0))))
            self.table.setItem(r, 4, QTableWidgetItem(str(row.get("yearly", 0))))
            self.table.setItem(r, 5, QTableWidgetItem(str(row.get("total", 0))))

    def download_pdf(self):
        if not hasattr(self, 'report_data') or not self.report_data:
            QMessageBox.warning(self, "No Data", "There is no report data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save Strand Report", "Strand_Enrollment_Report.pdf",
                                              "PDF Files (*.pdf)")
        if not path:
            return

        try:
            export_strand_report_pdf(path, self.report_data)
            QMessageBox.information(self, "Success", "Report PDF saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF:\n{e}")


class AdminEnrollmentReportsWindow(AdminBaseWindow):
    """The new window linking specific students to the Registrar who enrolled them."""

    def __init__(self):
        super().__init__()
        if Ui_EnrollmentReports is None:
            QMessageBox.critical(self, "Missing UI", "enrollmentReports_ui.py not found.")
            return

        self.ui = Ui_EnrollmentReports()
        self.ui.setupUi(self)

        self.table = getattr(self.ui, "tableWidget", None)
        if self.table:
            self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)

        btn_print = getattr(self.ui, "pushButton_5", None)
        if btn_print:
            safe_connect(btn_print, self.download_pdf)

        self.enrollment_report_data = []
        self.load_enrollment_records()

    def connect_sidebar(self):
        super().connect_sidebar()
        for btn_name in ["pushButton_5", "pushButton_6"]:
            btn = getattr(self.ui, btn_name, None)
            if btn and "Enrollment" in btn.text():
                safe_connect(btn, lambda: self.switch_to(getattr(self, 'enrollment_reports', None)))

    def showEvent(self, event):
        super().showEvent(event)
        self.load_enrollment_records()

    def load_enrollment_records(self):
        if not self.table:
            return

        try:
            rows, has_sched, has_reg = get_enrollment_report_rows()
            self.enrollment_report_data = rows
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load records:\n{e}")
            return

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            name = f"{row.get('last_name', '')}, {row.get('first_name', '')}"
            schedule = row.get("schedule", "") if has_sched else ""

            registrar_display = "Unknown"
            if has_reg:
                reg_name = row.get("registrar_name")
                reg_acc = row.get("reg_account")
                if reg_name and reg_acc:
                    registrar_display = f"{reg_name} ({reg_acc})"
                elif reg_name:
                    registrar_display = reg_name

            self.table.setItem(r, 0, QTableWidgetItem(str(row.get("student_id", ""))))
            self.table.setItem(r, 1, QTableWidgetItem(name))
            self.table.setItem(r, 2, QTableWidgetItem(str(row.get("grade_level", ""))))
            self.table.setItem(r, 3, QTableWidgetItem(str(row.get("strand", ""))))
            self.table.setItem(r, 4, QTableWidgetItem(schedule))
            self.table.setItem(r, 5, QTableWidgetItem(registrar_display))

        self.table.resizeColumnsToContents()

    def download_pdf(self):
        if not getattr(self, "enrollment_report_data", None):
            QMessageBox.warning(self, "No Data", "There is no enrollment report data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Enrollment Report",
            "Enrollment_Reports_Per_Student.pdf",
            "PDF Files (*.pdf)",
        )
        if not path:
            return

        try:
            export_enrollment_report_pdf(path, self.enrollment_report_data)
            QMessageBox.information(self, "Success", "Enrollment report PDF saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF:\n{e}")
