# controller/enrollment_windows.py

from typing import Optional, Dict, Tuple, List

import mysql.connector
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QDialog, QCheckBox

from model.helpers import normalize_doc
from model.enrollment_queue import get_next_student_id
from model.students import update_student_full, get_section_count
from model.schedule import schedule_from_section, section_number
from model.enrollment_services import (
    queue_student_for_payment,
    load_enrolled_students,
    load_payment_queue,
    remove_payment_queue_student,
    mark_payment_unpaid,
    approve_payment_queue_student,
)

from controller.ui_loader import (
    Ui_EnrollmentDashboard,
    Ui_ManagementDashboard,
    Ui_Payment,
)
from controller.ui_utils import RegistrarBaseWindow, safe_connect
from controller.dialogs import GenericAssignmentDialog, StudentDetailsDialog
from controller import app_state


TEACHER_LABEL_MAP = {
    "comboBox_3": "label_22",
    "comboBox_4": "label_23",
    "comboBox_5": "label_25",
    "comboBox_6": "label_26",
    "comboBox_7": "label_27",
}


def _teacher_option_index_for_section(section: str) -> int:
    number = section_number(section)
    return int(number) if number.isdigit() else 0


def _clean_teacher_name(value: str) -> str:
    teacher = str(value or "").strip()
    return "" if teacher.lower().startswith("select") else teacher


class EnrollmentDashboardWindow(RegistrarBaseWindow):
    def __init__(self):
        super().__init__()
        if Ui_EnrollmentDashboard is None:
            QMessageBox.critical(self, "Missing UI", "enrollmentDashboard_ui.py not found.")
            return

        self.ui = Ui_EnrollmentDashboard()
        self.ui.setupUi(self)

        self.assignment_windows: Dict[Tuple[str, str], "AssignmentWindowBase"] = {}
        safe_connect(getattr(self.ui, "pushButton_5", None), self.proceed_to_assignment)

    def clear_form(self):
        for name in ("textEdit", "textEdit_2", "textEdit_3", "textEdit_4"):
            w = getattr(self.ui, name, None)
            if w is not None:
                w.clear()

        for name in ("comboBox", "comboBox_2", "comboBox_3", "comboBox_4", "comboBox_5"):
            cb = getattr(self.ui, name, None)
            if cb is not None and cb.count() > 0:
                cb.setCurrentIndex(0)

    def proceed_to_assignment(self):
        first_name = self.ui.textEdit.toPlainText().strip()
        last_name = self.ui.textEdit_2.toPlainText().strip()
        email = self.ui.textEdit_3.toPlainText().strip()
        contact = self.ui.textEdit_4.toPlainText().strip()

        grade_level_raw = self.ui.comboBox.currentText().strip()
        strand_raw = self.ui.comboBox_2.currentText().strip()

        form_137 = normalize_doc(self.ui.comboBox_3.currentText())
        form_138 = normalize_doc(self.ui.comboBox_4.currentText())
        birth_cert = normalize_doc(self.ui.comboBox_5.currentText())

        if not all([first_name, last_name, email, contact, grade_level_raw, strand_raw]):
            QMessageBox.warning(self, "Incomplete", "Information not filled. Please complete all fields.")
            return

        grade = "11" if "11" in grade_level_raw else "12" if "12" in grade_level_raw else grade_level_raw
        strand = strand_raw.strip().upper()

        try:
            student_id = get_next_student_id()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to generate student ID:\n{e}")
            return

        pending = {
            "student_id": student_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "contact_number": contact,
            "grade_level": grade,
            "strand": strand,
            "form_137": form_137,
            "form_138": form_138,
            "birth_certificate": birth_cert,
            "schedule": ""
        }

        assign_window = self.assignment_windows.get((strand, grade))

        if assign_window is None:
            dlg = GenericAssignmentDialog(self, pending)
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return
            selected_grade, section, assignments = dlg.get_result()
            pending["grade_level"] = selected_grade

            # --- SLOT VERIFICATION ---
            enrolled_count = get_section_count(strand, selected_grade, section)
            if enrolled_count >= 50:
                QMessageBox.warning(self, "No Slots Available",
                                    f"Section '{section}' is currently FULL (50/50 slots taken).\n\nPlease select another section.")
                return

            missing = [sub for sub, t in assignments.items() if not t]
            if missing:
                QMessageBox.warning(self, "Teacher Required", "Fill teacher names:\n- " + "\n- ".join(missing))
                return

            try:
                queue_student_for_payment(pending, section, assignments)
            except mysql.connector.IntegrityError:
                QMessageBox.warning(self, "Duplicate", "Already in payment queue.")
                return
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed:\n{e}")
                return

            QMessageBox.information(self, "Waiting Approval", "Student sent to PAYMENT for approval.")
            self.clear_form()
            if hasattr(self, 'payment'):
                self.payment.load_queue()
                self.switch_to(self.payment)
            return

        assign_window.set_pending_student(pending)
        self.switch_to(assign_window)


