"""
build_embeddings.py — Offline skill-embedding index (via OpenRouter)
====================================================================
Creates `skill_embeddings.json`, the vector index that powers semantic skill
detection (see semantic.py). Embeddings come from OpenRouter (see llm.py), so
you need OPENROUTER_API_KEY set (env or .streamlit/secrets.toml). Optionally set
OPENROUTER_EMBED_MODEL (default: openai/text-embedding-3-small).

    python build_embeddings.py

Because OpenRouter is credit-based (no free-tier daily cap), the whole index
builds in one run. Requests are batched; progress is saved incrementally and the
run RESUMES if interrupted (already-embedded skills are skipped). If the embedding
model changes, the old index is ignored and rebuilt automatically.
"""

import os
import sys
import json
import math
import hashlib
import datetime

from roles_data import MASTER_SKILLS
import llm

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skill_embeddings.json")
BATCH = 96


def _normalize(vec):
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm else list(vec)


def atomic_save(payload):
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    os.replace(tmp, OUT_PATH)


def load_existing(model, dim):
    """Resume from a previous run only if the model AND dimension match (else the
    old index is from a different provider/model, so start fresh)."""
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


def main():
    if not llm.get_key():
        print("ERROR: no OpenRouter API key found.\n"
              "  Set OPENROUTER_API_KEY (env or .streamlit/secrets.toml).")
        sys.exit(1)

    skills = sorted(set(MASTER_SKILLS))
    print(f"Preparing to embed {len(skills)} skills -> {os.path.basename(OUT_PATH)}")

    # Probe once to learn which model actually served the request and its dim.
    probe, model, err = llm.embed(["Python"])
    if not probe:
        print(f"ERROR: embedding probe failed ({err}). Check the key / model / credits.")
        sys.exit(1)
    dim = len(probe[0])
    print(f"Using model: {model}  (dim={dim})")

    vectors = load_existing(model, dim)
    if vectors:
        print(f"Resuming — {len(vectors)} already embedded, {len(skills) - len(vectors)} to go.")
    todo = [s for s in skills if s not in vectors]
    skills_hash = hashlib.sha256("\n".join(skills).encode("utf-8")).hexdigest()[:16]

    def save():
        atomic_save({
            "model": model, "dim": dim, "count": len(vectors),
            "skills_hash": skills_hash,
            "built_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "vectors": vectors,
        })

    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        vecs, used, e = llm.embed(chunk, model=model)
        if not vecs or len(vecs) != len(chunk):
            save()
            print(f"\nStopped after {len(vectors)}/{len(skills)} ({e}). "
                  f"Re-run build_embeddings.bat to continue (it resumes).")
            break
        for skill, vec in zip(chunk, vecs):
            vectors[skill] = [round(x, 6) for x in _normalize(vec)]
        save()
        print(f"  embedded {len(vectors)}/{len(skills)}")

    save()
    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"\nDONE: {len(vectors)}/{len(skills)} skills embedded ({size_kb:.0f} KB).")
    if len(vectors) < len(skills):
        print("  Some skills still missing — re-run build_embeddings.bat to finish.")
    else:
        print("  Full index complete! Next: run push_fixes.bat, then reload the app.")


if __name__ == "__main__":
    main()
