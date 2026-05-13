# model/admin_records.py

from .constants import REPORTS_TABLE
from .db import db_connect
from .reports import recalc_and_store_reports
from .enrollment_reports import get_enrollment_report_rows as get_synced_enrollment_report_rows


def get_report_rows() -> list:
    recalc_and_store_reports()
    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            f"""
            SELECT strand, daily, weekly, monthly, yearly, total
            FROM {REPORTS_TABLE}
            ORDER BY strand ASC
            """
        )
        return cur.fetchall() or []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_enrollment_report_rows() -> tuple:
    return get_synced_enrollment_report_rows(), True, True
