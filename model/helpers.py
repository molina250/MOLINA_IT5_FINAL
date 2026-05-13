# model/helpers.py

import json
from typing import Optional, Dict
from .db import db_connect


def normalize_doc(value: Optional[str]) -> str:
    if value is None:
        return "To-Follow"
    v = str(value).strip().lower()
    if v in ("", "to-follow", "to follow", "tofollow", "pending", "missing", "no", "not submitted"):
        return "To-Follow"
    if v in ("passed", "pass", "submitted", "complete", "completed", "ok", "yes", "available"):
        return "Passed"
    return "To-Follow"


def table_exists(table_name: str) -> bool:
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("SHOW TABLES LIKE %s", (table_name,))
        ok = cur.fetchone() is not None
        cur.close()
        conn.close()
        return ok
    except Exception:
        return False


def column_exists(table_name: str, col: str) -> bool:
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(f"SHOW COLUMNS FROM {table_name} LIKE %s", (col,))
        ok = cur.fetchone() is not None
        cur.close()
        conn.close()
        return ok
    except Exception:
        return False


def safe_load_assignments(text: Optional[str]) -> Dict[str, str]:
    if not text:
        return {}
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            out = {}
            for k, v in data.items():
                out[str(k)] = "" if v is None else str(v)
            return out
    except Exception:
        pass
    return {}
