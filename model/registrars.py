# model/registrars.py

from .constants import REGISTRAR_TABLE
from .db import db_connect
from .schema import ensure_registrars_table
from .security import encrypt_password, decrypt_password


def authenticate_registrar(registrar_id: str, password: str):
    ensure_registrars_table()
    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            f"SELECT id, password FROM {REGISTRAR_TABLE} WHERE registrar_id=%s",
            (registrar_id,),
        )
        user = cur.fetchone()
        if user and decrypt_password(user["password"]) == password:
            return user["id"]
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return None


def create_registrar_account(full_name: str, contact_number: str, email: str, registrar_id: str, password: str):
    ensure_registrars_table()
    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor()
        username = f"reg_{registrar_id}"
        cur.execute(
            f"""
            INSERT INTO {REGISTRAR_TABLE}
                (full_name, email, contact_number, registrar_id, username, password)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (full_name, email, contact_number, registrar_id, username, encrypt_password(password)),
        )
        conn.commit()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def list_registrars() -> list:
    ensure_registrars_table()
    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            f"""
            SELECT id, registrar_id, full_name, email, contact_number, username
            FROM {REGISTRAR_TABLE}
            ORDER BY id DESC
            """
        )
        return cur.fetchall() or []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def update_registrar_account(registrar_id: str, data: dict):
    ensure_registrars_table()
    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(
            f"""
            UPDATE {REGISTRAR_TABLE}
            SET full_name=%s, email=%s, contact_number=%s, username=%s
            WHERE registrar_id=%s
            """,
            (
                data["full_name"],
                data["email"],
                data["contact_number"],
                data["username"],
                registrar_id,
            ),
        )
        conn.commit()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def delete_registrar_account(registrar_id: str):
    ensure_registrars_table()
    conn = None
    cur = None
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {REGISTRAR_TABLE} WHERE registrar_id=%s", (registrar_id,))
        conn.commit()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
