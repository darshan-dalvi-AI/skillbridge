"""
build_faiss.py — OPTIONAL FAISS index for semantic search
=========================================================
Builds a FAISS index from skill_embeddings.json so semantic.py can do approximate
nearest-neighbour search instead of the (already-fast) pure-Python cosine loop.

At 455 skills this is NOT a speed win — brute force is plenty — so it's a demo of
the technique, kept optional. FAISS is deliberately NOT in requirements.txt so it
doesn't slow the app's cold start on Streamlit Cloud.

    pip install faiss-cpu numpy
    python build_faiss.py                 # writes skill_faiss.index + labels
    # then enable at runtime:  set SKILLBRIDGE_USE_FAISS=1

Any missing pieces (no faiss, no env flag, no index file) simply mean the app
keeps using the pure-Python backend.
"""

import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
EMB_PATH = os.path.join(HERE, "skill_embeddings.json")
IDX_PATH = os.path.join(HERE, "skill_faiss.index")
LABELS_PATH = os.path.join(HERE, "skill_faiss_labels.json")


def main():
    if not os.path.exists(EMB_PATH):
        print("ERROR: skill_embeddings.json not found — run build_embeddings.py first.")
        sys.exit(1)
    try:
        import numpy as np
        import faiss
    except Exception as e:
        print("ERROR: FAISS build needs numpy + faiss-cpu.\n"
              f"  pip install faiss-cpu numpy\n  ({e})")
        sys.exit(1)

    with open(EMB_PATH, encoding="utf-8") as f:
        data = json.load(f)
    vectors = data.get("vectors") or {}
    if not vectors:
        print("ERROR: index has no vectors.")
        sys.exit(1)

    labels = list(vectors.keys())
    mat = np.asarray([vectors[s] for s in labels], dtype="float32")
    # vectors are already unit-normalised at build time, so inner product == cosine
    index = faiss.IndexFlatIP(mat.shape[1])
    index.add(mat)
    faiss.write_index(index, IDX_PATH)
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels, f)

    print(f"DONE: {len(labels)} vectors (dim={mat.shape[1]}) -> "
          f"{os.path.basename(IDX_PATH)} + {os.path.basename(LABELS_PATH)}")
    print("Enable at runtime with the env var:  SKILLBRIDGE_USE_FAISS=1")
    print("(Without that flag, or without faiss installed, the app uses pure-Python cosine.)")


if __name__ == "__main__":
    main()
