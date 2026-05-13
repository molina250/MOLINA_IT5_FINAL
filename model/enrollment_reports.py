# model/enrollment_reports.py

from .constants import ENROLLMENT_REPORTS_TABLE, REGISTRAR_TABLE, STUDENT_TABLE
from .db import db_connect
from .helpers import table_exists, column_exists
from .schema import ensure_enrollment_reports_table


def _student_col(name: str, fallback: str = "''") -> str:
    return f"s.{name}" if column_exists(STUDENT_TABLE, name) else fallback


def sync_enrollment_reports():
    """Keeps the phpMyAdmin enrollment_reports table aligned with enrolled students."""
    ensure_enrollment_reports_table()
    if not table_exists(STUDENT_TABLE):
        return

    has_registrar = column_exists(STUDENT_TABLE, "registrar_id") and table_exists(REGISTRAR_TABLE)
    registrar_join = f"LEFT JOIN {REGISTRAR_TABLE} r ON s.registrar_id = r.id" if has_registrar else ""
    registrar_db_id = "s.registrar_id" if has_registrar else "NULL"
    registrar_account = "r.registrar_id" if has_registrar else "NULL"
    registrar_name = "r.full_name" if has_registrar else "NULL"

    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO {ENROLLMENT_REPORTS_TABLE} (
                student_id, first_name, last_name, full_name, email, contact_number,
                grade_level, strand, section, schedule, form_137, form_138,
                birth_certificate, status, payment_status, registrar_db_id,
                registrar_account, registrar_name, enrolled_at, updated_at
            )
            SELECT
                s.student_id,
                s.first_name,
                s.last_name,
                CONCAT_WS(' ', s.first_name, s.last_name) AS full_name,
                {_student_col('email')},
                {_student_col('contact_number')},
                s.grade_level,
                s.strand,
                {_student_col('section')},
                {_student_col('schedule')},
                {_student_col('form_137')},
                {_student_col('form_138')},
                {_student_col('birth_certificate')},
                {_student_col('status')},
                {_student_col('payment_status')},
                {registrar_db_id},
                {registrar_account},
                {registrar_name},
                {_student_col('enrolled_at', 's.created_at')},
                NOW()
            FROM {STUDENT_TABLE} s
            {registrar_join}
            WHERE s.status = 'Enrolled'
            ON DUPLICATE KEY UPDATE
                first_name=VALUES(first_name),
                last_name=VALUES(last_name),
                full_name=VALUES(full_name),
                email=VALUES(email),
                contact_number=VALUES(contact_number),
                grade_level=VALUES(grade_level),
                strand=VALUES(strand),
                section=VALUES(section),
                schedule=VALUES(schedule),
                form_137=VALUES(form_137),
                form_138=VALUES(form_138),
                birth_certificate=VALUES(birth_certificate),
                status=VALUES(status),
                payment_status=VALUES(payment_status),
                registrar_db_id=VALUES(registrar_db_id),
                registrar_account=VALUES(registrar_account),
                registrar_name=VALUES(registrar_name),
                enrolled_at=VALUES(enrolled_at),
                updated_at=NOW()
            """
        )
        cur.execute(
            f"""
            DELETE er
            FROM {ENROLLMENT_REPORTS_TABLE} er
            LEFT JOIN {STUDENT_TABLE} s ON er.student_id = s.student_id AND s.status = 'Enrolled'
            WHERE s.student_id IS NULL
            """
        )
        conn.commit()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_enrollment_report_rows() -> list:
    sync_enrollment_reports()
    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            f"""
            SELECT
                student_id, first_name, last_name, full_name, email, contact_number,
                grade_level, strand, section, schedule, form_137, form_138,
                birth_certificate, status, payment_status, registrar_db_id,
                registrar_account AS reg_account,
                registrar_name,
                enrolled_at,
                updated_at
            FROM {ENROLLMENT_REPORTS_TABLE}
            ORDER BY enrolled_at DESC, id DESC
            """
        )
        return cur.fetchall() or []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
