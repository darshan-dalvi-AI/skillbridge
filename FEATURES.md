# SkillBridge — New Add-ons

Everything below is live in the app (or one setup step away). All of it degrades
gracefully — missing key/index/deps never breaks the app.

## In the app

**Sentence-level semantic matching (higher recall).**
`semantic.py` now splits a résumé/JD into sentences, embeds them in one batched
call, and scores each skill by its best match to *any* sentence — so a skill
implied by a single line is caught (not diluted by the whole document). Threshold
`SEMANTIC_THRESHOLD = 0.55` in `semantic.py`.

**Accept / reject inferred skills.**
In the sidebar, semantically-inferred skills appear as an editable list — untick
anything wrong and the analysis updates. Keeps the score honest.

**JD-tab semantic matching.**
The **🎯 JD Match** tab now also infers the skills a job description *implies*,
not just the ones it names — better coverage for prose-style JDs.

**AI cover-letter generator.**
Bottom of the **JD Match** tab: generates a tailored, 3-paragraph cover letter
from your skills + the pasted JD (+ optional company/language), with a `.txt`
download. Logic in `cover_letter.py`.

**Week-by-week study plan + calendar.**
Top of **Roadmap & Courses**: a slider (hours/week) packs your missing skills into
weeks, shows the plan, and exports a `.ics` file you can import into Google/Apple/
Outlook Calendar. Logic in `planner.py`.

## Optional setup

**FAISS vector search (demo).**
Not needed at 455 skills, and kept out of `requirements.txt` so cold start stays
fast. To demo it:

```
pip install faiss-cpu numpy
python build_faiss.py            # builds skill_faiss.index (+ labels)
set SKILLBRIDGE_USE_FAISS=1      # then run the app
```

Without the flag / faiss / index, the app uses the pure-Python cosine backend.
`semantic.py` reports which backend ran in its result meta.

**Weekly email nudge.**
`send_nudge.py` + `.github/workflows/nudge.yml` (Mondays 09:00 UTC). It DRY-RUNS
(prints, sends nothing) until you add repo secrets:
`SENDGRID_API_KEY`, `NUDGE_TO`, `NUDGE_FROM` (optionally `NUDGE_NAME/ROLE/MATCH/SKILLS`).
Trigger it manually from the Actions tab (workflow_dispatch) to test.

## Tests & CI

```
pip install -r requirements-dev.txt
pytest -q
```

26 tests cover `analyzer`, `semantic`, `planner`, `cover_letter`, and the nudge
composer. `.github/workflows/ci.yml` runs them on every push — a green badge for
your repo and viva.
