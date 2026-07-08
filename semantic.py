"""
semantic.py — Embedding-based (RAG) skill inference
===================================================
The keyword matcher in analyzer.extract_skills() is literal: it only finds a
skill if the résumé writes that exact word (or a known alias). This module adds
a semantic layer that also catches skills the résumé *implies*.

Pipeline (RAG-style):
  offline (build_embeddings.py):  embed every skill  ->  skill_embeddings.json
  runtime  (here):                split the résumé into SENTENCES, embed them in
                                  ONE batched call, and match each skill by its
                                  BEST similarity to any sentence (higher recall
                                  than embedding the whole résumé as one vector).

Search backend:
  * default = pure-Python cosine (perfect for a few hundred skills, no deps).
  * optional = FAISS (set env SKILLBRIDGE_USE_FAISS=1 and build skill_faiss.index
    with build_faiss.py). Any FAISS error falls back to pure-Python, so it can
    never break the app. FAISS is kept OUT of requirements.txt so cold start
    stays fast — it's an opt-in demo of the technique.

Everything is defensive: no index / no key / embedding error -> ([], meta) and
the caller keeps the keyword-only result.
"""

import os
import re
import json
import math
from functools import lru_cache

# ---------------------------------------------------------------- config
_HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(_HERE, "skill_embeddings.json")
FAISS_INDEX_PATH = os.path.join(_HERE, "skill_faiss.index")
FAISS_LABELS_PATH = os.path.join(_HERE, "skill_faiss_labels.json")

EMBED_MODELS = ["gemini-embedding-001", "text-embedding-004", "embedding-001"]

# Cosine cut-off for accepting an inferred skill. Higher = stricter. 0.55–0.70 is
# sensible; 0.55 favours recall (catches secondary skills a résumé only describes)
# at a small risk of the odd loose match. Raise it if you see skills that aren't
# really implied.
SEMANTIC_THRESHOLD = 0.55
MAX_SEMANTIC = 12          # cap on inferred skills added per résumé
MAX_SENTENCES = 40         # cap sentences embedded per résumé (bounds cost/latency)
MIN_WORDS = 3              # ignore very short fragments when splitting


# ---------------------------------------------------------------- index load
def index_exists() -> bool:
    """True if a precomputed skill-embedding index is present."""
    return os.path.exists(INDEX_PATH)


@lru_cache(maxsize=1)
def _load_index():
    """Load and cache the index once per process.
    Returns {"model", "dim", "vectors": {skill: (float, ...)}} or None on any error."""
    if not os.path.exists(INDEX_PATH):
        return None
    try:
        with open(INDEX_PATH, encoding="utf-8") as f:
            data = json.load(f)
        vectors = {s: tuple(v) for s, v in (data.get("vectors") or {}).items()}
        if not vectors:
            return None
        return {"model": data.get("model", ""), "dim": data.get("dim", 0),
                "vectors": vectors}
    except Exception:
        return None


# ---------------------------------------------------------------- math helpers
def _normalize(vec):
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm else list(vec)


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


_SENT_SPLIT = re.compile(r"[.!?\n\r;•|]+")


def _split_sentences(text: str):
    """Split a résumé into de-duplicated sentence-ish chunks (capped), so a skill
    can match the ONE line that implies it instead of the whole diluted document."""
    parts = [p.strip() for p in _SENT_SPLIT.split(text or "")]
    sents = [p for p in parts if len(p.split()) >= MIN_WORDS]
    if not sents:
        whole = (text or "").strip()
        return [whole] if whole else []
    seen, out = set(), []
    for s in sents:
        k = s.lower()
        if k not in seen:
            seen.add(k)
            out.append(s)
        if len(out) >= MAX_SENTENCES:
            break
    return out


# ---------------------------------------------------------------- embedding
def _make_cfg(task_type, output_dim):
    try:
        from google.genai import types
        try:
            return (types.EmbedContentConfig(task_type=task_type, output_dimensionality=output_dim)
                    if output_dim else types.EmbedContentConfig(task_type=task_type))
        except Exception:
            return types.EmbedContentConfig(task_type=task_type)
    except Exception:
        return None


def _extract_values(resp):
    """One float-vector from a single-content embed response (any SDK shape)."""
    embs = getattr(resp, "embeddings", None)
    if embs:
        first = embs[0]
        vals = getattr(first, "values", None)
        if vals:
            return vals
        if isinstance(first, (list, tuple)):
            return first
    emb = getattr(resp, "embedding", None)
    if emb is not None:
        return getattr(emb, "values", emb)
    if isinstance(resp, dict):
        e = resp.get("embedding") or resp.get("embeddings")
        if isinstance(e, dict):
            return e.get("values")
        return e
    return None


def _extract_all_values(resp):
    """List of float-vectors from a batched embed response."""
    embs = getattr(resp, "embeddings", None)
    if embs:
        out = []
        for e in embs:
            vals = getattr(e, "values", None)
            out.append(list(vals) if vals else (list(e) if isinstance(e, (list, tuple)) else None))
        return out
    single = _extract_values(resp)
    return [single] if single else None


def embed_text(text: str, api_key: str, model: str = None, output_dim: int = None,
               task_type: str = "RETRIEVAL_QUERY"):
    """Embed ONE string. Returns (unit_vector, model_used, None) or (None, None, err).
    `model`/`output_dim` should come from the index so the query matches the stored
    skill vectors."""
    if not api_key:
        return None, None, "no_key"
    if not (text or "").strip():
        return None, None, "empty_text"
    try:
        from google import genai
    except Exception as e:
        return None, None, f"sdk_import_failed: {e}"
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        return None, None, str(e)

    cfg = _make_cfg(task_type, output_dim)
    last = "unknown embedding error"
    for m in ([model] if model else EMBED_MODELS):
        try:
            resp = (client.models.embed_content(model=m, contents=text, config=cfg)
                    if cfg is not None else
                    client.models.embed_content(model=m, contents=text))
            vals = _extract_values(resp)
            if vals:
                return _normalize(list(vals)), m, None
            last = "empty embedding response"
        except Exception as e:
            last = str(e)
            continue
    return None, None, last


