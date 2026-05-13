# model/enrollment_queue.py

import json
from typing import Dict
from .db import db_connect
from .constants import PAYMENT_TABLE, PENDING_TABLE, STUDENT_TABLE
from .helpers import table_exists
from .schema import ensure_payment_queue_table, ensure_pending_enrollments_table_and_columns


def upsert_pending_enrollment(student: dict, section: str, assignments: Dict[str, str], payment_status: str = "Unpaid"):
    ensure_pending_enrollments_table_and_columns()
    sid = student.get("student_id", "")
    if not sid:
        return

    teacher_assignments = json.dumps(assignments, ensure_ascii=False)

    try:
        conn = db_connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(f"SELECT id FROM {PENDING_TABLE} WHERE student_id=%s LIMIT 1", (sid,))
        row = cur.fetchone()

        if row:
            cur2 = conn.cursor()
            cur2.execute(
                f"""
                UPDATE {PENDING_TABLE}
                SET first_name=%s,last_name=%s,email=%s,contact_number=%s,
                    grade_level=%s,strand=%s,form_137=%s,form_138=%s,birth_certificate=%s,
                    section=%s,teacher_assignments=%s,payment_status=%s
                WHERE student_id=%s
                """,
                (
                    student.get("first_name", ""),
                    student.get("last_name", ""),
                    student.get("email", ""),
                    student.get("contact_number", ""),
                    str(student.get("grade_level", "")),
                    student.get("strand", ""),
                    student.get("form_137", "To-Follow"),
                    student.get("form_138", "To-Follow"),
                    student.get("birth_certificate", "To-Follow"),
                    section,
                    teacher_assignments,
                    payment_status,
                    sid,
                ),
            )
            conn.commit()
            cur2.close()
        else:
            cur2 = conn.cursor()
            cur2.execute(
                f"""
                INSERT INTO {PENDING_TABLE}
                    (student_id, first_name, last_name, email, contact_number,
                     grade_level, strand, form_137, form_138, birth_certificate,
                     section, teacher_assignments, payment_status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    sid,
                    student.get("first_name", ""),
                    student.get("last_name", ""),
                    student.get("email", ""),
                    student.get("contact_number", ""),
                    str(student.get("grade_level", "")),
                    student.get("strand", ""),
                    student.get("form_137", "To-Follow"),
                    student.get("form_138", "To-Follow"),
                    student.get("birth_certificate", "To-Follow"),
                    section,
                    teacher_assignments,
                    payment_status,
                ),
            )
            conn.commit()
            cur2.close()

        cur.close()
        conn.close()
    except Exception:
        pass


def update_pending_payment_status(student_id: str, status: str):
    ensure_pending_enrollments_table_and_columns()
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(f"UPDATE {PENDING_TABLE} SET payment_status=%s WHERE student_id=%s", (status, student_id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass


def delete_pending_enrollment(student_id: str):
    ensure_pending_enrollments_table_and_columns()
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {PENDING_TABLE} WHERE student_id=%s", (student_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass


def _extract_student_num(student_id: str) -> int:
    try:
        digits = "".join(ch for ch in str(student_id) if ch.isdigit())
        return int(digits) if digits else 0
    except Exception:
        return 0


def get_next_student_id() -> str:
    ensure_payment_queue_table()
    ensure_pending_enrollments_table_and_columns()

    max_num = 0
    conn = db_connect()
    cur = conn.cursor(dictionary=True)

    try:
        if table_exists(STUDENT_TABLE):
            cur.execute(f"SELECT student_id FROM {STUDENT_TABLE} WHERE student_id IS NOT NULL")
            for r in cur.fetchall() or []:
                max_num = max(max_num, _extract_student_num(r.get("student_id", "")))
    except Exception:
        pass

    try:
        cur.execute(f"SELECT student_id FROM {PAYMENT_TABLE} WHERE student_id IS NOT NULL")
        for r in cur.fetchall() or []:
            max_num = max(max_num, _extract_student_num(r.get("student_id", "")))
    except Exception:
        pass

    try:
        cur.execute(f"SELECT student_id FROM {PENDING_TABLE} WHERE student_id IS NOT NULL")
        for r in cur.fetchall() or []:
            max_num = max(max_num, _extract_student_num(r.get("student_id", "")))
    except Exception:
        pass

    cur.close()
    conn.close()
    return f"ST-{(max_num + 1):04d}"