class AssignmentWindowBase(RegistrarBaseWindow):
    def __init__(self, ui_cls, strand: str, grade: str):
        super().__init__()
        if ui_cls is None:
            raise RuntimeError(f"Missing assignment UI for {strand}{grade}")

        self.ui = ui_cls()
        self.ui.setupUi(self)

        self.strand = strand
        self.grade = grade
        self.pending_student: Optional[dict] = None

        self.section_boxes: List[QCheckBox] = self._find_section_checkboxes()
        for cb in self.section_boxes:
            cb.stateChanged.connect(self._enforce_single_section)

        self.schedule_boxes: List[QCheckBox] = self._find_schedule_checkboxes()
        for cb in self.schedule_boxes:
            cb.stateChanged.connect(self._enforce_single_schedule)
            cb.setEnabled(False)
            cb.setToolTip("Schedule is auto-selected from the selected section.")

        self._prepare_teacher_combos()

        safe_connect(getattr(self.ui, "pushButton_5", None), self.on_next)

    def _prepare_teacher_combos(self):
        for cb_name in TEACHER_LABEL_MAP:
            cb = getattr(self.ui, cb_name, None)
            if cb is not None:
                cb.setEnabled(False)
                cb.setToolTip("Teacher is auto-selected from the selected section.")

    def _find_section_checkboxes(self) -> List[QCheckBox]:
        boxes: List[QCheckBox] = []
        for cb in self.findChildren(QCheckBox):
            name = (cb.objectName() or "").lower()
            text = (cb.text() or "").strip().upper()
            if name.startswith("checkbox") and text not in ("MORNING", "AFTERNOON", "EVENING"):
                boxes.append(cb)
        boxes.sort(key=lambda x: (x.objectName() or ""))
        return boxes

    def _find_schedule_checkboxes(self) -> List[QCheckBox]:
        boxes: List[QCheckBox] = []
        for cb in self.findChildren(QCheckBox):
            text = (cb.text() or "").strip().upper()
            if text in ("MORNING", "AFTERNOON", "EVENING"):
                boxes.append(cb)
        return boxes

    def _enforce_single_section(self):
        sender = self.sender()
        if sender is None or not isinstance(sender, QCheckBox):
            return
        if sender.isChecked():
            for cb in self.section_boxes:
                if cb is not sender:
                    cb.blockSignals(True)
                    cb.setChecked(False)
                    cb.blockSignals(False)
            self._select_schedule_for_section(sender.text())
            self._select_teachers_for_section(sender.text())

    def _enforce_single_schedule(self):
        sender = self.sender()
        if sender is None or not isinstance(sender, QCheckBox):
            return
        if sender.isChecked():
            for cb in self.schedule_boxes:
                if cb is not sender:
                    cb.blockSignals(True)
                    cb.setChecked(False)
                    cb.blockSignals(False)

    def _select_schedule_for_section(self, section: str):
        mapped_schedule = schedule_from_section(section)
        if not mapped_schedule:
            return
        selected = False
        for cb in self.schedule_boxes:
            if cb.text().strip().upper() == mapped_schedule and not selected:
                cb.blockSignals(True)
                cb.setChecked(True)
                cb.blockSignals(False)
                selected = True
            else:
                cb.blockSignals(True)
                cb.setChecked(False)
                cb.blockSignals(False)

    def _select_teachers_for_section(self, section: str):
        option_index = _teacher_option_index_for_section(section)
        if option_index <= 0:
            return

        for cb_name in TEACHER_LABEL_MAP:
            cb = getattr(self.ui, cb_name, None)
            if cb is not None and cb.count() > option_index:
                cb.blockSignals(True)
                cb.setCurrentIndex(option_index)
                cb.blockSignals(False)

    def set_pending_student(self, pending: dict):
        self.pending_student = pending
        info_lbl = getattr(self.ui, "label_24", None)
        if info_lbl is not None:
            info_lbl.setText(
                f"{pending.get('student_id', '')} | {pending.get('last_name', '')}, {pending.get('first_name', '')} | "
                f"{pending.get('strand', '')} {pending.get('grade_level', '')}"
            )

        for cb_name in TEACHER_LABEL_MAP:
            cb = getattr(self.ui, cb_name, None)
            if cb is not None and cb.count() > 0:
                cb.setCurrentIndex(0)

        for cb in self.section_boxes + self.schedule_boxes:
            cb.setChecked(False)

    def _get_selected_section(self) -> Optional[str]:
        checked = [cb.text().strip() for cb in self.section_boxes if cb.isChecked()]
        return checked[0] if len(checked) == 1 else None

    def _get_selected_schedule(self) -> Optional[str]:
        checked = {cb.text().strip().upper() for cb in self.schedule_boxes if cb.isChecked()}
        return next(iter(checked)) if len(checked) == 1 else None

    def _collect_assignments(self) -> dict:
        section = self._get_selected_section()
        if section:
            self._select_teachers_for_section(section)

        assignments = {}
        for cb_name, lbl_name in TEACHER_LABEL_MAP.items():
            cb = getattr(self.ui, cb_name, None)
            if cb is None:
                continue
            lbl = getattr(self.ui, lbl_name, None)
            subject = lbl.text().strip() if lbl is not None else cb_name
            assignments[subject] = _clean_teacher_name(cb.currentText())
        return assignments

    def on_next(self):
        if not self.pending_student:
            QMessageBox.warning(self, "No Student", "No pending student loaded.")
            return

        section = self._get_selected_section()
        if not section:
            QMessageBox.warning(self, "Section Required", "Please select EXACTLY ONE section.")
            return

        # --- SLOT VERIFICATION ---
        enrolled_count = get_section_count(self.strand, self.grade, section)
        if enrolled_count >= 50:
            QMessageBox.warning(self, "No Slots Available",
                                f"Section '{section}' is currently FULL (50/50 slots taken).\n\nPlease select another section.")
            return

        schedule = self._get_selected_schedule()
        if self.schedule_boxes and not schedule:
            QMessageBox.warning(self, "Schedule Required", "Please select a SCHEDULE (Morning/Afternoon/Evening).")
            return

        assignments = self._collect_assignments()
        missing = [sub for sub, t in assignments.items() if not t]
        if missing:
            QMessageBox.warning(self, "Teacher Required", "Missing:\n- " + "\n- ".join(missing))
            return

        student = dict(self.pending_student)
        student["section"] = section
        student["schedule"] = schedule or ""

        try:
            queue_student_for_payment(student, section, assignments)
        except mysql.connector.IntegrityError:
            QMessageBox.warning(self, "Duplicate", "Already in payment queue.")
            return
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed:\n{e}")
            return

        QMessageBox.information(self, "Waiting Approval", "Student sent to PAYMENT for approval.")
        if hasattr(self, 'enrollment'):
            self.enrollment.clear_form()
        if hasattr(self, 'payment'):
            self.payment.load_queue()
            self.switch_to(self.payment)


