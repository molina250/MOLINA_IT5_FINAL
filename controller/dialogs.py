# controller/dialogs.py

from typing import Dict, List, Tuple, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDialogButtonBox,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QFileDialog
)

from model.helpers import normalize_doc, safe_load_assignments
from model.students import fetch_student_full, delete_student
from model.subjects import subjects_for
from model.registrars import delete_registrar_account
from model.pdf_exports import export_student_receipt_pdf
from model.schedule import schedule_from_section, section_number


def _teacher_option_index_for_section(section: str) -> int:
    number = section_number(section)
    if number.isdigit():
        return int(number)

    suffix = str(section or "").strip().upper().split()[-1:]
    return {"A": 1, "B": 2, "C": 3}.get(suffix[0], 0) if suffix else 0


def _clean_teacher_name(value: str) -> str:
    teacher = str(value or "").strip()
    return "" if teacher.lower().startswith("select") else teacher


class RegistrarDetailsDialog(QDialog):
    """Dialog to edit registrar account information triggered from Admin Management."""

    def __init__(self, parent, registrar_data: dict):
        super().__init__(parent)
        self.setWindowTitle("Edit Registrar Account")
        self.setMinimumWidth(400)

        # Store registrar ID for deletion logic
        self.registrar_id = registrar_data.get('registrar_id')

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.reg_id_lbl = QLabel(f"<b>{self.registrar_id}</b>")
        form.addRow("Registrar ID:", self.reg_id_lbl)

        self.full_name = QLineEdit(registrar_data.get('full_name', ''))
        self.email = QLineEdit(registrar_data.get('email', ''))
        self.contact = QLineEdit(registrar_data.get('contact_number', ''))
        self.username = QLineEdit(registrar_data.get('username', ''))

        form.addRow("Full Name:", self.full_name)
        form.addRow("Email:", self.email)
        form.addRow("Contact:", self.contact)
        form.addRow("Username:", self.username)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        self.btn_remove = QPushButton("Remove Registrar")
        self.btn_remove.setStyleSheet(
            "background-color: #dc3545; color: white; font-weight: bold; padding: 5px 10px; border-radius: 4px;")
        btn_row.addWidget(self.btn_remove)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.btn_remove.clicked.connect(self.remove_registrar)

    def remove_registrar(self):
        reply = QMessageBox.question(
            self, 'Confirm Remove',
            f"Are you sure you want to permanently remove Registrar {self.registrar_id} from the system?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_registrar_account(self.registrar_id)
                self.done(2)
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to remove registrar:\n{e}")

    def get_updated_data(self):
        return {
            "full_name": self.full_name.text().strip(),
            "email": self.email.text().strip(),
            "contact_number": self.contact.text().strip(),
            "username": self.username.text().strip()
        }


class GenericAssignmentDialog(QDialog):
    """Popup window to select Grade Level and Section with teachers auto-picked by section."""

    def __init__(self, parent, pending_student: dict):
        super().__init__(parent)
        self.setWindowTitle("Assign Curriculum & Teachers")
        self.setMinimumWidth(550)
        self.strand = pending_student.get('strand', 'ABM')

        self.teacher_list = [
            "Select Teacher...",
            "Andrew M. Lim",
            "Clarissa M. Villanueva",
            "Roberto D. Santos",
            "Maria K. Ramos",
            "Jonathan P. Reyes"
        ]

        self._teacher_combos: Dict[str, QComboBox] = {}
        self.layout = QVBoxLayout(self)
        self.form = QFormLayout()

        self.grade_box = QComboBox()
        self.grade_box.addItems(["11", "12"])
        self.grade_box.setCurrentText(str(pending_student.get('grade_level', '11')))
        self.form.addRow("Grade Level:", self.grade_box)

        self.section_box = QComboBox()
        self.form.addRow("Section:", self.section_box)
        self.layout.addLayout(self.form)

        self.subject_layout = QFormLayout()
        self.layout.addLayout(self.subject_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

        self.grade_box.currentTextChanged.connect(self.refresh_sections)
        self.grade_box.currentTextChanged.connect(self.refresh_subjects)
        self.section_box.currentTextChanged.connect(self.apply_section_teachers)
        self.refresh_sections()
        self.refresh_subjects()

    def refresh_sections(self):
        current = self.section_box.currentText()
        grade = self.grade_box.currentText()
        sections = [f"{self.strand}{grade} - {number}" for number in ("1", "2", "3")]
        self.section_box.blockSignals(True)
        self.section_box.clear()
        self.section_box.addItems(sections)
        if current in sections:
            self.section_box.setCurrentText(current)
        self.section_box.blockSignals(False)
        self.apply_section_teachers()

    def refresh_subjects(self):
        for combo in self._teacher_combos.values():
            self.subject_layout.removeRow(combo)
        self._teacher_combos.clear()

        current_grade = self.grade_box.currentText()
        subjects = subjects_for(self.strand, current_grade)

        for subj in subjects:
            cb = QComboBox()
            cb.addItems(self.teacher_list)
            cb.setEnabled(False)
            cb.setToolTip("Teacher is auto-selected from the selected section.")
            self._teacher_combos[subj] = cb
            self.subject_layout.addRow(f"{subj}:", cb)

        self.apply_section_teachers()

    def apply_section_teachers(self):
        option_index = _teacher_option_index_for_section(self.section_box.currentText())
        if option_index <= 0:
            return

        for cb in self._teacher_combos.values():
            if cb.count() > option_index:
                cb.setCurrentIndex(option_index)

    def validate_and_accept(self):
        self.apply_section_teachers()
        for subj, cb in self._teacher_combos.items():
            if not _clean_teacher_name(cb.currentText()):
                QMessageBox.warning(self, "Selection Required", f"No teacher is available for: {subj}")
                return
        self.accept()

    def get_result(self) -> Tuple[str, str, Dict[str, str]]:
        return (
            self.grade_box.currentText(),
            self.section_box.currentText(),
            {subj: _clean_teacher_name(cb.currentText()) for subj, cb in self._teacher_combos.items()}
        )


class StudentDetailsDialog(QDialog):
    """Main student editor with PDF receipt, removal feature, and integrated curriculum setup."""

    def __init__(self, parent, student_id: str):
        super().__init__(parent)
        self.setWindowTitle("Student Details (Edit)")
        self.setMinimumWidth(820)
        self.student_id = student_id
        self._loading = True

        layout = QVBoxLayout(self)
        self.title = QLabel(f"<b>{student_id}</b>")
        layout.addWidget(self.title)

        form = QFormLayout()
        layout.addLayout(form)

        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.email = QLineEdit()
        self.contact = QLineEdit()

        self.grade = QLineEdit();
        self.grade.setReadOnly(True)
        self.strand = QComboBox()
        self.strand.addItems(["STEM", "ABM", "HUMSS", "GAS", "TVL"])

        self.section = QLineEdit();
        self.section.setReadOnly(True)

        # --- SCHEDULE DROPDOWN UPDATED TO INCLUDE EVENING ---
        self.schedule = QComboBox()
        self.schedule.addItems(["", "MORNING", "AFTERNOON", "EVENING"])

        self.doc137 = QComboBox();
        self.doc137.addItems(["Passed", "To-Follow"])
        self.doc138 = QComboBox();
        self.doc138.addItems(["Passed", "To-Follow"])
        self.birth = QComboBox();
        self.birth.addItems(["Passed", "To-Follow"])
        self.status = QComboBox();
        self.status.addItems(["Enrolled", "Pending", "Dropped", "Inactive"])

        form.addRow("First Name:", self.first_name)
        form.addRow("Last Name:", self.last_name)
        form.addRow("Email:", self.email)
        form.addRow("Contact Number:", self.contact)
        form.addRow("Grade Level:", self.grade)
        form.addRow("Strand:", self.strand)
        form.addRow("Section:", self.section)
        form.addRow("Schedule:", self.schedule)
        form.addRow("Form 137:", self.doc137)
        form.addRow("Form 138:", self.doc138)
        form.addRow("Birth Certificate:", self.birth)
        form.addRow("Status:", self.status)

        layout.addWidget(QLabel("<b>Subjects / Teachers</b>"))
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Subject", "Teacher"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()

        self.btn_remove = QPushButton("Remove Student")
        self.btn_remove.setStyleSheet(
            "background-color: #dc3545; color: white; font-weight: bold; padding: 5px 10px; border-radius: 4px;")
        btn_row.addWidget(self.btn_remove)

        btn_row.addStretch(1)

        self.btn_print = QPushButton("Print Receipt (PDF)")
        btn_row.addWidget(self.btn_print)
        layout.addLayout(btn_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept);
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.btn_print.clicked.connect(self.print_receipt)
        self.btn_remove.clicked.connect(self.remove_student)
        self.strand.currentTextChanged.connect(self.prompt_curriculum_change)

        row = fetch_student_full(student_id)
        self.first_name.setText(row.get("first_name", ""))
        self.last_name.setText(row.get("last_name", ""))
        self.email.setText(row.get("email", ""))
        self.contact.setText(row.get("contact_number", ""))
        self.section.setText(row.get("section", ""))
        self.schedule.setCurrentText(row.get("schedule", ""))
        self.grade.setText(str(row.get("grade_level", "11")))

        self.strand.setCurrentText(row.get("strand", "ABM"))
        self._set_combo_value(self.doc137, normalize_doc(row.get("form_137")))
        self._set_combo_value(self.doc138, normalize_doc(row.get("form_138")))
        self._set_combo_value(self.birth, normalize_doc(row.get("birth_certificate")))
        self._set_combo_value(self.status, (row.get("status") or "Enrolled"))

        self.set_assignments(safe_load_assignments(row.get("assignments")))
        self._loading = False

    def remove_student(self):
        reply = QMessageBox.question(
            self, 'Confirm Remove',
            f"Are you sure you want to permanently remove {self.student_id} from the system?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_student(self.student_id)
                self.done(2)
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to remove student:\n{e}")

    def prompt_curriculum_change(self):
        if self._loading: return

        reply = QMessageBox.question(
            self, 'Confirm Change',
            "Changing the Strand requires a new curriculum setup. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            pending = {
                "strand": self.strand.currentText(),
                "grade_level": self.grade.text()
            }

            picker = GenericAssignmentDialog(self, pending)
            if picker.exec() == QDialog.DialogCode.Accepted:
                new_grade, section, assignments = picker.get_result()
                self.grade.setText(new_grade)
                self.section.setText(section)
                self.schedule.setCurrentText(schedule_from_section(section))
                self.set_assignments(assignments)

    @staticmethod
    def _set_combo_value(combo, value):
        idx = combo.findText(value or "")
        if idx >= 0:
            combo.setCurrentIndex(idx)
        else:
            combo.addItem(value);
            combo.setCurrentIndex(combo.count() - 1)

    def set_assignments(self, assignments):
        self.table.setRowCount(0)
        for s, t in assignments.items():
            r = self.table.rowCount()
            self.table.insertRow(r)
            subj_item = QTableWidgetItem(s);
            subj_item.setFlags(subj_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(r, 0, subj_item)
            self.table.setItem(r, 1, QTableWidgetItem(t))

    def print_receipt(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"Receipt_{self.student_id}.pdf", "PDF Files (*.pdf)")
        if not path: return
        try:
            student = {
                "student_id": self.student_id,
                "name": f"{self.first_name.text()} {self.last_name.text()}",
                "strand": self.strand.currentText(),
                "grade": self.grade.text(),
                "section": self.section.text(),
                "schedule": self.schedule.currentText(),
            }
            assignments = {
                self.table.item(r, 0).text(): (self.table.item(r, 1).text() if self.table.item(r, 1) else "")
                for r in range(self.table.rowCount())
            }
            export_student_receipt_pdf(path, student, assignments)
            QMessageBox.information(self, "Success", "PDF Saved.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def get_data(self):
        data = {
            "first_name": self.first_name.text(),
            "last_name": self.last_name.text(),
            "email": self.email.text(),
            "contact_number": self.contact.text(),
            "grade_level": self.grade.text(),
            "strand": self.strand.currentText(),
            "section": self.section.text(),
            "schedule": self.schedule.currentText(),
            "form_137": self.doc137.currentText(),
            "form_138": self.doc138.currentText(),
            "birth_certificate": self.birth.currentText(),
            "status": self.status.currentText()
        }
        assign = {
            self.table.item(r, 0).text(): (self.table.item(r, 1).text() if self.table.item(r, 1) else "")
            for r in range(self.table.rowCount())
        }
        return data, assign
