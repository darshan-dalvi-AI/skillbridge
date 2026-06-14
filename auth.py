"""
auth.py — Lightweight Local Login + Progress Saving
===================================================
A simple, dependency-free account system so students can save their progress
over time. Passwords are hashed with PBKDF2-HMAC-SHA256 and a per-user salt
(never stored in plain text) using only Python's standard library.

Honest scope: this is DEMO-GRADE auth meant for a local college project. Data
lives in a local JSON file (user_data.json, gitignored). It is not meant to be
production security, and on an ephemeral host (e.g. Streamlit Cloud) the file
can reset on restart — the app states this in the UI.
"""

import os
import json
import hashlib
import secrets

_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_data.json")
_ITERATIONS = 200_000
_EMPTY_PROGRESS = {"learned": [], "role": "", "history": []}


def _load() -> dict:
    if os.path.exists(_DATA_FILE):
        try:
            with open(_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"users": {}}
    return {"users": {}}


def _save(data: dict) -> None:
    tmp = _DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, _DATA_FILE)


def _hash(password: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), _ITERATIONS
    ).hex()


def _norm(username: str) -> str:
    return (username or "").strip().lower()


def register(username: str, password: str):
    """Create a new account. Returns (ok, message)."""
    username = _norm(username)
    if not username or not password:
        return False, "Enter both a username and a password."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    data = _load()
    if username in data.get("users", {}):
        return False, "That username already exists — try logging in instead."
    salt = secrets.token_hex(16)
    data.setdefault("users", {})[username] = {
        "salt": salt,
        "hash": _hash(password, salt),
        "progress": dict(_EMPTY_PROGRESS),
    }
    _save(data)
    return True, "Account created — you're logged in!"


def authenticate(username: str, password: str):
    """Verify credentials. Returns (ok, message)."""
    username = _norm(username)
    user = _load().get("users", {}).get(username)
    if not user:
        return False, "No account with that username — register first."
    if _hash(password, user["salt"]) == user["hash"]:
        return True, "Logged in."
    return False, "Incorrect password."


def get_progress(username: str) -> dict:
    """Return the saved progress dict for a user (or an empty template)."""
    user = _load().get("users", {}).get(_norm(username))
    if not user:
        return dict(_EMPTY_PROGRESS)
    prog = user.get("progress") or {}
    # ensure all keys exist
    merged = dict(_EMPTY_PROGRESS)
    merged.update(prog)
    return merged


def save_progress(username: str, progress: dict) -> bool:
    """Persist a user's progress dict. Returns True on success."""
    username = _norm(username)
    data = _load()
    if username in data.get("users", {}):
        data["users"][username]["progress"] = progress
        _save(data)
        return True
    return False
