"""
analyzer.py — Core Analysis Logic
=================================
Three responsibilities (each a clear function for the viva):

1. extract_text_from_pdf()  -> reads resume PDF into plain text
2. extract_skills()         -> finds known skills in that text  (NLP step)
3. analyze_gap()            -> compares student skills vs role  (gap logic)

No AI here — this module is pure, testable Python. The AI part
(roadmap generation) lives separately in app.py.
"""

import re
import pdfplumber
from roles_data import (
    MASTER_SKILLS, SKILL_ALIASES, ROLE_REQUIREMENTS,
    SKILL_HOURS, DEFAULT_SKILL_HOURS,
    SKILL_DEMAND, DEFAULT_SKILL_DEMAND, HIGH_DEMAND_THRESHOLD,
    SKILL_CATEGORY, DEFAULT_CATEGORY,
)


def extract_text_from_pdf(pdf_file) -> str:
    """Read all text from an uploaded PDF file object."""
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        return f"__ERROR__{e}"
    return text


def extract_skills(text: str) -> list:
    """
    Find which known skills appear in the text.
    Strategy: lowercase the text, then for every skill (and alias)
    check if it appears as a whole word. Returns canonical names.
    This keyword + alias matching is the NLP component.
    """
    if not text:
        return []

    text_low = " " + text.lower() + " "
    found = set()

    # 1. direct match against master skills
    for skill in MASTER_SKILLS:
        # word-boundary match so "r" doesn't match inside "react"
        pattern = r"(?<![a-zA-Z0-9+#])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9+#])"
        if re.search(pattern, text_low):
            found.add(skill)

    # 2. alias match (js -> JavaScript, ml -> Machine Learning, ...)
    for alias, canonical in SKILL_ALIASES.items():
        pattern = r"(?<![a-zA-Z0-9+#])" + re.escape(alias) + r"(?![a-zA-Z0-9+#])"
        if re.search(pattern, text_low):
            found.add(canonical)

    return sorted(found)


def analyze_gap(student_skills: list, target_role: str) -> dict:
    """
    Compare the student's skills against a target role.
    Returns matched/missing core, matched/missing bonus, and a
    weighted match score (core counts more than bonus).
    """
    role = ROLE_REQUIREMENTS.get(target_role)
    if not role:
        return {}

    student_set = set(student_skills)
    core = role["core"]
    bonus = role["bonus"]

    matched_core = [s for s in core if s in student_set]
    missing_core = [s for s in core if s not in student_set]
    matched_bonus = [s for s in bonus if s in student_set]
    missing_bonus = [s for s in bonus if s not in student_set]

    # Weighted score: core skills are 80% of score, bonus 20%
    core_score = (len(matched_core) / len(core)) * 80 if core else 0
    bonus_score = (len(matched_bonus) / len(bonus)) * 20 if bonus else 0
    match_percent = round(core_score + bonus_score)

    # Readiness label
    if match_percent >= 80:
        readiness = "Job Ready 🚀"
    elif match_percent >= 55:
        readiness = "Almost There 💪"
    elif match_percent >= 30:
        readiness = "Building Up 📈"
    else:
        readiness = "Just Starting 🌱"

    return {
        "match_percent": match_percent,
        "readiness": readiness,
        "matched_core": matched_core,
        "missing_core": missing_core,
        "matched_bonus": matched_bonus,
        "missing_bonus": missing_bonus,
        "all_missing": missing_core + missing_bonus,
    }


# ---------------------------------------------------------------------------
# ADVANCED HELPERS (timeline, demand, resume quality, JD matching)
# Still pure, testable Python — no AI, easy to defend in a viva.
# ---------------------------------------------------------------------------

def estimate_timeline(missing_skills: list, hours_per_week: int = 10) -> dict:
    """
    Estimate how long it takes to learn the missing skills, by summing each
    skill's approximate learning hours and dividing by a weekly study budget.
    """
    per_skill = [(s, SKILL_HOURS.get(s, DEFAULT_SKILL_HOURS)) for s in missing_skills]
    total_hours = sum(h for _, h in per_skill)
    hours_per_week = max(1, hours_per_week)
    weeks = total_hours / hours_per_week
    months = weeks / 4.345
    per_skill.sort(key=lambda x: x[1], reverse=True)
    return {
        "total_hours": total_hours,
        "hours_per_week": hours_per_week,
        "weeks": round(weeks),
        "months": round(months, 1),
        "per_skill": per_skill,
    }


def rank_in_demand(skills: list) -> list:
    """Return [(skill, demand_score, is_high_demand)] sorted by demand desc."""
    ranked = []
    for s in skills:
        d = SKILL_DEMAND.get(s, DEFAULT_SKILL_DEMAND)
        ranked.append((s, d, d >= HIGH_DEMAND_THRESHOLD))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