class ManagementDashboardWindow(RegistrarBaseWindow):
    def __init__(self):
        super().__init__()
        if Ui_ManagementDashboard is None:
            QMessageBox.critical(self, "Missing UI", "managementDashboard_ui.py not found.")
            return

        self.ui = Ui_ManagementDashboard()
        self.ui.setupUi(self)

        self.table = getattr(self.ui, "tableWidget", None)
        self.search_bar = getattr(self.ui, "textEdit", None)

        if self.table:
            self.table.setRowCount(0)
            try:
                self.table.cellDoubleClicked.disconnect()
            except Exception:
                pass
            self.table.cellDoubleClicked.connect(self.on_row_double_clicked)

        if self.search_bar:
            self.search_bar.textChanged.connect(self.perform_search)

        self.load_students()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_students()

    def load_students(self):
        if self.table is None:
            return

        try:
            rows = load_enrolled_students()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load:\n{e}")
            return

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            docs = (
                f"137:{normalize_doc(row.get('form_137'))} | "
                f"138:{normalize_doc(row.get('form_138'))} | "
                f"BC:{normalize_doc(row.get('birth_certificate'))}"
            )
            name = f"{row.get('last_name', '')}, {row.get('first_name', '')}"

            values = [
                row.get("student_id", ""),
                name,
                row.get("strand", ""),
                str(row.get("grade_level", "")),
                row.get("schedule", "") if "schedule" in row else "",
                docs,
                row.get("status", ""),
            ]
            for c, v in enumerate(values):
                item = QTableWidgetItem(str(v))
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()
        self.perform_search()

    def perform_search(self):
        if not self.search_bar or not self.table:
            return

        if hasattr(self.search_bar, "toPlainText"):
            search_text = self.search_bar.toPlainText().lower().strip()
        else:
            search_text = self.search_bar.text().lower().strip()

        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            name_item = self.table.item(row, 1)

            id_text = id_item.text().lower() if id_item else ""
            name_text = name_item.text().lower() if name_item else ""

            if search_text in id_text or search_text in name_text:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def on_row_double_clicked(self, row: int, col: int):
        if self.table is None:
            return
        sid_item = self.table.item(row, 0)
        if not sid_item:
            return
        student_id = sid_item.text().strip()
        if not student_id:
            return

        dlg = StudentDetailsDialog(self, student_id)
        result = dlg.exec()

        if result == QDialog.DialogCode.Accepted:
            data, assignments = dlg.get_data()
            try:
                update_student_full(student_id, data, assignments)
            except Exception as e:
                QMessageBox.critical(self, "Save Failed", f"Could not update student:\n{e}")
                return
            QMessageBox.information(self, "Saved", "Student updated successfully.")
            self.load_students()

        elif result == 2:
            QMessageBox.information(self, "Removed", "Student successfully removed from the system.")
            self.load_students()


