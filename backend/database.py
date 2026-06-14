"""
database.py — storage layer for the SkillBridge backend
=======================================================
Works with TWO engines behind one tiny interface:

  * SQLite  (default, local)  -> file `skillbridge.db`, zero setup.
  * Postgres (cloud)          -> used automatically when the env var
                                 DATABASE_URL is set (e.g. Neon / Supabase).

`get_conn()` returns a thin wrapper whose `.execute(sql, params)` accepts the
SAME `?`-style SQL for both engines (it rewrites `?` -> `%s` for Postgres) and
exposes `.insert(sql, params)` which returns the new row id on either engine.
So `main.py` is engine-agnostic.

Tables: users, profiles, analyses, progress_history, jd_matches, chats.
List/object columns are stored as JSON text (portable across both engines).
"""

import os
import json
from datetime import datetime, timezone

DATABASE_URL = (os.environ.get("DATABASE_URL", "") or "").strip()
IS_PG = DATABASE_URL.startswith(("postgres://", "postgresql://"))

if IS_PG:
    import psycopg
    from psycopg.rows import dict_row
    # psycopg3 accepts both schemes, but normalise for safety.
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]
else:
    import sqlite3
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skillbridge.db")


# ----------------------------------------------------------------- helpers
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def dumps(value) -> str:
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return "[]"


def loads(text, default=None):
    if not text:
        return default if default is not None else []
    try:
        return json.loads(text)
    except Exception:
        return default if default is not None else []


def _q(sql: str) -> str:
    """Translate ?-placeholders to %s for Postgres; leave SQLite untouched."""
    return sql.replace("?", "%s") if IS_PG else sql


# ----------------------------------------------------------------- connection wrapper
class _Cursor:
    def __init__(self, raw):
        self._raw = raw

    def fetchone(self):
        r = self._raw.fetchone()
        return dict(r) if r is not None else None

    def fetchall(self):
        return [dict(r) for r in self._raw.fetchall()]


class Conn:
    """Engine-agnostic connection. Use ?-placeholders in SQL."""
    def __init__(self, raw):
        self._raw = raw

    def execute(self, sql, params=()):
        return _Cursor(self._raw.execute(_q(sql), tuple(params)))

    def insert(self, sql, params=()):
        """Run an INSERT and return the new row's id (works on both engines)."""
        if IS_PG:
            cur = self._raw.execute(_q(sql) + " RETURNING id", tuple(params))
            return cur.fetchone()["id"]
        cur = self._raw.execute(_q(sql), tuple(params))
        return cur.lastrowid

    def commit(self):
        self._raw.commit()

    def close(self):
        self._raw.close()


def _connect_raw():
    if IS_PG:
        return psycopg.connect(DATABASE_URL, row_factory=dict_row)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_conn() -> Conn:
    return Conn(_connect_raw())


# ----------------------------------------------------------------- schema
def init_db() -> None:
    """Create all tables if they do not exist (safe to call on every startup)."""
    pk = "SERIAL PRIMARY KEY" if IS_PG else "INTEGER PRIMARY KEY AUTOINCREMENT"
    statements = [
        f"""CREATE TABLE IF NOT EXISTS users (
            id        {pk},
            username  TEXT UNIQUE NOT NULL,
            salt      TEXT NOT NULL,
            pw_hash   TEXT NOT NULL,
            token     TEXT,
            created   TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS profiles (
            user_id      INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            target_role  TEXT DEFAULT '',
            skills       TEXT DEFAULT '[]',
            resume_text  TEXT DEFAULT '',
            updated      TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS analyses (
            id            {pk},
            user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role          TEXT,
            match_percent INTEGER,
            readiness     TEXT,
            matched       TEXT DEFAULT '[]',
            missing       TEXT DEFAULT '[]',
            created       TEXT NOT NULL
        )""",
        f"""CREATE TABLE IF NOT EXISTS progress_history (
            id        {pk},
            user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role      TEXT,
            score     INTEGER,
            learned   TEXT DEFAULT '[]',
            created   TEXT NOT NULL
        )""",
        f"""CREATE TABLE IF NOT EXISTS jd_matches (
            id            {pk},
            user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role          TEXT,
            match_percent INTEGER,
            matched       TEXT DEFAULT '[]',
            missing       TEXT DEFAULT '[]',
            jd_excerpt    TEXT DEFAULT '',
            created       TEXT NOT NULL
        )""",
        f"""CREATE TABLE IF NOT EXISTS chats (
            id        {pk},
            user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role      TEXT,
            sender    TEXT,
            content   TEXT,
            created   TEXT NOT NULL
        )""",
    ]
    raw = _connect_raw()
    for s in statements:
        raw.execute(s)
    raw.commit()
    raw.close()
