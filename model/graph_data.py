# model/graph_data.py

from .constants import STUDENT_TABLE, REGISTRAR_TABLE, PAYMENT_TABLE, SLOTS_TABLE
from .db import db_connect
from .helpers import table_exists, column_exists
from .schedule import schedule_label_for_section
from .schema import sync_all_slots


DEFAULT_STRANDS = ["STEM", "ABM", "HUMSS", "GAS", "TVL"]
DEFAULT_GRADES = ["11", "12"]
DEFAULT_SECTIONS = ["1", "2", "3"]
SECTION_CAPACITY = 50


def get_strand_enrollment_counts() -> dict:
    counts = {strand: 0 for strand in DEFAULT_STRANDS}
    if not table_exists(STUDENT_TABLE):
        return counts

    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            f"""
            SELECT strand, COUNT(*) AS total
            FROM {STUDENT_TABLE}
            WHERE status='Enrolled'
            GROUP BY strand
            """
        )
        for row in cur.fetchall() or []:
            strand = str(row.get("strand", "")).strip().upper()
            if strand in counts:
                counts[strand] = int(row.get("total") or 0)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return counts


def get_registrar_performance_counts() -> dict:
    if not table_exists(REGISTRAR_TABLE) or not table_exists(STUDENT_TABLE):
        return {"No Data": 0}

    if not column_exists(STUDENT_TABLE, "registrar_id"):
        return {"No Data": 0}

    counts = {}
    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            f"""
            SELECT r.username, COUNT(s.id) AS total
            FROM {REGISTRAR_TABLE} r
            LEFT JOIN {STUDENT_TABLE} s ON r.id = s.registrar_id AND s.status = 'Enrolled'
            GROUP BY r.id, r.username
            """
        )
        for row in cur.fetchall() or []:
            name = row.get("username") or "Unknown"
            counts[name] = int(row.get("total") or 0)
    except Exception:
        return {"Error": 0}
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return counts or {"No Data": 0}


def get_available_slots_by_strand(strand: str) -> list:
    normalized_strand = str(strand or "").strip().upper()
    conn = None
    cur = None
    try:
        sync_all_slots()
        conn = db_connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            f"""
            SELECT grade_level, section, schedule, available_slots
            FROM {SLOTS_TABLE}
            WHERE strand=%s
            ORDER BY grade_level ASC, section ASC
            """,
            (normalized_strand,),
        )
        rows = cur.fetchall() or []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    slots = []
    for row in rows:
        section = row.get("section", "")
        slots.append({
            "grade": str(row.get("grade_level", "")),
            "section": section,
            "schedule_label": row.get("schedule") or schedule_label_for_section(section),
            "available": int(row.get("available_slots") or 0),
        })
    return slots
