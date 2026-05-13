# model/strands.py

from typing import Optional
from .db import db_connect
from .constants import STRANDS_TABLE
from .schema import ensure_strands_table_and_seed


def get_or_create_strand_id(strand_name: str) -> Optional[int]:
    if not strand_name:
        return None
    name = strand_name.strip().upper()
    try:
        ensure_strands_table_and_seed()
        conn = db_connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(f"SELECT id FROM {STRANDS_TABLE} WHERE UPPER(name)=UPPER(%s) LIMIT 1", (name,))
        row = cur.fetchone()
        if row and row.get("id") is not None:
            sid = int(row["id"])
            cur.close()
            conn.close()
            return sid

        cur.execute(f"INSERT INTO {STRANDS_TABLE}(name) VALUES(%s)", (name,))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return int(new_id) if new_id else None
    except Exception:
        return None
