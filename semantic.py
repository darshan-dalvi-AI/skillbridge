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

All embeddings go through OpenRouter (see llm.py). Search backend:
  * default = pure-Python cosine (perfect for a few hundred skills, no deps).
  * optional = FAISS (set env SKILLBRIDGE_USE_FAISS=1 and build skill_faiss.index
    with build_faiss.py); any FAISS error falls back to pure-Python.

Everything is defensive: no index / no key / embedding error -> ([], meta) and
the caller keeps the keyword-only result.
"""

import os
import re
import json
import math
from functools import lru_cache

import llm

# ---------------------------------------------------------------- config
_HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(_HERE, "skill_embeddings.json")
FAISS_INDEX_PATH = os.path.join(_HERE, "skill_faiss.index")
FAISS_LABELS_PATH = os.path.join(_HERE, "skill_faiss_labels.json")

# Cosine cut-off for accepting an inferred skill. Higher = stricter. 0.35–0.55 is
# sensible for OpenRouter embedding models (their raw cosines run lower than
# Gemini's); 0.40 favours recall. Raise it if you see skills that aren't implied.
SEMANTIC_THRESHOLD = 0.40
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


# ---------------------------------------------------------------- embedding (via OpenRouter)
def embed_text(text: str, api_key=None, model: str = None, output_dim: int = None,
               task_type: str = "RETRIEVAL_QUERY"):
    """Embed ONE string through OpenRouter. Returns (unit_vector, model_used, None)
    or (None, None, err). `api_key`/`output_dim`/`task_type` are accepted for
    backward compatibility but the provider (llm.py) manages the key and model."""
    if not (text or "").strip():
        return None, None, "empty_text"
    vecs, used, err = llm.embed([text], model=model)
    if not vecs:
        return None, None, err
    return _normalize(list(vecs[0])), used, None


def embed_texts(texts, api_key=None, model: str = None, output_dim: int = None,
                task_type: str = "RETRIEVAL_QUERY"):
    """Embed a LIST of strings in ONE OpenRouter request. Returns
    (list_of_unit_vectors, model_used, None) or (None, None, err)."""
    texts = [t for t in (texts or []) if (t or "").strip()]
    if not texts:
        return None, None, "empty_text"
    vecs, used, err = llm.embed(texts, model=model)
    if not vecs or len(vecs) != len(texts):
        return None, None, (err or "embedding count mismatch")
    return [_normalize(list(v)) for v in vecs], used, None


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
def infer_skills(resume_text: str, already_found, api_key=None,
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

    cvecs, model, err = embed_texts(chunks, model=idx.get("model") or None)
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
