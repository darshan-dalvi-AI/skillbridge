"""
api_client.py — Streamlit ⇄ FastAPI backend bridge
==================================================
The Streamlit app talks to the SkillBridge REST API (backend/main.py) through
this module. Two design goals:

1. Persist EVERYTHING per user (profile, analyses, progress history, JD matches,
   AI-mentor chat) by calling the backend over HTTP.
2. NEVER crash the app if the backend isn't running. Every call is wrapped; if
   the API is unreachable we transparently fall back to the local auth.py JSON
   store for login/progress, and silently skip the richer saves. So the demo
   works whether or not the backend process is up.

A "session" dict is returned on login/register and passed back to save/fetch
calls:  {"mode": "api"|"local", "user_id": int|None, "token": str, "username": str}
"""

import os
import requests

import auth  # local JSON fallback (offline mode)

def _resolve_api_url() -> str:
    """Where the backend lives. Priority:
    1) env var SKILLBRIDGE_API_URL (Render/Streamlit Cloud expose secrets as env too)
    2) Streamlit secrets [SKILLBRIDGE_API_URL] (set it in the app's Secrets UI)
    3) local default http://127.0.0.1:8000
    """
    url = (os.environ.get("SKILLBRIDGE_API_URL", "") or "").strip()
    if url:
        return url.rstrip("/")
    try:
        import streamlit as st
        if "SKILLBRIDGE_API_URL" in st.secrets:
            return str(st.secrets["SKILLBRIDGE_API_URL"]).strip().rstrip("/")
    except Exception:
        pass
    return "http://127.0.0.1:8000"


API_URL = _resolve_api_url()
_TIMEOUT = (2.5, 6)  # (connect, read) seconds — fast offline detection


# ----------------------------------------------------------------- low level
def _headers(session):
    tok = (session or {}).get("token", "")
    return {"Authorization": f"Bearer {tok}"} if tok else {}


def backend_online() -> bool:
    try:
        r = requests.get(f"{API_URL}/", timeout=_TIMEOUT)
        return r.status_code == 200
    except Exception:
        return False


def _post(path, json=None, session=None):
    r = requests.post(f"{API_URL}{path}", json=json, headers=_headers(session), timeout=_TIMEOUT)
    return r


def _get(path, session=None):
    r = requests.get(f"{API_URL}{path}", headers=_headers(session), timeout=_TIMEOUT)
    return r


# ----------------------------------------------------------------- auth
def register(username, password):
    """Returns (ok, message, session)."""
    try:
        r = _post("/register", json={"username": username, "password": password})
        if r.status_code == 200:
            d = r.json()
            return True, "Account created — you're logged in!", {
                "mode": "api", "user_id": d["user_id"], "token": d["token"],
                "username": d["username"]}
        return False, r.json().get("detail", "Registration failed."), None
    except Exception:
        # offline fallback -> local auth.py
        ok, msg = auth.register(username, password)
        sess = {"mode": "local", "user_id": None, "token": "",
                "username": (username or "").strip().lower()} if ok else None
        return ok, msg + (" (offline)" if ok else ""), sess


def authenticate(username, password):
    """Returns (ok, message, session)."""
    try:
        r = _post("/login", json={"username": username, "password": password})
        if r.status_code == 200:
            d = r.json()
            return True, "Logged in.", {
                "mode": "api", "user_id": d["user_id"], "token": d["token"],
                "username": d["username"]}
        return False, r.json().get("detail", "Login failed."), None
    except Exception:
        ok, msg = auth.authenticate(username, password)
        sess = {"mode": "local", "user_id": None, "token": "",
                "username": (username or "").strip().lower()} if ok else None
        return ok, msg + (" (offline)" if ok else ""), sess


def is_api(session) -> bool:
    return bool(session) and session.get("mode") == "api" and session.get("user_id")


# ----------------------------------------------------------------- saves (best effort)
def save_profile(session, target_role, skills, resume_text=""):
    """PUT the profile (upsert). Returns True on success."""
    if not is_api(session):
        return False
    try:
        uid = session["user_id"]
        r = requests.put(f"{API_URL}/profile/{uid}",
                         json={"target_role": target_role, "skills": list(skills),
                               "resume_text": resume_text or ""},
                         headers=_headers(session), timeout=_TIMEOUT)
        return r.status_code == 200
    except Exception:
        return False


def save_analysis(session, role, match_percent, readiness, matched, missing):
    if not is_api(session):
        return False
    try:
        uid = session["user_id"]
        r = _post(f"/analyses/{uid}", json={"role": role, "match_percent": int(match_percent),
                  "readiness": readiness, "matched": list(matched), "missing": list(missing)},
                  session=session)
        return r.status_code == 200
    except Exception:
        return False


def save_jd(session, role, match_percent, matched, missing, jd_excerpt=""):
    if not is_api(session):
        return False
    try:
        uid = session["user_id"]
        r = _post(f"/jd-matches/{uid}", json={"role": role, "match_percent": int(match_percent),
                  "matched": list(matched), "missing": list(missing),
                  "jd_excerpt": (jd_excerpt or "")[:400]}, session=session)
        return r.status_code == 200
    except Exception:
        return False


def save_chat(session, role, sender, content):
    if not is_api(session):
        return False
    try:
        uid = session["user_id"]
        r = _post(f"/chats/{uid}", json={"role": role, "sender": sender, "content": content},
                  session=session)
        return r.status_code == 200
    except Exception:
        return False


# ----------------------------------------------------------------- progress (api or local)
def get_progress(session, username=""):
    """Return progress in the legacy shape {learned, role, history} for the UI.
    Uses the API when online, else the local auth.py store."""
    if is_api(session):
        try:
            uid = session["user_id"]
            d = _get(f"/progress/{uid}", session=session).json()
            return {"learned": d.get("latest_learned", []), "role": "",
                    "history": d.get("history", [])}
        except Exception:
            pass
    return auth.get_progress(username or (session or {}).get("username", ""))


def save_progress(session, username, role, score, learned):
    """Persist a progress point. API -> progress_history row; local -> JSON."""
    if is_api(session):
        try:
            uid = session["user_id"]
            r = _post(f"/progress/{uid}", json={"role": role, "score": int(score),
                      "learned": list(learned)}, session=session)
            return r.status_code == 200
        except Exception:
            pass
    # local fallback
    prog = auth.get_progress(username)
    prog["learned"] = list(learned)
    prog["role"] = role
    prog.setdefault("history", []).append({"score": int(score), "role": role})
    return auth.save_progress(username, prog)


def get_history(session):
    """List of {date, score, role} for the progress-over-time chart (API only)."""
    if is_api(session):
        try:
            uid = session["user_id"]
            return _get(f"/progress/{uid}", session=session).json().get("history", [])
        except Exception:
            return []
    prog = auth.get_progress((session or {}).get("username", ""))
    return prog.get("history", [])


def export_all(session):
    if not is_api(session):
        return None
    try:
        uid = session["user_id"]
        return _get(f"/export/{uid}", session=session).json()
    except Exception:
        return None
