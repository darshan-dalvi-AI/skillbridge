# SkillBridge — Semantic (RAG) Skill Detection

An optional embedding layer that catches skills a résumé *implies* but never spells
out. It sits **on top of** the existing keyword matcher — it only ever adds skills,
never removes them, and silently disables itself if the index or API key is missing.

## Why

`analyzer.extract_skills()` is precise but literal — it needs the exact word or a
known alias. A résumé that says *"trained convolutional neural nets on image data"*
clearly implies **Deep Learning** and **Computer Vision**, but the keyword matcher
sees neither. The semantic layer closes that gap using embeddings.

## How it works (RAG shape)

```
OFFLINE  (build_embeddings.py, run once)
  MASTER_SKILLS ──embed (RETRIEVAL_DOCUMENT)──► skill_embeddings.json   (committed vector index)

RUNTIME  (semantic.py, per résumé)
  résumé text ──embed (RETRIEVAL_QUERY)──► query vector
  query vector ─cosine vs each skill vector─► skills above threshold ─► added to your matches
```

- **Precomputed index** = the fixed skill list, embedded once and committed. Loading
  it at runtime is instant.
- **One runtime embedding call per résumé**, and it's cached (`@st.cache_data`), so
  reruns cost nothing — the speed work we did earlier still holds.
- Vectors are **unit-normalised at build time**, so a runtime match is just a dot
  product (pure Python, no numpy dependency).

## Files

| File | Role |
|------|------|
| `build_embeddings.py` | Offline: embeds every skill → `skill_embeddings.json` |
| `build_embeddings.bat` | One-click runner for the above (reads your key from secrets) |
| `semantic.py` | Runtime: loads the index, embeds the résumé, returns inferred skills |
| `skill_embeddings.json` | The committed vector index (you generate this once) |
| `app.py` | Sidebar toggle **🧠 Smart semantic detection** + augmentation, all cached |

## Setup (one time)

1. Double-click **`build_embeddings.bat`**. It embeds the skills **one at a time**,
   throttled and with automatic back-off, and writes `skill_embeddings.json`. It
   saves as it goes and **resumes**, so it's safe to re-run.
2. Double-click **`push_fixes.bat`** to commit the code + the index to GitHub.
3. Reload the app. With a résumé uploaded/pasted you'll see the
   **🧠 Smart semantic detection** toggle (on by default). Turn it off for pure
   keyword matching.

The app is safe to deploy **before** step 1 — without the index the feature is a
no-op and the toggle simply doesn't appear.

### Free-tier / quota note

Embeddings use `gemini-embedding-001` (Google's free tier; `text-embedding-004`
isn't available on all keys). The free tier is rate-limited, so if the build
prints `429 / RESOURCE_EXHAUSTED` and stops early:

- It has **saved everything embedded so far.**
- Just **run `build_embeddings.bat` again** — it skips finished skills and
  continues. Repeat until it prints *"Full index complete!"* (a minute-per-run
  limit may mean two or three runs; a daily limit may mean running it again the
  next day). Already-embedded work is never lost.

## Tuning

In `semantic.py`:

- `SEMANTIC_THRESHOLD` (default `0.62`) — cosine cut-off. Raise it if you see loose
  matches; lower it if it's too shy. Sensible range 0.55–0.70.
- `MAX_SEMANTIC` (default `10`) — cap on inferred skills added per résumé.
- `EMBED_MODELS` — embedding model fallback chain.

Rebuild the index (`build_embeddings.bat`) only when you change the skill list or
the embedding model.

## Viva talking points

- **Retrieval-augmented matching**: a precomputed vector index (offline) queried
  live — the same architecture as production RAG, minus an LLM generation step.
- **Hybrid retrieval**: fast exact keyword matching + semantic recall, so you get
  precision *and* recall instead of choosing one.
- **Cost/latency engineering**: embeddings are precomputed; the single runtime call
  is cached per résumé, so the feature adds recall without hurting responsiveness.
- **Graceful degradation**: no key / no index / API error ⇒ automatic fallback to
  keyword-only. The app never breaks.
- **Task-typed embeddings**: skills embedded as `RETRIEVAL_DOCUMENT`, résumé as
  `RETRIEVAL_QUERY`, which is how these models are designed to be paired.