def score_resume_quality(text: str) -> dict:
    """
    Heuristic resume quality check — looks beyond skills for the things
    recruiters expect: contact, links, summary, projects, education,
    experience, a skills section and a sensible length.
    Returns a 0-100 score plus a list of (issue, tip) for what's missing.
    """
    if not text or text.startswith("__ERROR__"):
        return {"score": 0, "passed": [], "issues": [("Could not read resume",
                "Upload a text-based PDF (not a scanned image).")], "word_count": 0}

    low = text.lower()
    has_email = bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
    has_github = "github.com" in low
    has_linkedin = "linkedin.com" in low
    has_links = has_github or has_linkedin or "http" in low
    has_summary = any(k in low for k in ("summary", "objective", "profile", "about me"))
    has_projects = "project" in low
    has_education = any(k in low for k in ("education", "bachelor", "b.e", "b.tech",
                                           "degree", "university", "college"))
    has_experience = any(k in low for k in ("experience", "intern", "worked", "employment"))
    has_skills = "skill" in low
    words = len(text.split())
    good_length = 150 <= words <= 1200

    checks = [
        ("Contact email", has_email, 15, "Add a professional email at the top."),
        ("GitHub / LinkedIn link", has_github or has_linkedin, 20,
         "Add your GitHub and LinkedIn URLs — recruiters look for them."),
        ("Summary / Objective", has_summary, 10,
         "Add a 2-3 line summary stating your target role and strengths."),
        ("Projects section", has_projects, 20,
         "Add 2-3 projects with what you built and the tech used."),
        ("Education", has_education, 10, "Include your degree, college and year."),
        ("Experience / Internship", has_experience, 10,
         "Add internships, freelance or relevant experience (even if brief)."),
        ("Skills section", has_skills, 10,
         "List your technical skills clearly in one section."),
        ("Sensible length", good_length, 5,
         "Aim for ~1 page (roughly 150-1200 words)."),
    ]
    score = sum(w for _, ok, w, _ in checks if ok)
    passed = [label for label, ok, _, _ in checks if ok]
    issues = [(label, tip) for label, ok, _, tip in checks if not ok]
    return {"score": score, "passed": passed, "issues": issues, "word_count": words,
            "has_links": has_links}


def jd_match(resume_skills: list, jd_text: str) -> dict:
    """
    Match a resume against a specific pasted job description: extract the
    skills the JD asks for, then score the resume's coverage of them.
    """
    jd_skills = extract_skills(jd_text)
    resume_set = set(resume_skills)
    matched = [s for s in jd_skills if s in resume_set]
    missing = [s for s in jd_skills if s not in resume_set]
    match_percent = round(len(matched) / len(jd_skills) * 100) if jd_skills else 0
    return {
        "jd_skills": jd_skills,
        "matched": matched,
        "missing": missing,
        "match_percent": match_percent,
    }


def ats_score(text: str, student_skills=None) -> dict:
    """
    ATS-friendliness score (0-100). Most companies filter resumes with software
    first, so this rewards machine-readable structure: parseable text, contact
    info, standard sections, links, and QUANTIFIED achievements.
    """
    if not text or text.startswith("__ERROR__"):
        return {"score": 0, "checks": [],
                "tips": [("Unreadable resume",
                          "Export a text-based PDF (not a scanned image) so ATS can parse it.")],
                "has_achievements": False}
    low = text.lower()
    has_email = bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
    has_phone = bool(re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text))
    sections = sum(1 for k in ("skill", "experience", "education", "project") if k in low)
    has_sections = sections >= 3
    has_links = ("github.com" in low) or ("linkedin.com" in low)
    impact_verb = any(v in low for v in ("increase", "reduc", "improv", "achiev",
                                         "built", "develop", "led ", "automat",
                                         "optimi", "boost", "grew", "saved"))
    has_numbers = len(re.findall(r"\d+\s?%|\d+\s?\+|\b\d{2,}\b", text)) >= 2
    has_achievements = impact_verb and has_numbers
    words = len(text.split())
    good_len = 150 <= words <= 1200
    rich = (student_skills is None) or (len(student_skills) >= 5)

    checks = [
        ("Machine-readable text", True, 10, ""),
        ("Contact email", has_email, 12, "Put a clear email at the very top."),
        ("Phone number", has_phone, 8, "Add a phone number in the header."),
        ("Standard sections", has_sections, 20,
         "Use clear headings: Skills, Experience, Education, Projects."),
        ("GitHub / LinkedIn link", has_links, 15,
         "Add your GitHub and LinkedIn URLs - recruiters click them."),
        ("Measurable achievements", has_achievements, 20,
         "Quantify impact, e.g. 'improved model accuracy by 18%' or 'cut runtime 2x'."),
        ("Enough skill keywords", rich, 10,
         "List more of the role's keywords so ATS keyword-matching ranks you higher."),
        ("ATS-friendly length", good_len, 5, "Aim for ~1 page (150-1200 words)."),
    ]
    score = sum(w for _, ok, w, _ in checks if ok)
    tips = [(lbl, tip) for lbl, ok, _, tip in checks if not ok and tip]
    return {"score": score, "checks": [(l, ok) for l, ok, _, _ in checks],
            "tips": tips, "has_achievements": has_achievements}


def skill_categories(role: str, student_skills: list) -> list:
    """
    For the radar chart: per broad category, what % of the role's skills in that
    category the student already has. Returns [(category, have_percent, total)].
    """
    req = ROLE_REQUIREMENTS.get(role, {})
    role_skills = list(dict.fromkeys(req.get("core", []) + req.get("bonus", [])))
    student = set(student_skills)
    cats = {}
    for sk in role_skills:
        cat = SKILL_CATEGORY.get(sk, DEFAULT_CATEGORY)
        have, total = cats.get(cat, (0, 0))
        cats[cat] = (have + (1 if sk in student else 0), total + 1)
    out = [(c, round(h / t * 100), t) for c, (h, t) in cats.items()]
    out.sort(key=lambda x: x[0])
    return out
