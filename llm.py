"""
llm.py — OpenRouter provider for ALL AI tasks
=============================================
Every AI call in SkillBridge (text generation AND embeddings) routes through this
one module, which talks to OpenRouter's OpenAI-compatible API:

    chat(prompt)        -> POST /api/v1/chat/completions   (roadmap, mentor, cover letter, …)
    embed(texts)        -> POST /api/v1/embeddings          (semantic skill index + résumé)

Config (env var OR .streamlit/secrets.toml, checked in that order):
    OPENROUTER_API_KEY       required
    OPENROUTER_MODEL         chat model slug        (default: google/gemini-2.0-flash-001)
    OPENROUTER_EMBED_MODEL   embedding model slug   (default: openai/text-embedding-3-small)

Both functions retry with backoff, fall back across a model chain, and never
raise — they return an error string so the UI can degrade gracefully.
"""

import os
import re
import time

import requests

_HERE = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://openrouter.ai/api/v1"
_REFERER = "https://skillbridge-darshan.streamlit.app/"
_TITLE = "SkillBridge"

# Fallback chains (the configured model, if any, is tried first).
CHAT_MODELS = ["google/gemini-2.0-flash-001", "openai/gpt-4o-mini"]
EMBED_MODELS = ["openai/text-embedding-3-small"]


# ---------------------------------------------------------------- config
def _cfg(name: str, default: str = "") -> str:
    """Read a config value from env → Streamlit secrets → .streamlit/secrets.toml."""
    v = (os.environ.get(name, "") or "").strip()
    if v:
        return v
    try:
        import streamlit as st
        if name in st.secrets:
            return str(st.secrets[name]).strip()
    except Exception:
        pass
    try:
        p = os.path.join(_HERE, ".streamlit", "secrets.toml")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                m = re.search(r'(?mi)^\s*' + re.escape(name) + r'\s*=\s*["\']([^"\']+)["\']', f.read())
            if m:
                return m.group(1).strip()
    except Exception:
        pass
    return default


def get_key() -> str:
    return _cfg("OPENROUTER_API_KEY", "")


def _headers(key: str) -> dict:
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": _REFERER,   # optional attribution for OpenRouter rankings
        "X-Title": _TITLE,
    }


def _is_transient(code: int, text: str) -> bool:
    t = (text or "").lower()
    return code in (408, 409, 429, 500, 502, 503, 529) or any(
        k in t for k in ("overloaded", "rate limit", "timeout", "temporarily"))


def _is_fatal(code: int, text: str) -> bool:
    t = (text or "").lower()
    return code in (401, 403) or "invalid api key" in t or "user not found" in t


def _models(explicit, configured_name, chain):
    picked = [explicit] if explicit else ([_cfg(configured_name)] + chain)
    seen, out = set(), []
    for m in picked:
        if m and m not in seen:
            seen.add(m)
            out.append(m)
    return out


# ---------------------------------------------------------------- chat
def chat(prompt: str, system: str = None, model: str = None,
         temperature: float = 0.7, timeout: int = 60):
    """Return (text, None) or (None, error_string). Retries + model fallback."""
    key = get_key()
    if not key:
        return None, "no_key"
    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
    last = "unknown error"
    for m in _models(model, "OPENROUTER_MODEL", CHAT_MODELS):
        for attempt in range(2):
            try:
                r = requests.post(f"{BASE_URL}/chat/completions", headers=_headers(key),
                                  json={"model": m, "messages": messages,
                                        "temperature": temperature}, timeout=timeout)
                if r.status_code == 200:
                    txt = ((((r.json() or {}).get("choices") or [{}])[0]
                            .get("message") or {}).get("content"))
                    if txt and txt.strip():
                        return txt, None
                    last = "The AI returned an empty response."
                    break
                last = f"{r.status_code}: {(r.text or '')[:200]}"
                if _is_fatal(r.status_code, r.text):
                    return None, last
                if _is_transient(r.status_code, r.text) and attempt == 0:
                    time.sleep(1.6)
                    continue
                break
            except Exception as e:
                last = str(e)
                if attempt == 0:
                    time.sleep(1.2)
                    continue
                break
    return None, last


# ---------------------------------------------------------------- embeddings
def embed(texts, model: str = None, timeout: int = 60):
    """Embed a string or list of strings in ONE request.
    Returns (list_of_raw_vectors, model_used, None) or (None, None, error_string).
    Callers normalise the vectors themselves."""
    key = get_key()
    if not key:
        return None, None, "no_key"
    inp = [texts] if isinstance(texts, str) else [t for t in (texts or []) if (t or "").strip()]
    if not inp:
        return None, None, "empty_text"
    last = "unknown error"
    for m in _models(model, "OPENROUTER_EMBED_MODEL", EMBED_MODELS):
        for attempt in range(3):
            try:
                r = requests.post(f"{BASE_URL}/embeddings", headers=_headers(key),
                                  json={"model": m, "input": inp}, timeout=timeout)
                if r.status_code == 200:
                    data = (r.json() or {}).get("data") or []
                    vecs = [d.get("embedding") for d in data]
                    if vecs and len(vecs) == len(inp) and all(vecs):
                        return vecs, m, None
                    last = "empty or mismatched embeddings"
                    break
                last = f"{r.status_code}: {(r.text or '')[:200]}"
                if _is_fatal(r.status_code, r.text):
                    return None, None, last
                if _is_transient(r.status_code, r.text) and attempt < 2:
                    time.sleep(2.0 * (attempt + 1))
                    continue
                break
            except Exception as e:
                last = str(e)
                if attempt < 2:
                    time.sleep(1.5)
                    continue
                break
    return None, None, last
