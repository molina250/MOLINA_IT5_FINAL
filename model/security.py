# model/security.py

import base64

_SECRET_KEY = b"EDUGATE_SECRET_KEY_2025"


def encrypt_password(plain: str) -> str:
    if plain is None:
        plain = ""
    data = plain.encode("utf-8")
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ _SECRET_KEY[i % len(_SECRET_KEY)])
    token = base64.urlsafe_b64encode(bytes(out)).decode("utf-8")
    return f"ENC:{token}"


def decrypt_password(stored: str) -> str:
    if stored is None:
        return ""
    s = str(stored)
    if not s.startswith("ENC:"):
        return s
    token = s[4:]
    raw = base64.urlsafe_b64decode(token.encode("utf-8"))
    out = bytearray()
    for i, b in enumerate(raw):
        out.append(b ^ _SECRET_KEY[i % len(_SECRET_KEY)])
    return out.decode("utf-8", errors="replace")
