# SkillBridge — Deployment Guide

How to take SkillBridge from `localhost` to a public website, and what to watch out for.

---

## 1. What the app is made of

| Piece | File(s) | Runs on | Role |
|-------|---------|---------|------|
| **Frontend** | `app.py` (+ data modules) | port **8510** | Streamlit UI |
| **Backend** | `backend/main.py`, `backend/database.py` | port **8000** | FastAPI REST API |
| **Database** | `backend/skillbridge.db` | local file | SQLite (all user data) |

The frontend talks to the backend over HTTP through `api_client.py`, using the
URL in the env var **`SKILLBRIDGE_API_URL`** (default `http://127.0.0.1:8000`).
If the backend is unreachable, the app automatically falls back to local
storage and never crashes.

---

## 2. The one thing that breaks "going live"

Right now the frontend points at `http://127.0.0.1:8000` — that only exists **on
your PC**. If you deploy *just* the Streamlit app to the cloud, it can't reach
that address, so it silently switches to ephemeral local storage (which resets
on the host). **To keep real saving online you must also host the backend and a
real database, then point the app at them.**

---

## 3. Recommendation

- **For your viva / demo:** keep running locally with `run.bat`. It's the most
  reliable, and you can show the live backend + DB Browser. This is the
  strongest option for a competition.
- **For a shareable public link:** follow Option B below.

---

## Option A — Local (current, already working)

Double-click **`run.bat`**. It installs dependencies, starts the backend
(port 8000) in one window, then the app (port 8510). Done.

---

## Option B — Full cloud deploy (all free tiers)

Three pieces: **Streamlit Community Cloud** (frontend) + **Render** (backend) +
**Neon** (Postgres database).

### Step 1 — Push the project to GitHub
- Create a repo and push the `skillgap/` folder.
- Confirm `.gitignore` excludes `.streamlit/secrets.toml`, `*.db`, and
  `user_data.json` (already set up) so you never commit secrets or local data.

### Step 2 — Database: Neon Postgres (free + persistent)
- **Do not use Render's own free Postgres** — it **expires 30 days** after
  creation. Use **Neon** (or Supabase); their free tier is persistent and adds
  connection pooling.
- Sign up at **neon.tech** → create a project → copy the connection string
  (`postgresql://user:pass@host/dbname`).
- ✅ **No code change needed:** the backend **already** auto-switches to
  Postgres when **`DATABASE_URL`** is set (and uses SQLite otherwise).
  `psycopg[binary]` is in `requirements.txt`, so Render installs it for you.
  Just create the Neon database and pass its URL as `DATABASE_URL` (Step 3).

### Step 3 — Backend: Render Web Service (free)
- Render dashboard → **New → Web Service** → connect your GitHub repo →
  set **Root Directory** = `skillgap`.
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Environment variables:** `DATABASE_URL` (from Neon), `GEMINI_API_KEY`,
  `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`.
- **Free-tier note:** the service **sleeps after 15 min** of no traffic and
  takes **~1 minute** to wake on the next request (750 free hours/month).
- After it deploys, copy the public URL, e.g.
  `https://skillbridge-api.onrender.com`.

### Step 4 — Frontend: Streamlit Community Cloud (free)
- **share.streamlit.io** → **New app** → pick your repo →
  **Main file path** = `skillgap/app.py`.
- In **Advanced settings → Secrets**, add:
  ```toml
  SKILLBRIDGE_API_URL = "https://skillbridge-api.onrender.com"
  GEMINI_API_KEY = "your-gemini-key"
  ADZUNA_APP_ID  = "your-adzuna-id"
  ADZUNA_APP_KEY = "your-adzuna-key"
  ```
- `api_client` reads `SKILLBRIDGE_API_URL` from the environment **and** from
  `st.secrets`, so either path points the app at your Render backend.

### Step 5 — Test it
- Open the Streamlit URL → **Register** → the account box should read
  **"☁️ Backend (...)"** (not "Local").
- The **first** action after the backend was asleep may take ~1 minute
  (Render waking up); after that it's fast.

---

## 4. Hardening (only if real users will use it)

- **HTTPS** is automatic on both Render and Streamlit Cloud.
- The current login is **demo-grade**. For real users, add rate-limiting on
  `/register` & `/login`, restrict CORS to your frontend's domain, rotate the
  bearer token periodically, and consider email verification.
- **Never commit secrets** — always use each platform's Secrets/Env settings.

---

## 5. Quick reference

| Piece | Host | Free? | Watch out for |
|-------|------|-------|---------------|
| Frontend (Streamlit) | Streamlit Community Cloud | ✅ | main file = `skillgap/app.py` |
| Backend (FastAPI) | Render Web Service | ✅ | sleeps after 15 min idle (~1 min cold start) |
| Database | Neon Postgres | ✅ | persistent; backend auto-uses it via `DATABASE_URL` |

> TL;DR: Demo locally with `run.bat`. To go public: GitHub → Neon Postgres →
> Render backend → Streamlit Cloud frontend, and set `SKILLBRIDGE_API_URL`.