def embed_texts(texts, api_key: str, model: str = None, output_dim: int = None,
                task_type: str = "RETRIEVAL_QUERY"):
    """Embed a LIST of strings in ONE batched call. Returns (list_of_unit_vectors,
    model_used, None) or (None, None, err). Falls back to per-item embedding if the
    batch call is rejected."""
    texts = [t for t in (texts or []) if (t or "").strip()]
    if not api_key:
        return None, None, "no_key"
    if not texts:
        return None, None, "empty_text"
    try:
        from google import genai
    except Exception as e:
        return None, None, f"sdk_import_failed: {e}"
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        return None, None, str(e)

    cfg = _make_cfg(task_type, output_dim)
    last = "unknown embedding error"
    for m in ([model] if model else EMBED_MODELS):
        try:
            resp = (client.models.embed_content(model=m, contents=texts, config=cfg)
                    if cfg is not None else
                    client.models.embed_content(model=m, contents=texts))
            vecs = _extract_all_values(resp)
            if vecs and len(vecs) == len(texts) and all(vecs):
                return [_normalize(list(v)) for v in vecs], m, None
            last = "batch shape mismatch"
        except Exception as e:
            last = str(e)
            continue

    # fallback: embed one at a time (slower, but robust)
    out, used = [], None
    for t in texts:
        v, mm, e = embed_text(t, api_key, model=model, output_dim=output_dim, task_type=task_type)
        if v is None:
            return None, None, e
        out.append(v)
        used = mm
    return out, used, None


# ---------------------------------------------------------------- search backends
def faiss_available() -> bool:
    """True if FAISS is importable AND a prebuilt FAISS index is on disk."""
    try:
        import faiss  # noqa: F401
        return os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_LABELS_PATH)
    except Exception:
        return False


def _faiss_enabled() -> bool:
    return (os.environ.get("SKILLBRIDGE_USE_FAISS", "").lower() in ("1", "true", "yes")
            and faiss_available())


@lru_cache(maxsize=1)
def _load_faiss():
    import faiss
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(FAISS_LABELS_PATH, encoding="utf-8") as f:
        labels = json.load(f)
    return index, labels


def _faiss_scores(chunk_vecs, already):
    """Approx nearest-neighbour search per sentence; returns {skill: best_sim}."""
    import numpy as np
    index, labels = _load_faiss()
    q = np.asarray(chunk_vecs, dtype="float32")
    k = min(MAX_SEMANTIC * 3, len(labels))
    sims, ids = index.search(q, k)           # IndexFlatIP on unit vectors == cosine
    scores = {}
    for row_s, row_i in zip(sims, ids):
        for d, i in zip(row_s, row_i):
            if i < 0:
                continue
            skill = labels[i]
            if skill in already:
                continue
            if float(d) > scores.get(skill, 0.0):
                scores[skill] = float(d)
    return scores


def _bruteforce_scores(chunk_vecs, idx, already):
    """Pure-Python cosine: {skill: best_sim over sentences}."""
    scores = {}
    for skill, svec in idx["vectors"].items():
        if skill in already:
            continue
        best = 0.0
        for cv in chunk_vecs:
            if len(cv) == len(svec):
                d = _dot(cv, svec)
                if d > best:
                    best = d
        scores[skill] = best
    return scores


def _score_skills(chunk_vecs, idx, already):
    """Score every candidate skill by best similarity to any sentence. Uses FAISS
    when explicitly enabled, else pure-Python; FAISS errors fall back silently."""
    if _faiss_enabled():
        try:
            return _faiss_scores(chunk_vecs, already), "faiss"
        except Exception:
            pass
    return _bruteforce_scores(chunk_vecs, idx, already), "bruteforce"


# ---------------------------------------------------------------- public API
def infer_skills(resume_text: str, already_found, api_key: str,
                 threshold: float = SEMANTIC_THRESHOLD, max_add: int = MAX_SEMANTIC):
    """
    Return (added_skills, meta).

    added_skills : skills the résumé is semantically closest to, EXCLUDING anything
                   in `already_found`, sorted by confidence and capped at `max_add`.
    meta         : {"source", "model", "backend", "chunks", "scores", "error"}.

    Any failure (no index / no key / embedding error) yields ([], meta).
    """
    idx = _load_index()
    if idx is None:
        return [], {"source": "no_index",
                    "error": "Run build_embeddings.py to create skill_embeddings.json."}

    chunks = _split_sentences(resume_text)
    if not chunks:
        return [], {"source": "error", "error": "empty_text"}

    cvecs, model, err = embed_texts(chunks, api_key,
                                    model=idx.get("model") or None,
                                    output_dim=idx.get("dim") or None,
                                    task_type="RETRIEVAL_QUERY")
    if not cvecs:
        return [], {"source": "error", "error": err}

    already = set(already_found or [])
    scores, backend = _score_skills(cvecs, idx, already)
    accepted = [(s, v) for s, v in scores.items() if v >= threshold]
    accepted.sort(key=lambda x: x[1], reverse=True)
    accepted = accepted[:max_add]
    return ([s for s, _ in accepted],
            {"source": "semantic", "model": model, "backend": backend,
             "chunks": len(chunks),
             "scores": {s: round(v, 3) for s, v in accepted}, "error": None})
