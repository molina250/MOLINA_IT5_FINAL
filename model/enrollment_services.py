# model/enrollment_services.py

import json
from datetime import datetime

from .constants import STUDENT_TABLE, PAYMENT_TABLE, PENDING_TABLE
from .db import db_connect
from .helpers import table_exists, column_exists
from .schema import (
    ensure_payment_queue_table,
    ensure_pending_enrollments_table_and_columns,
    ensure_student_optional_columns,
    sync_all_slots,
)
from .enrollment_queue import (
    upsert_pending_enrollment,
    update_pending_payment_status,
    delete_pending_enrollment,
    get_next_student_id,
)
from .strands import get_or_create_strand_id
from .reports import recalc_and_store_reports
from .schedule import schedule_from_section


def ensure_schedule_columns():
    for table in [STUDENT_TABLE, PAYMENT_TABLE, PENDING_TABLE]:
        if table_exists(table) and not column_exists(table, "schedule"):
            conn = None
            cur = None
            try:
                conn = db_connect()
                cur = conn.cursor()
                cur.execute(f"ALTER TABLE {table} ADD COLUMN schedule VARCHAR(50) DEFAULT ''")
                conn.commit()
            finally:
                if cur:
                    cur.close()
                if conn:
                    conn.close()


def queue_student_for_payment(student: dict, section: str, assignments: dict):
    ensure_payment_queue_table()
    ensure_pending_enrollments_table_and_columns()
    ensure_schedule_columns()

    assignment_payload = student.get("assignments") or json.dumps(assignments, ensure_ascii=False)

    cols = [
        "student_id", "first_name", "last_name", "email", "contact_number",
        "grade_level", "strand", "form_137", "form_138", "birth_certificate",
        "section", "assignments", "payment_status"
    ]
    vals = [
        student["student_id"], student["first_name"], student["last_name"],
        student["email"], student["contact_number"], student["grade_level"],
        student["strand"], student["form_137"], student["form_138"],
        student["birth_certificate"], section, assignment_payload, "Unpaid"
    ]

    if column_exists(PAYMENT_TABLE, "schedule"):
        cols.append("schedule")
        vals.append(student.get("schedule") or schedule_from_section(section))

    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor()
        placeholders = ",".join(["%s"] * len(cols))
        cur.execute(f"INSERT INTO {PAYMENT_TABLE} ({','.join(cols)}) VALUES ({placeholders})", tuple(vals))
        conn.commit()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    upsert_pending_enrollment(student, section, assignments, "Unpaid")
    sync_all_slots()


def load_enrolled_students() -> list:
    ensure_schedule_columns()
    if not table_exists(STUDENT_TABLE):
        return []

    has_schedule = column_exists(STUDENT_TABLE, "schedule")
    schedule_col = ", schedule" if has_schedule else ""

    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            f"""
            SELECT student_id, first_name, last_name, strand, grade_level,
                   form_137, form_138, birth_certificate, status {schedule_col}
            FROM {STUDENT_TABLE}
            WHERE status='Enrolled'
            ORDER BY id DESC
            """
        )
        return cur.fetchall() or []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def load_payment_queue() -> list:
    ensure_payment_queue_table()
    ensure_pending_enrollments_table_and_columns()

    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            f"""
            SELECT student_id, first_name, last_name, strand, grade_level,
                   form_137, form_138, birth_certificate, payment_status
            FROM {PAYMENT_TABLE}
            ORDER BY created_at DESC
            """
        )
        return cur.fetchall() or []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def remove_payment_queue_student(student_id: str):
    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {PAYMENT_TABLE} WHERE student_id=%s", (student_id,))
        conn.commit()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    delete_pending_enrollment(student_id)
    sync_all_slots()


def mark_payment_unpaid(student_id: str):
    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(f"UPDATE {PAYMENT_TABLE} SET payment_status='Unpaid' WHERE student_id=%s", (student_id,))
        conn.commit()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    update_pending_payment_status(student_id, "Unpaid")
    sync_all_slots()


def approve_payment_queue_student(student_id: str, registrar_db_id):
    if not table_exists(STUDENT_TABLE):
        return False

    ensure_student_optional_columns()
    ensure_pending_enrollments_table_and_columns()
    ensure_schedule_columns()

    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor(dictionary=True)

        cur.execute(f"SELECT * FROM {PAYMENT_TABLE} WHERE student_id=%s LIMIT 1", (student_id,))
        row = cur.fetchone()
        if not row:
            return False

        approved_student_id = row.get("student_id")
        cur.execute(f"SELECT id FROM {STUDENT_TABLE} WHERE student_id=%s LIMIT 1", (approved_student_id,))
        if cur.fetchone():
            approved_student_id = get_next_student_id()
            cur.execute(
                f"UPDATE {PAYMENT_TABLE} SET student_id=%s WHERE student_id=%s",
                (approved_student_id, student_id),
            )
            cur.execute(
                f"UPDATE {PENDING_TABLE} SET student_id=%s WHERE student_id=%s",
                (approved_student_id, student_id),
            )

        cols = [
            "student_id", "first_name", "last_name", "email", "contact_number",
            "grade_level", "strand", "form_137", "form_138", "birth_certificate", "status"
        ]
        vals = [
            approved_student_id, row.get("first_name"), row.get("last_name"),
            row.get("email"), row.get("contact_number"), row.get("grade_level"),
            row.get("strand"), row.get("form_137"), row.get("form_138"),
            row.get("birth_certificate"), "Enrolled"
        ]

        if column_exists(STUDENT_TABLE, "section") and "section" in row:
            cols.append("section")
            vals.append(row.get("section"))

        if column_exists(STUDENT_TABLE, "schedule") and "schedule" in row:
            cols.append("schedule")
            vals.append(row.get("schedule"))

        if column_exists(STUDENT_TABLE, "assignments") and "assignments" in row:
            cols.append("assignments")
            vals.append(row.get("assignments"))

        if column_exists(STUDENT_TABLE, "registrar_id") and registrar_db_id is not None:
            cols.append("registrar_id")
            vals.append(int(registrar_db_id))

        if column_exists(STUDENT_TABLE, "strand_id"):
            cols.append("strand_id")
            vals.append(get_or_create_strand_id(str(row.get("strand") or "")))

        if column_exists(STUDENT_TABLE, "payment_status"):
            cols.append("payment_status")
            vals.append("Paid")
        if column_exists(STUDENT_TABLE, "payment_approved"):
            cols.append("payment_approved")
            vals.append(1)
        if column_exists(STUDENT_TABLE, "paid_at"):
            cols.append("paid_at")
            vals.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        if column_exists(STUDENT_TABLE, "enrolled_at"):
            cols.append("enrolled_at")
            vals.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if column_exists(STUDENT_TABLE, "teacher_assignments") and "assignments" in row:
            cols.append("teacher_assignments")
            vals.append(row.get("assignments"))

        placeholders = ",".join(["%s"] * len(cols))
        cur.execute(f"INSERT INTO {STUDENT_TABLE} ({','.join(cols)}) VALUES ({placeholders})", tuple(vals))
        cur.execute(f"DELETE FROM {PAYMENT_TABLE} WHERE student_id=%s", (approved_student_id,))
        conn.commit()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    delete_pending_enrollment(approved_student_id)
    recalc_and_store_reports()
    sync_all_slots()
    from .enrollment_reports import sync_enrollment_reports
    sync_enrollment_reports()
    return True
