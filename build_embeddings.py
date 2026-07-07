"""
build_embeddings.py — Offline precompute of the skill-embedding index (RAG)
===========================================================================
Creates `skill_embeddings.json`, the vector index that powers semantic skill
detection in the app (see semantic.py).

    python build_embeddings.py            # key from env or .streamlit/secrets.toml
    python build_embeddings.py YOUR_KEY   # or pass the Gemini key directly

Free-tier friendly:
  * ONE request per skill, throttled to stay under the per-minute limit.
  * Exponential backoff on 429 (quota) instead of giving up.
  * Incremental save + RESUME — if the run is interrupted or hits the daily cap,
    just double-click build_embeddings.bat again and it continues where it left
    off (already-embedded skills are skipped).
Vectors are truncated to 768 dims and unit-normalised, so the index stays small
and runtime matching is a fast dot product.
"""

import os
import re
import sys
import json
import math
import time
import hashlib
import datetime

from roles_data import MASTER_SKILLS

# gemini-embedding-001 first: text-embedding-004 is 404 on some keys. Order =
# preference; the first model that actually works is used and recorded.
EMBED_MODELS = ["gemini-embedding-001", "text-embedding-004", "embedding-001"]
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skill_embeddings.json")
OUT_DIM = 768          # Matryoshka-truncate big models down to this (small file, good quality)
THROTTLE = 1.0         # seconds between requests (~60/min, under the 100 RPM free limit)
SAVE_EVERY = 20        # write progress to disk every N new vectors (so resume works)
MAX_RETRIES = 6        # per-skill retries on a 429 before skipping it


# ---------------------------------------------------------------- key resolution
def resolve_key(argv) -> str:
    if len(argv) > 1 and argv[1].strip():
        return argv[1].strip()
    for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        if os.environ.get(var):
            return os.environ[var].strip()
    secrets = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           ".streamlit", "secrets.toml")
    if os.path.exists(secrets):
        try:
            with open(secrets, encoding="utf-8") as f:
                txt = f.read()
            m = re.search(r'(?mi)^\s*GEMINI_API_KEY\s*=\s*["\']([^"\']+)["\']', txt)
            if m:
                return m.group(1).strip()
        except Exception:
            pass
    return ""


# ---------------------------------------------------------------- helpers
def _normalize(vec):
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm else list(vec)


def _values(resp):
    """Pull one float-vector from a single-content embed response (any SDK shape)."""
    embs = getattr(resp, "embeddings", None)
    if embs:
        first = embs[0]
        return list(getattr(first, "values", first))
    emb = getattr(resp, "embedding", None)
    if emb is not None:
        return list(getattr(emb, "values", emb))
    if isinstance(resp, dict):
        e = resp.get("embedding") or resp.get("embeddings")
        if isinstance(e, dict):
            return e.get("values")
        return e
    return None


def _is_quota(msg: str) -> bool:
    m = (msg or "").lower()
    return "429" in m or "resource_exhausted" in m or "quota" in m or "rate limit" in m


def make_config(task_type):
    """EmbedContentConfig with task type + output dim, or None if unsupported."""
    try:
        from google.genai import types
        try:
            return types.EmbedContentConfig(task_type=task_type, output_dimensionality=OUT_DIM)
        except Exception:
            return types.EmbedContentConfig(task_type=task_type)
    except Exception:
        return None


def embed_one(client, model, cfg, text):
    """Embed a single string with backoff on 429. Returns (vector|None, error|None)."""
    delay = 6.0
    for attempt in range(MAX_RETRIES):
        try:
            kw = {"model": model, "contents": text}
            if cfg is not None:
                kw["config"] = cfg
            resp = client.models.embed_content(**kw)
            vals = _values(resp)
            if vals:
                return vals, None
            return None, "empty response"
        except Exception as e:
            msg = str(e)
            if _is_quota(msg) and attempt < MAX_RETRIES - 1:
                print(f"      quota hit — waiting {int(delay)}s (retry {attempt + 1}/{MAX_RETRIES-1})")
                time.sleep(delay)
                delay = min(delay * 2, 120)
                continue
            return None, msg
    return None, "max_retries_exhausted"


