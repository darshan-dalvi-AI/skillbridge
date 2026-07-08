"""
cover_letter.py — AI cover-letter prompt builder
================================================
Builds the Gemini prompt for a tailored cover letter from the student's skills,
target role and (optionally) a pasted job description. Kept separate from app.py
so the prompt logic is unit-testable; the app passes the returned prompt to
gemini_generate().
"""


def build_cover_letter_prompt(name: str, target_role: str, skills, jd_text: str = "",
                              company: str = "", tone: str = "professional",
                              language: str = "English") -> str:
    """Return a prompt that asks Gemini for a concise, tailored cover letter."""
    skills_str = ", ".join(skills) if skills else "the core skills for this role"
    who = name.strip() or "a final-year engineering student"
    jd_block = (f"\n\nTailor it to THIS job description:\n\"\"\"\n{jd_text.strip()[:2500]}\n\"\"\""
                if (jd_text or "").strip() else
                f"\n\nThere is no specific job description; target a typical {target_role} role.")
    company_line = f" at {company.strip()}" if (company or "").strip() else ""

    return (
        f"Write a {tone}, confident cover letter for {who} applying for a "
        f"{target_role} position{company_line}.\n"
        f"The candidate's key skills: {skills_str}.\n"
        f"{jd_block}\n\n"
        "Requirements:\n"
        "- 3 short paragraphs, under ~250 words total.\n"
        "- Open with genuine interest in the role; middle paragraph maps the "
        "candidate's skills to what the role needs; close with a call to action.\n"
        "- Specific and honest — do NOT invent employers, degrees, or metrics that "
        "weren't given. Refer to skills and projects only in general terms.\n"
        "- No placeholders like [Company] left unfilled; if something is unknown, "
        "phrase it naturally instead.\n"
        f"- Write the entire letter in {language}.\n"
        "Return only the letter text."
    )
