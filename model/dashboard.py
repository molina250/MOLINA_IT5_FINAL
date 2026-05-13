# model/dashboard.py

from .constants import REGISTRAR_TABLE, STUDENT_TABLE, PAYMENT_TABLE
from .db import db_connect
from .helpers import table_exists, column_exists


def _fetch_count(cur, query: str, params=()) -> int:
    cur.execute(query, params)
    row = cur.fetchone() or {}
    return int(row.get("total") or 0)


def get_admin_dashboard_counts() -> dict:
    counts = {
        "registrars": 0,
        "enrolled_students": 0,
    }

    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor(dictionary=True)

        if table_exists(REGISTRAR_TABLE):
            counts["registrars"] = _fetch_count(cur, f"SELECT COUNT(*) AS total FROM {REGISTRAR_TABLE}")

        if table_exists(STUDENT_TABLE):
            counts["enrolled_students"] = _fetch_count(
                cur,
                f"SELECT COUNT(*) AS total FROM {STUDENT_TABLE} WHERE status='Enrolled'",
            )
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return counts


def get_registrar_dashboard_counts() -> dict:
    counts = {
        "verified": 0,
        "to_follow": 0,
        "enrolled": 0,
    }

    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor(dictionary=True)

        if table_exists(STUDENT_TABLE):
            counts["enrolled"] = _fetch_count(
                cur,
                f"SELECT COUNT(*) AS total FROM {STUDENT_TABLE} WHERE status='Enrolled'",
            )

            has_student_docs = all(
                column_exists(STUDENT_TABLE, col)
                for col in ("form_137", "form_138", "birth_certificate")
            )
            if has_student_docs:
                counts["verified"] += _fetch_count(
                    cur,
                    f"""
                    SELECT COUNT(*) AS total
                    FROM {STUDENT_TABLE}
                    WHERE status='Enrolled'
                      AND COALESCE(form_137, '') = 'Passed'
                      AND COALESCE(form_138, '') = 'Passed'
                      AND COALESCE(birth_certificate, '') = 'Passed'
                    """,
                )
                counts["to_follow"] += _fetch_count(
                    cur,
                    f"""
                    SELECT COUNT(*) AS total
                    FROM {STUDENT_TABLE}
                    WHERE status='Enrolled'
                      AND (
                        COALESCE(form_137, '') <> 'Passed'
                        OR COALESCE(form_138, '') <> 'Passed'
                        OR COALESCE(birth_certificate, '') <> 'Passed'
                      )
                    """,
                )

        if table_exists(PAYMENT_TABLE):
            has_payment_docs = all(
                column_exists(PAYMENT_TABLE, col)
                for col in ("form_137", "form_138", "birth_certificate")
            )
            if has_payment_docs:
                counts["verified"] += _fetch_count(
                    cur,
                    f"""
                    SELECT COUNT(*) AS total
                    FROM {PAYMENT_TABLE}
                    WHERE COALESCE(form_137, '') = 'Passed'
                      AND COALESCE(form_138, '') = 'Passed'
                      AND COALESCE(birth_certificate, '') = 'Passed'
                    """,
                )
                counts["to_follow"] += _fetch_count(
                    cur,
                    f"""
                    SELECT COUNT(*) AS total
                    FROM {PAYMENT_TABLE}
                    WHERE COALESCE(form_137, '') <> 'Passed'
                       OR COALESCE(form_138, '') <> 'Passed'
                       OR COALESCE(birth_certificate, '') <> 'Passed'
                    """,
                )
            else:
                counts["to_follow"] += _fetch_count(cur, f"SELECT COUNT(*) AS total FROM {PAYMENT_TABLE}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return counts
