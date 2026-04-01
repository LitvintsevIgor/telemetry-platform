"""In-memory Owen API bearer token, set on successful POST /login (MVP)."""

from __future__ import annotations

import threading

_lock = threading.Lock()
_token: str | None = None


def get() -> str | None:
    with _lock:
        return _token


def set_token(value: str | None) -> None:
    global _token
    with _lock:
        _token = value
