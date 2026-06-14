"""
market_data.py — Job-Market Signal (AI + curated)
=================================================
Honest take on "live job-market data". True scraping of LinkedIn/Naukri is
against their ToS and breaks once deployed, so this module gives two reliable
layers instead:

1. curated_market()  — deterministic, offline ranking of a role's skills by a
   maintained demand score. Always works, no key needed.
2. ai_market_pulse() — an OPTIONAL Gemini call that writes a short, current
   "what employers want right now" brief for the role (India context). If
   there's no key or the call fails, the UI simply falls back to layer 1.
"""

from roles_data import (
    ROLE_REQUIREMENTS, SKILL_DEMAND, DEFAULT_SKILL_DEMAND,
)


def curated_market(role: str, top_n: int = 8) -> list:
    """Return [(skill, demand_score)] for a role, ranked by demand."""
    req = ROLE_REQUIREMENTS.get(role, {})
    skills = list(dict.fromkeys(req.get("core", []) + req.get("bonus", [])))
    ranked = sorted(
        ((s, SKILL_DEMAND.get(s, DEFAULT_SKILL_DEMAND)) for s in skills),
        key=lambda x: x[1], reverse=True,
    )
    return ranked[:top_n]


def ai_market_pulse(role: str, api_key: str, model: str = "gemini-2.5-flash"):
    """
    Return (text, error). Asks Gemini for a short current market read for the
    role in India. Caller falls back to curated_market() when error is set.
    """
    if not api_key:
        return None, "no_key"
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = (
            "You are a tech-hiring analyst for the Indian job market in 2026.\n"
            f"In 120 words or less, summarise what employers currently want from a "
            f"fresher / junior {role}.\n"
            "Cover: the 5-6 most in-demand skills, one or two rising tools, and one "
            "hiring trend. Use short bullet points. Be specific and practical."
        )
        resp = client.models.generate_content(model=model, contents=prompt)
        return resp.text, None
    except Exception as e:
        return None, str(e)
