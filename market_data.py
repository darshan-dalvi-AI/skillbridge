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


def ai_market_pulse(role: str, api_key=None, model: str = None):
    """
    Return (text, error). Asks the AI (OpenRouter, via llm.chat) for a short
    current market read for the role in India. Caller falls back to
    curated_market() when error is set. `api_key` is accepted for backward
    compatibility but ignored — llm.py manages credentials.
    """
    import llm
    prompt = (
        "You are a tech-hiring analyst for the Indian job market in 2026.\n"
        f"In 120 words or less, summarise what employers currently want from a "
        f"fresher / junior {role}.\n"
        "Cover: the 5-6 most in-demand skills, one or two rising tools, and one "
        "hiring trend. Use short bullet points. Be specific and practical."
    )
    return llm.chat(prompt, model=model)
