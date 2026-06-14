"""
report.py — Downloadable PDF Career Report
==========================================
Builds a clean PDF of the student's skill-gap analysis, timeline, salary
insight and (if generated) AI roadmap + projects, so they can keep results.

Uses fpdf2 (pure-Python, no system deps) and sanitises all text to latin-1 so
it never crashes on emojis, the rupee sign, or smart quotes.
"""

import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos

ACCENT = (123, 47, 247)
TEAL = (0, 150, 170)
DARK = (35, 35, 45)
GREY = (120, 120, 130)


def _ascii(s: str) -> str:
    if not s:
        return ""
    repl = {"₹": "Rs.", "—": "-", "–": "-", "•": "-",
            "“": '"', "”": '"', "‘": "'", "’": "'",
            "…": "...", "→": "->"}
    for k, v in repl.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "ignore").decode("latin-1")


def _clean_md(s: str) -> str:
    """Lightly strip markdown so the roadmap reads cleanly in plain PDF text."""
    if not s:
        return ""
    s = s.replace("**", "").replace("`", "")
    out = []
    for line in s.splitlines():
        line = line.rstrip()
        line = re.sub(r"^\s*#{1,6}\s*", "", line)
        line = re.sub(r"^\s*[\*\-]\s+", "- ", line)
        out.append(line)
    return "\n".join(out)


class _PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*GREY)
        self.cell(0, 6, _ascii("SkillBridge - AI Career & Skill-Gap Report"))
        self.ln(8)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 6, _ascii(f"Page {self.page_no()} - SkillBridge"), align="C")


def _heading(pdf, text):
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*ACCENT)
    pdf.multi_cell(0, 7, _ascii(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*DARK)


def _body(pdf, text, size=11):
    pdf.set_font("Helvetica", "", size)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 6, _ascii(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_report_pdf(data: dict) -> bytes:
    """
    data keys: name, role, generated_on, result(dict), timeline(dict),
    salary(dict|None), resume_score(dict|None), roadmap_text(str|None),
    projects_text(str|None)
    """
    result = data.get("result", {}) or {}
    pdf = _PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*ACCENT)
    pdf.multi_cell(0, 10, _ascii("SkillBridge Career Report"),
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*GREY)
    pdf.multi_cell(0, 6, _ascii(f"Candidate: {data.get('name', 'Student')}    "
                               f"Target role: {data.get('role', '-')}    "
                               f"Date: {data.get('generated_on', '')}"),
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    pct = int(result.get("match_percent", 0))
    _heading(pdf, f"Role Match: {pct}%  -  {result.get('readiness', '')}")
    bar_x, bar_w, bar_h = pdf.get_x(), 180, 6
    bar_y = pdf.get_y() + 1
    pdf.set_fill_color(225, 225, 232)
    pdf.rect(bar_x, bar_y, bar_w, bar_h, "F")
    pdf.set_fill_color(*TEAL)
    pdf.rect(bar_x, bar_y, max(1, bar_w * pct / 100), bar_h, "F")
    pdf.ln(10)

    have = result.get("matched_core", []) + result.get("matched_bonus", [])
    _heading(pdf, "Skills you already have")
    _body(pdf, ", ".join(have) if have else "None detected yet.")

    _heading(pdf, "Core skills to learn")
    _body(pdf, ", ".join(result.get("missing_core", [])) or "All core skills covered!")

    if result.get("missing_bonus"):
        _heading(pdf, "Bonus skills (good to have)")
        _body(pdf, ", ".join(result["missing_bonus"]))

    tl = data.get("timeline")
    if tl:
        _heading(pdf, "Estimated learning timeline")
        _body(pdf, f"About {tl['total_hours']} hours of study "
                   f"(~{tl['weeks']} weeks / ~{tl['months']} months) at "
                   f"{tl['hours_per_week']} hours per week.")

    sal = data.get("salary")
    if sal:
        _heading(pdf, "Salary insight (India, fresher - indicative)")
        _body(pdf, f"Typical range: Rs.{sal['low']}-{sal['high']} LPA  "
                   f"(median ~Rs.{sal['median']} LPA). Varies by company, city "
                   f"and skills.")

    rq = data.get("resume_score")
    if rq:
        _heading(pdf, f"Resume quality score: {rq['score']}/100")
        if rq.get("issues"):
            tips = "  ".join(f"- {lbl}: {tip}" for lbl, tip in rq["issues"][:6])
            _body(pdf, tips, size=10)
        else:
            _body(pdf, "Looks solid - all key sections present.")

    if data.get("roadmap_text"):
        _heading(pdf, "Your AI Learning Roadmap")
        _body(pdf, _clean_md(data["roadmap_text"]), size=10)

    if data.get("projects_text"):
        _heading(pdf, "Suggested Portfolio Projects")
        _body(pdf, _clean_md(data["projects_text"]), size=10)

    return bytes(pdf.output())
