# controller/app_wiring.py

import sys
from typing import Dict, Tuple

from PyQt6.QtWidgets import QApplication

from model.schema import (
    ensure_registrars_table,
    ensure_payment_queue_table,
    ensure_pending_enrollments_table_and_columns,
    ensure_student_optional_columns,
    ensure_reports_table_and_seed,
    ensure_slots_table_and_seed,
    ensure_enrollment_reports_table,
    sync_all_slots,
)
from model.reports import recalc_and_store_reports
from model.enrollment_reports import sync_enrollment_reports

from controller.ui_loader import (
    Ui_ABM11, Ui_ABM12, Ui_STEM11, Ui_STEM12,
    Ui_HUMSS11, Ui_HUMSS12, Ui_GAS11, Ui_GAS12,
    Ui_TVL11, Ui_TVL12,
)

from controller.admin_windows import (
    AdminLoginWindow,
    AdminDashboardWindow,
    AdminManagementWindow,
    AdminReportsWindow,
    AdminEnrollmentReportsWindow
)
from controller.registrar_windows import (
    RegistrarLoginWindow,
    CreateAccountWindow,
    RegistrarDashboardWindow,
    RegistrarSlotsWindow  # <-- ADDED SLOTS WINDOW
)
from controller.enrollment_windows import (
    EnrollmentDashboardWindow,
    ManagementDashboardWindow,
    PaymentWindow,
    AssignmentWindowBase,
)


def run_app():
    # 1. Database Initialization
    ensure_registrars_table()
    ensure_payment_queue_table()
    ensure_pending_enrollments_table_and_columns()
    ensure_student_optional_columns()
    ensure_reports_table_and_seed()
    ensure_slots_table_and_seed()
    ensure_enrollment_reports_table()
    recalc_and_store_reports()
    sync_all_slots()
    sync_enrollment_reports()

    app = QApplication(sys.argv)

    # -----------------------------
    # 2. Instantiate Windows
    # -----------------------------

    # Admin Module
    admin_login = AdminLoginWindow()
    admin_dashboard = AdminDashboardWindow()
    admin_management = AdminManagementWindow()
    admin_reports = AdminReportsWindow()
    admin_enrollment_reports = AdminEnrollmentReportsWindow()

    # Registrar Module
    registrar_login = RegistrarLoginWindow()
    create_account = CreateAccountWindow()
    registrar_dashboard = RegistrarDashboardWindow()

    enrollment_dashboard = EnrollmentDashboardWindow()
    management_dashboard = ManagementDashboardWindow()
    payment_window = PaymentWindow()
    slots_window = RegistrarSlotsWindow()  # <-- NEW: Instantiate the Slots window

    # Curriculum / Assignment Windows
    assignment_windows = {
        ("ABM", "11"): AssignmentWindowBase(Ui_ABM11, "ABM", "11"),
        ("ABM", "12"): AssignmentWindowBase(Ui_ABM12, "ABM", "12"),
        ("STEM", "11"): AssignmentWindowBase(Ui_STEM11, "STEM", "11"),
        ("STEM", "12"): AssignmentWindowBase(Ui_STEM12, "STEM", "12"),
        ("HUMSS", "11"): AssignmentWindowBase(Ui_HUMSS11, "HUMSS", "11"),
        ("HUMSS", "12"): AssignmentWindowBase(Ui_HUMSS12, "HUMSS", "12"),
        ("GAS", "11"): AssignmentWindowBase(Ui_GAS11, "GAS", "11"),
        ("GAS", "12"): AssignmentWindowBase(Ui_GAS12, "GAS", "12"),
        ("TVL", "11"): AssignmentWindowBase(Ui_TVL11, "TVL", "11"),
        ("TVL", "12"): AssignmentWindowBase(Ui_TVL12, "TVL", "12"),
    }
    enrollment_dashboard.assignment_windows = assignment_windows

    # -----------------------------
    # 3. Wiring (Inject Dependencies)
    # -----------------------------

    # Link Admin Login to Registrar Login
    admin_login.registrar_login = registrar_login
    admin_login.dashboard = admin_dashboard

    # Link Admin Navigation Loop
    admin_pages = [
        admin_dashboard,
        admin_management,
        admin_reports,
        admin_enrollment_reports
    ]

    for page in admin_pages:
        page.dashboard = admin_dashboard
        page.management = admin_management
        page.reports = admin_reports
        page.enrollment_reports = admin_enrollment_reports
        page.login = admin_login
        page.connect_sidebar()

    # Link Registrar Navigation Base
    registrar_login.admin_login = admin_login
    registrar_login.create_account = create_account
    registrar_login.registrar_dashboard = registrar_dashboard

    create_account.registrar = registrar_login
    create_account.admin_dashboard = admin_dashboard
    create_account.admin_management = admin_management

    # Link Registrar Navigation Loop
    registrar_pages = [
                          registrar_dashboard,
                          enrollment_dashboard,
                          management_dashboard,
                          payment_window,
                          slots_window  # <-- Added to navigation loop
                      ] + list(assignment_windows.values())

    for page in registrar_pages:
        if getattr(page, "ui", None) is None:
            continue
        page.dashboard = registrar_dashboard
        page.enrollment = enrollment_dashboard
        page.management = management_dashboard
        page.payment = payment_window
        page.slots = slots_window  # <-- Setup dynamic mapping
        page.login = registrar_login
        page.connect_sidebar()

    # Extra links needed by specific enrollment flows
    for aw in assignment_windows.values():
        aw.enrollment = enrollment_dashboard
        aw.payment = payment_window

    payment_window.management = management_dashboard
    payment_window.dashboard = registrar_dashboard
    enrollment_dashboard.payment = payment_window

    # -----------------------------
    # 4. Start Application
    # -----------------------------
    registrar_login.show()
    sys.exit(app.exec())
