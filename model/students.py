# model/students.py

import json
from typing import Dict, Optional
from .db import db_connect
from .constants import STUDENT_TABLE
from .schema import ensure_student_optional_columns
from .helpers import column_exists


def fetch_student_full(student_id: str) -> Dict[str, str]:
    """Fetches all student data including the schedule."""
    ensure_student_optional_columns()
    conn = db_connect()
    cur = conn.cursor(dictionary=True)

    schedule_col = ", schedule" if column_exists(STUDENT_TABLE, "schedule") else ""

    cur.execute(
        f"""
        SELECT student_id, first_name, last_name, email, contact_number,
               grade_level, strand, form_137, form_138, birth_certificate,
               status, section, assignments {schedule_col}
        FROM {STUDENT_TABLE}
        WHERE student_id=%s
        LIMIT 1
        """,
        (student_id,),
    )
    row = cur.fetchone() or {}
    cur.close()
    conn.close()
    return {k: ("" if row.get(k) is None else str(row.get(k))) for k in row.keys()}


def update_student_full(student_id: str, data: Dict[str, str], assignments: Dict[str, str]):
    """Updates student info and the schedule."""
    ensure_student_optional_columns()
    conn = db_connect()
    cur = conn.cursor()

    has_sched = column_exists(STUDENT_TABLE, "schedule")
    sched_update = ", schedule=%s" if has_sched else ""

    query = f"""
        UPDATE {STUDENT_TABLE}
        SET first_name=%s,
            last_name=%s,
            email=%s,
            contact_number=%s,
            grade_level=%s,
            strand=%s,
            form_137=%s,
            form_138=%s,
            birth_certificate=%s,
            status=%s,
            section=%s,
            assignments=%s
            {sched_update}
        WHERE student_id=%s
    """

    params = [
        data.get("first_name", ""),
        data.get("last_name", ""),
        data.get("email", ""),
        data.get("contact_number", ""),
        data.get("grade_level", ""),
        data.get("strand", ""),
        data.get("form_137", "To-Follow"),
        data.get("form_138", "To-Follow"),
        data.get("birth_certificate", "To-Follow"),
        data.get("status", "Enrolled"),
        data.get("section", ""),
        json.dumps(assignments, ensure_ascii=False)
    ]

    if has_sched:
        params.append(data.get("schedule", ""))

    params.append(student_id)

    cur.execute(query, tuple(params))
    conn.commit()
    cur.close()
    conn.close()


def delete_student(student_id: str):
    ensure_student_optional_columns()
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {STUDENT_TABLE} WHERE student_id=%s", (student_id,))
    conn.commit()
    cur.close()
    conn.close()


def get_section_count(strand: str, grade_level: str, section: str) -> int:
    """Counts the number of enrolled AND pending students in a specific section."""
    ensure_student_optional_columns()
    conn = db_connect()
    cur = conn.cursor(dictionary=True)
    count = 0
    from model.constants import PAYMENT_TABLE
    try:
        cur.execute(
            f"SELECT COUNT(*) as c FROM {STUDENT_TABLE} WHERE strand=%s AND grade_level=%s AND section=%s AND status='Enrolled'",
            (strand, grade_level, section)
        )
        res = cur.fetchone()
        if res: count += res['c']
    except:
        pass

    try:
        cur.execute(
            f"SELECT COUNT(*) as c FROM {PAYMENT_TABLE} WHERE strand=%s AND grade_level=%s AND section=%s",
            (strand, grade_level, section)
        )
        res = cur.fetchone()
        if res: count += res['c']
    except:
        pass

    cur.close()
    conn.close()
    return count
