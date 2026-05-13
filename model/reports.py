# model/reports.py

from datetime import datetime
from .db import db_connect
from .constants import STUDENT_TABLE, REPORTS_TABLE, STRANDS_TABLE
from .helpers import table_exists
from .schema import ensure_reports_table_and_seed


def recalc_and_store_reports():
    if not table_exists(STUDENT_TABLE):
        return
    ensure_reports_table_and_seed()

    conn = db_connect()
    cur = conn.cursor(dictionary=True)

    # ensure strand_id is filled
    try:
        cur.execute(
            f"""
            UPDATE {REPORTS_TABLE} r
            JOIN {STRANDS_TABLE} s ON r.strand = s.name
            SET r.strand_id = s.id
            WHERE r.strand_id IS NULL
            """
        )
        conn.commit()
    except Exception:
        pass

    today = datetime.now().date()
    year = today.year
    month = today.month

    def _count(query, params=()):
        cur.execute(query, params)
        return {r["strand"]: int(r["total"]) for r in (cur.fetchall() or []) if r.get("strand")}

    totals = _count(
        f"""
        SELECT strand, COUNT(*) AS total
        FROM {STUDENT_TABLE}
        WHERE status='Enrolled'
        GROUP BY strand
        """
    )
    daily = _count(
        f"""
        SELECT strand, COUNT(*) AS total
        FROM {STUDENT_TABLE}
        WHERE status='Enrolled' AND DATE(created_at)=CURDATE()
        GROUP BY strand
        """
    )
    weekly = _count(
        f"""
        SELECT strand, COUNT(*) AS total
        FROM {STUDENT_TABLE}
        WHERE status='Enrolled' AND YEARWEEK(created_at, 1)=YEARWEEK(CURDATE(), 1)
        GROUP BY strand
        """
    )
    monthly = _count(
        f"""
        SELECT strand, COUNT(*) AS total
        FROM {STUDENT_TABLE}
        WHERE status='Enrolled' AND YEAR(created_at)=%s AND MONTH(created_at)=%s
        GROUP BY strand
        """,
        (year, month),
    )
    yearly = _count(
        f"""
        SELECT strand, COUNT(*) AS total
        FROM {STUDENT_TABLE}
        WHERE status='Enrolled' AND YEAR(created_at)=%s
        GROUP BY strand
        """,
        (year,),
    )

    cur.execute(f"SELECT id, strand FROM {REPORTS_TABLE}")
    existing = cur.fetchall() or []

    for row in existing:
        s = row.get("strand")
        if not s:
            continue
        cur.execute(
            f"""
            UPDATE {REPORTS_TABLE}
            SET daily=%s, weekly=%s, monthly=%s, yearly=%s, total=%s, updated_at=NOW()
            WHERE id=%s
            """,
            (
                daily.get(s, 0),
                weekly.get(s, 0),
                monthly.get(s, 0),
                yearly.get(s, 0),
                totals.get(s, 0),
                row["id"],
            ),
        )

    conn.commit()
    cur.close()
    conn.close()