class PaymentWindow(RegistrarBaseWindow):
    def __init__(self):
        super().__init__()
        if Ui_Payment is None:
            QMessageBox.critical(self, "Missing UI", "payment_ui.py not found.")
            return

        self.ui = Ui_Payment()
        self.ui.setupUi(self)

        self.table = getattr(self.ui, "tableWidget", None)
        if self.table:
            self.table.setRowCount(0)
            self.table.cellClicked.connect(self.on_row_clicked)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_queue()

    def load_queue(self):
        if self.table is None:
            return

        try:
            rows = load_payment_queue()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load queue:\n{e}")
            return

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            sid = row.get("student_id", "")
            name = f"{row.get('last_name', '')}, {row.get('first_name', '')}"
            docs = (
                f"137:{normalize_doc(row.get('form_137'))} | "
                f"138:{normalize_doc(row.get('form_138'))} | "
                f"BC:{normalize_doc(row.get('birth_certificate'))}"
            )
            values = [
                sid,
                name,
                row.get("strand", ""),
                str(row.get("grade_level", "")),
                docs,
                row.get("payment_status", "Unpaid"),
            ]
            for c, v in enumerate(values):
                item = QTableWidgetItem(str(v))
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()

    def on_row_clicked(self, row: int, col: int):
        if self.table is None:
            return
        sid_item = self.table.item(row, 0)
        if not sid_item:
            return
        student_id = sid_item.text().strip()
        if not student_id:
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Payment Status")
        msg.setText(f"Student ID: {student_id}\n\nChoose:")
        btn_paid = msg.addButton("Paid (Approve)", QMessageBox.ButtonRole.AcceptRole)
        btn_unpaid = msg.addButton("Unpaid", QMessageBox.ButtonRole.DestructiveRole)
        btn_remove = msg.addButton("Remove", QMessageBox.ButtonRole.ActionRole)
        msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == btn_paid:
            self.approve_payment(student_id)
        elif clicked == btn_unpaid:
            self.set_unpaid(student_id)
        elif clicked == btn_remove:
            self.remove_payment(student_id)

    def remove_payment(self, student_id: str):
        reply = QMessageBox.question(
            self, 'Confirm Remove',
            f"Are you sure you want to permanently remove {student_id} from the system?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                remove_payment_queue_student(student_id)
            except Exception as e:
                pass

            QMessageBox.information(self, "Removed", "Student successfully removed from the queue.")
            self.load_queue()

    def set_unpaid(self, student_id: str):
        try:
            mark_payment_unpaid(student_id)
        except Exception:
            pass

        self.load_queue()

    def approve_payment(self, student_id: str):
        try:
            approved = approve_payment_queue_student(student_id, app_state.CURRENT_REGISTRAR_DB_ID)
            if not approved:
                return
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to approve:\n{e}")
            return

        try:
            if hasattr(self, 'management'):
                self.management.load_students()
            if hasattr(self, 'dashboard'):
                self.dashboard.refresh_counts()
        except Exception:
            pass

        QMessageBox.information(self, "Approved", "Student moved to MANAGEMENT (Enrolled).")
        self.load_queue()
