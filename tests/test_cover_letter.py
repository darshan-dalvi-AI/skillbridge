"""Tests for cover_letter.py — prompt builder."""
import cover_letter


def test_prompt_includes_role_skills_company_language():
    p = cover_letter.build_cover_letter_prompt(
        "Asha", "Data Analyst", ["SQL", "Python"],
        jd_text="", company="Acme", language="English")
    assert "Data Analyst" in p
    assert "SQL" in p and "Python" in p
    assert "Acme" in p
    assert "English" in p


def test_prompt_handles_missing_jd():
    p = cover_letter.build_cover_letter_prompt("", "AI Engineer", [], "")
    assert "AI Engineer" in p
    assert "no specific job description" in p.lower()


def test_prompt_embeds_jd_when_present():
    p = cover_letter.build_cover_letter_prompt(
        "X", "Backend Developer", ["Go"], jd_text="We need Go and Kubernetes.")
    assert "Kubernetes" in p
