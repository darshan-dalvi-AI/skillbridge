"""
main.py — SkillBridge REST API (FastAPI)
========================================
A small, honest backend that the Streamlit app calls over HTTP to persist every
user's data in SQLite (local) or Postgres (cloud, via DATABASE_URL).

Auth: passwords are hashed with PBKDF2-HMAC-SHA256 + per-user salt (same scheme
as the old local auth.py). On register/login the server issues a random bearer
token; protected endpoints require `Authorization: Bearer <token>` matching the
user_id in the path.

Run:  uvicorn backend.main:app --port 8000   (from the skillgap folder)
"""

import hashlib
import secrets
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel

from backend import database as db

_ITERATIONS = 200_000

app = FastAPI(title="SkillBridge API", version="1.0")


@app.on_event("startup")
def _startup():
    db.init_db()


# ----------------------------------------------------------------- security
def _hash(password: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), _ITERATIONS
    ).hex()


def _norm(username: str) -> str:
    return (username or "").strip().lower()


def require_user(user_id: int, authorization: Optional[str] = Header(None)):
    """Dependency: verify the bearer token belongs to user_id. Returns the row."""
    token = ""
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    conn = db.get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    if not token or token != row["token"]:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return row


# ----------------------------------------------------------------- schemas
class Creds(BaseModel):
    username: str
    password: str


class Profile(BaseModel):
    target_role: str = ""
    skills: List[str] = []
    resume_text: str = ""


class Analysis(BaseModel):
    role: str = ""
    match_percent: int = 0
    readiness: str = ""
    matched: List[str] = []
    missing: List[str] = []


class ProgressIn(BaseModel):
    role: str = ""
    score: int = 0
    learned: List[str] = []


class JDMatch(BaseModel):
    role: str = ""
    match_percent: int = 0
    matched: List[str] = []
    missing: List[str] = []
    jd_excerpt: str = ""


class ChatIn(BaseModel):
    role: str = ""
    sender: str = "user"
    content: str = ""


# ----------------------------------------------------------------- health
@app.get("/")
def health():
    return {"status": "ok", "service": "SkillBridge API", "version": "1.0"}


# ----------------------------------------------------------------- auth
@app.post("/register")
def register(c: Creds):
    username = _norm(c.username)
    if not username or not c.password:
        raise HTTPException(400, "Enter both a username and a password.")
    if len(username) < 3:
        raise HTTPException(400, "Username must be at least 3 characters.")
    if len(c.password) < 4:
        raise HTTPException(400, "Password must be at least 4 characters.")
    conn = db.get_conn()
    exists = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if exists:
        conn.close()
        raise HTTPException(409, "That username already exists — try logging in.")
    salt = secrets.token_hex(16)
    token = secrets.token_urlsafe(24)
    uid = conn.insert(
        "INSERT INTO users (username, salt, pw_hash, token, created) VALUES (?,?,?,?,?)",
        (username, salt, _hash(c.password, salt), token, db.now_iso()),
    )
    conn.execute(
        "INSERT INTO profiles (user_id, target_role, skills, resume_text, updated) "
        "VALUES (?,?,?,?,?)",
        (uid, "", "[]", "", db.now_iso()),
    )
    conn.commit()
    conn.close()
    return {"ok": True, "user_id": uid, "username": username, "token": token}


@app.post("/login")
def login(c: Creds):
    username = _norm(c.username)
    conn = db.get_conn()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "No account with that username — register first.")
    if _hash(c.password, row["salt"]) != row["pw_hash"]:
        conn.close()
        raise HTTPException(401, "Incorrect password.")
    token = secrets.token_urlsafe(24)
    conn.execute("UPDATE users SET token=? WHERE id=?", (token, row["id"]))
    conn.commit()
    conn.close()
    return {"ok": True, "user_id": row["id"], "username": username, "token": token}


