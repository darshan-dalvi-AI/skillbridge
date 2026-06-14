"""
jobs_api.py — Live Job-Market Data via the Adzuna API
=====================================================
Pulls REAL job postings for a role in India from Adzuna's official API and
extracts the skills employers actually ask for (ranked by how many ads mention
them). This is the honest "live data" path: a proper API, not fragile scraping.

Credentials (free): create an account at https://developer.adzuna.com/ to get an
app_id + app_key, then add them to .streamlit/secrets.toml:
    ADZUNA_APP_ID = "..."
    ADZUNA_APP_KEY = "..."

With no key (or any error) it falls back to the curated demand index, so the app
never breaks.
"""

import os
import json
import urllib.request
import urllib.parse
from collections import Counter

from analyzer import extract_skills
from market_data import curated_market

ADZUNA_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/1"


def get_adzuna_creds():
    try:
        import streamlit as st
        app_id = st.secrets.get("ADZUNA_APP_ID", "")
        app_key = st.secrets.get("ADZUNA_APP_KEY", "")
        if app_id and app_key:
            return app_id, app_key
    except Exception:
        pass
    return os.environ.get("ADZUNA_APP_ID", ""), os.environ.get("ADZUNA_APP_KEY", "")


def _skills_from_results(results):
    counter = Counter()
    for job in results:
        text = (job.get("title", "") or "") + ". " + (job.get("description", "") or "")
        for sk in extract_skills(text):
            counter[sk] += 1
    return counter


def fetch_live_skills(role, country="in", max_jobs=25, timeout=12):
    """
    Return (ranked_skills, meta). ranked_skills = [(skill, mentions)] from real
    Adzuna ads. meta = {'source': 'adzuna'|'curated', 'jobs': n, 'error': ...}.
    Falls back to curated demand on missing key / error.
    """
    app_id, app_key = get_adzuna_creds()
    if not app_id or not app_key:
        return curated_market(role, top_n=12), {"source": "curated", "error": "no_key"}
    try:
        params = urllib.parse.urlencode({
            "app_id": app_id, "app_key": app_key, "what": role,
            "where": "India", "results_per_page": max_jobs,
            "content-type": "application/json",
        })
        url = ADZUNA_URL.format(country=country) + "?" + params
        req = urllib.request.Request(url, headers={"User-Agent": "SkillBridge/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        results = data.get("results", []) or []
        ranked = _skills_from_results(results).most_common(12)
        if not ranked:
            return curated_market(role, top_n=12), {"source": "curated", "error": "no_skills"}
        return ranked, {"source": "adzuna", "jobs": len(results),
                        "total": data.get("count")}
    except Exception as e:
        return curated_market(role, top_n=12), {"source": "curated", "error": str(e)[:140]}


def match_live(student_skills, ranked):
    """
    Match the student's skills against LIVE (or curated) ranked demand.
    ranked = [(skill, count)] where count = job mentions (Adzuna) or demand
    score (curated). Returns a weighted match % plus have/missing lists that
    keep each skill's real-world frequency, so the UI can say e.g.
    "Docker - wanted in 14 of 20 jobs, you're missing it".
    """
    student = set(student_skills)
    total = sum(c for _, c in ranked) or 1
    have = [(s, c) for s, c in ranked if s in student]
    missing = [(s, c) for s, c in ranked if s not in student]
    have_weight = sum(c for _, c in have)
    return {
        "have": have,
        "missing": missing,
        "match_percent": round(have_weight / total * 100),
        "total_mentions": sum(c for _, c in ranked),
        "n_skills": len(ranked),
    }