def pick_model(client):
    """Return (model, cfg, dim) for the first EMBED_MODELS entry that works."""
    for model in EMBED_MODELS:
        cfg = make_config("RETRIEVAL_DOCUMENT")
        vec, err = embed_one(client, model, cfg, "Python")
        if vec:
            return model, cfg, len(vec)
        print(f"  · {model} unavailable ({str(err)[:80]})")
    return None, None, 0


def atomic_save(payload):
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    os.replace(tmp, OUT_PATH)


def load_existing(model, dim):
    """Resume from a previous run — but ONLY if the model AND dimension match this
    run (else the old file is stale/incompatible, e.g. a different-dim attempt, so
    we start fresh). Also drops any vector whose length != dim."""
    if not os.path.exists(OUT_PATH):
        return {}
    try:
        with open(OUT_PATH, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("model") == model and int(data.get("dim", 0)) == int(dim):
            return {s: v for s, v in (data.get("vectors") or {}).items() if len(v) == dim}
    except Exception:
        pass
    return {}


# ---------------------------------------------------------------- main
def main():
    key = resolve_key(sys.argv)
    if not key:
        print("ERROR: no Gemini API key found.\n"
              "  Pass it:   python build_embeddings.py YOUR_KEY\n"
              "  or set env GEMINI_API_KEY, or put it in .streamlit/secrets.toml")
        sys.exit(1)

    try:
        from google import genai
    except Exception as e:
        print(f"ERROR: google-genai SDK not importable: {e}\n  pip install google-genai")
        sys.exit(1)
    client = genai.Client(api_key=key)

    skills = sorted(set(MASTER_SKILLS))
    print(f"Preparing to embed {len(skills)} skills -> {os.path.basename(OUT_PATH)}")

    model, cfg, dim = pick_model(client)
    if not model:
        print("ERROR: no embedding model worked with this key. Check the key / quota.")
        sys.exit(1)
    print(f"Using model: {model}  (dim={dim})")

    vectors = load_existing(model, dim)
    if vectors:
        print(f"Resuming — {len(vectors)} skills already embedded, "
              f"{len(skills) - len(vectors)} to go.")
    todo = [s for s in skills if s not in vectors]

    skills_hash = hashlib.sha256("\n".join(skills).encode("utf-8")).hexdigest()[:16]

    def save():
        atomic_save({
            "model": model, "dim": dim, "count": len(vectors),
            "skills_hash": skills_hash,
            "built_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "vectors": vectors,
        })

    new, failed = 0, 0
    for i, skill in enumerate(todo, 1):
        vec, err = embed_one(client, model, cfg, skill)
        if vec:
            vectors[skill] = [round(x, 6) for x in _normalize(vec)]
            new += 1
            if new % SAVE_EVERY == 0:
                save()
                print(f"  saved · {len(vectors)}/{len(skills)} embedded")
        else:
            failed += 1
            print(f"  ! skipped {skill!r}: {str(err)[:70]}")
            if _is_quota(err):
                # Daily cap likely reached — save and stop; re-run later to resume.
                save()
                print(f"\nStopped early on quota after {len(vectors)}/{len(skills)}. "
                      f"Re-run build_embeddings.bat later to continue (it resumes).")
                break
        time.sleep(THROTTLE)

    save()
    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"\nDONE for now: {len(vectors)}/{len(skills)} skills embedded "
          f"({size_kb:.0f} KB).")
    if len(vectors) < len(skills):
        print(f"  {len(skills) - len(vectors)} still missing — re-run build_embeddings.bat "
              f"to embed the rest (already-done skills are skipped).")
    else:
        print("  Full index complete! Next: run push_fixes.bat, then reload the app.")


if __name__ == "__main__":
    main()