# ----------------------------------------------------------------- profile
@app.get("/profile/{user_id}")
def get_profile(user_id: int, user=Depends(require_user)):
    conn = db.get_conn()
    p = conn.execute("SELECT * FROM profiles WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    if not p:
        return {"target_role": "", "skills": [], "resume_text": ""}
    return {"target_role": p["target_role"], "skills": db.loads(p["skills"]),
            "resume_text": p["resume_text"]}


@app.put("/profile/{user_id}")
def put_profile(user_id: int, body: Profile, user=Depends(require_user)):
    conn = db.get_conn()
    conn.execute(
        "INSERT INTO profiles (user_id, target_role, skills, resume_text, updated) "
        "VALUES (?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET "
        "target_role=excluded.target_role, skills=excluded.skills, "
        "resume_text=excluded.resume_text, updated=excluded.updated",
        (user_id, body.target_role, db.dumps(body.skills), body.resume_text, db.now_iso()),
    )
    conn.commit()
    conn.close()
    return {"ok": True}


# ----------------------------------------------------------------- analyses
@app.post("/analyses/{user_id}")
def add_analysis(user_id: int, body: Analysis, user=Depends(require_user)):
    conn = db.get_conn()
    rid = conn.insert(
        "INSERT INTO analyses (user_id, role, match_percent, readiness, matched, missing, "
        "created) VALUES (?,?,?,?,?,?,?)",
        (user_id, body.role, body.match_percent, body.readiness,
         db.dumps(body.matched), db.dumps(body.missing), db.now_iso()),
    )
    conn.commit()
    conn.close()
    return {"ok": True, "id": rid}


@app.get("/analyses/{user_id}")
def list_analyses(user_id: int, user=Depends(require_user)):
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT * FROM analyses WHERE user_id=? ORDER BY id DESC LIMIT 50", (user_id,)
    ).fetchall()
    conn.close()
    return [{"id": r["id"], "role": r["role"], "match_percent": r["match_percent"],
             "readiness": r["readiness"], "matched": db.loads(r["matched"]),
             "missing": db.loads(r["missing"]), "created": r["created"]} for r in rows]


# ----------------------------------------------------------------- progress
@app.post("/progress/{user_id}")
def add_progress(user_id: int, body: ProgressIn, user=Depends(require_user)):
    conn = db.get_conn()
    rid = conn.insert(
        "INSERT INTO progress_history (user_id, role, score, learned, created) "
        "VALUES (?,?,?,?,?)",
        (user_id, body.role, body.score, db.dumps(body.learned), db.now_iso()),
    )
    conn.commit()
    conn.close()
    return {"ok": True, "id": rid}


@app.get("/progress/{user_id}")
def get_progress(user_id: int, user=Depends(require_user)):
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT * FROM progress_history WHERE user_id=? ORDER BY id ASC LIMIT 200",
        (user_id,),
    ).fetchall()
    conn.close()
    history = [{"date": r["created"], "score": r["score"], "role": r["role"]} for r in rows]
    latest_learned = db.loads(rows[-1]["learned"]) if rows else []
    return {"latest_learned": latest_learned, "history": history}


# ----------------------------------------------------------------- jd matches
@app.post("/jd-matches/{user_id}")
def add_jd(user_id: int, body: JDMatch, user=Depends(require_user)):
    conn = db.get_conn()
    rid = conn.insert(
        "INSERT INTO jd_matches (user_id, role, match_percent, matched, missing, "
        "jd_excerpt, created) VALUES (?,?,?,?,?,?,?)",
        (user_id, body.role, body.match_percent, db.dumps(body.matched),
         db.dumps(body.missing), body.jd_excerpt[:400], db.now_iso()),
    )
    conn.commit()
    conn.close()
    return {"ok": True, "id": rid}


@app.get("/jd-matches/{user_id}")
def list_jd(user_id: int, user=Depends(require_user)):
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT * FROM jd_matches WHERE user_id=? ORDER BY id DESC LIMIT 50", (user_id,)
    ).fetchall()
    conn.close()
    return [{"id": r["id"], "role": r["role"], "match_percent": r["match_percent"],
             "matched": db.loads(r["matched"]), "missing": db.loads(r["missing"]),
             "jd_excerpt": r["jd_excerpt"], "created": r["created"]} for r in rows]


# ----------------------------------------------------------------- chats
@app.post("/chats/{user_id}")
def add_chat(user_id: int, body: ChatIn, user=Depends(require_user)):
    conn = db.get_conn()
    conn.execute(
        "INSERT INTO chats (user_id, role, sender, content, created) VALUES (?,?,?,?,?)",
        (user_id, body.role, body.sender, body.content, db.now_iso()),
    )
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/chats/{user_id}")
def list_chats(user_id: int, user=Depends(require_user)):
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT * FROM chats WHERE user_id=? ORDER BY id ASC LIMIT 200", (user_id,)
    ).fetchall()
    conn.close()
    return [{"sender": r["sender"], "content": r["content"], "role": r["role"],
             "created": r["created"]} for r in rows]


# ----------------------------------------------------------------- export all
@app.get("/export/{user_id}")
def export_all(user_id: int, user=Depends(require_user)):
    """Everything stored for a user — handy for the viva and a 'download my data' button."""
    return {
        "username": user["username"],
        "profile": get_profile(user_id, user),
        "analyses": list_analyses(user_id, user),
        "progress": get_progress(user_id, user),
        "jd_matches": list_jd(user_id, user),
        "chats": list_chats(user_id, user),
    }
