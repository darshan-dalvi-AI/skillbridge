"""
semantic.py — Optional embedding-based (RAG) skill inference
============================================================
The keyword matcher in analyzer.extract_skills() is precise but literal: it only
finds a skill if the résumé writes that exact word (or a known alias). It misses
skills the résumé *implies* — e.g. "trained convolutional neural nets on images"
clearly means Deep Learning / Computer Vision, but those words never appear.

This module adds a semantic layer on top, RAG-style:

  offline (build_embeddings.py):  embed every known skill once  ->  skill_embeddings.json
  runtime  (here):                embed the résumé once (cached) ->  cosine-match the
                                  skills it's closest to, above a confidence threshold

Design goals (all defensive, so the app NEVER breaks):
  * If the index file is missing, or there's no API key, or the embedding call
    fails -> we return NOTHING and the app silently stays keyword-only.
  * We only ADD skills the keyword matcher missed; we never remove its matches.
  * Vectors in the index are pre-normalised, so a runtime match is just a dot
    product (fast, pure-Python, no numpy dependency).
"""

import os
import json
import math
from functools import lru_cache

# ---------------------------------------------------------------- config
_HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(_HERE, "skill_embeddings.json")

# Embedding models tried in order (mirrors app.py's text-model fallback idea).
EMBED_MODELS = ["text-embedding-004", "gemini-embedding-001", "embedding-001"]

# Cosine-similarity cut-off for accepting an inferred skill. Higher = stricter
# (fewer, more confident matches). Tune this after you build the index and try a
# few real résumés — 0.55–0.70 is the sensible range for these models.
SEMANTIC_THRESHOLD = 0.62

# Never flood the analysis: cap how many inferred skills we add per résumé.
MAX_SEMANTIC = 10


# ---------------------------------------------------------------- index load
def index_exists() -> bool:
    """True if a precomputed skill-embedding index is present."""
    return os.path.exists(INDEX_PATH)


@lru_cache(maxsize=1)
def _load_index():
    """Load and cache the index once per process.
    Returns {"model", "dim", "vectors": {skill: (float, ...)}} or None on any error.
    Vectors are already unit-normalised at build time."""
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
    """Return a unit-length copy of vec (so later comparisons are pure dot products)."""
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0:
        return list(vec)
    return [x / norm for x in vec]


def _dot(a, b):
    """Dot product of two equal-length sequences (== cosine when both are unit vectors)."""
    return sum(x * y for x, y in zip(a, b))


# ---------------------------------------------------------------- embedding call
def embed_text(text: str, api_key: str, model: str = None, output_dim: int = None,
               task_type: str = "RETRIEVAL_QUERY"):
    """Embed one string with Gemini and return (unit_vector, model_used, None) or
    (None, None, error_message).

    `model` / `output_dim` should come from the index metadata so the résumé query
    is embedded with the SAME model and dimensionality as the stored skill vectors
    — otherwise the two vectors aren't comparable. Falls back to EMBED_MODELS only
    when no model is pinned. Defensive throughout, so any failure degrades to a
    silent keyword-only result instead of raising."""
    if not api_key:
        return None, None, "no_key"
    if not (text or "").strip():
        return None, None, "empty_text"
    try:
        from google import genai
    except Exception as e:                       # SDK not importable
        return None, None, f"sdk_import_failed: {e}"

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        return None, None, str(e)

    # Task-typed config, with matching output dim when the SDK supports it; fall
    # back gracefully if that import/signature isn't available in this version.
    cfg = None
    try:
        from google.genai import types
        try:
            cfg = (types.EmbedContentConfig(task_type=task_type, output_dimensionality=output_dim)
                   if output_dim else types.EmbedContentConfig(task_type=task_type))
        except Exception:
            cfg = types.EmbedContentConfig(task_type=task_type)
    except Exception:
        cfg = None

    last = "unknown embedding error"
    for m in ([model] if model else EMBED_MODELS):
        try:
            if cfg is not None:
                resp = client.models.embed_content(model=m, contents=text, config=cfg)
            else:
                resp = client.models.embed_content(model=m, contents=text)
            vals = _extract_values(resp)
            if vals:
                return _normalize(list(vals)), m, None
            last = "empty embedding response"
        except Exception as e:
            last = str(e)
            continue
    return None, None, last


def _extract_values(resp):
    """Pull the float vector out of whatever shape the SDK returned."""
    # new google-genai: resp.embeddings -> [ContentEmbedding(values=[...])]
    embs = getattr(resp, "embeddings", None)
    if embs:
        first = embs[0]
        vals = getattr(first, "values", None)
        if vals:
            return vals
        if isinstance(first, (list, tuple)):
            return first
    # older shape: resp.embedding.values  or  resp["embedding"]
    emb = getattr(resp, "embedding", None)
    if emb is not None:
        return getattr(emb, "values", emb)
    if isinstance(resp, dict):
        e = resp.get("embedding") or resp.get("embeddings")
        if isinstance(e, dict):
            return e.get("values")
        return e
    return None


# ---------------------------------------------------------------- public API
def infer_skills(resume_text: str, already_found, api_key: str,
                 threshold: float = SEMANTIC_THRESHOLD, max_add: int = MAX_SEMANTIC):
    """
    Return (added_skills, meta).

    added_skills : list[str] — skills from the index the résumé is semantically
                   closest to, EXCLUDING anything already in `already_found`,
                   sorted by confidence and capped at `max_add`.
    meta         : dict — {"source", "model", "scores": {skill: sim}, "error"}.

    Any failure (no index / no key / embedding error) yields ([], meta) so the
    caller just keeps the keyword-only result.
    """
    idx = _load_index()
    if idx is None:
        return [], {"source": "no_index",
                    "error": "Run build_embeddings.py to create skill_embeddings.json."}

    qvec, model, err = embed_text(resume_text, api_key,
                                  model=idx.get("model") or None,
                                  output_dim=idx.get("dim") or None,
                                  task_type="RETRIEVAL_QUERY")
    if qvec is None:
        return [], {"source": "error", "error": err}

    already = set(already_found or [])
    scored = []
    for skill, svec in idx["vectors"].items():
        if skill in already:
            continue
        if len(svec) != len(qvec):     # dimension mismatch -> skip safely
            continue
        sim = _dot(qvec, svec)
        if sim >= threshold:
            scored.append((skill, sim))

    scored.sort(key=lambda x: x[1], reverse=True)
    scored = scored[:max_add]
    return ([s for s, _ in scored],
            {"source": "semantic", "model": model,
             "scores": {s: round(v, 3) for s, v in scored}, "error": None})
