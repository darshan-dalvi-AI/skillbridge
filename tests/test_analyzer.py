"""Tests for analyzer.py — the pure skill-gap logic."""
import analyzer
import roles_data


def test_extract_skills_keyword_and_alias():
    found = analyzer.extract_skills("Experienced in Python, SQL and js.")
    assert "Python" in found
    assert "SQL" in found
    assert "JavaScript" in found          # alias js -> JavaScript


def test_extract_skills_empty_input():
    assert analyzer.extract_skills("") == []
    assert analyzer.extract_skills(None) == []


def test_extract_skills_returns_independent_lists():
    a = analyzer.extract_skills("Python")
    b = analyzer.extract_skills("Python")
    assert a == b and a is not b           # cached core, fresh copy per call
    a.append("ZZZ")
    assert "ZZZ" not in analyzer.extract_skills("Python")


def test_analyze_gap_full_and_empty():
    role = next(iter(roles_data.ROLE_REQUIREMENTS))
    req = roles_data.ROLE_REQUIREMENTS[role]
    all_skills = list(dict.fromkeys(req["core"] + req["bonus"]))
    full = analyzer.analyze_gap(all_skills, role)
    assert full["match_percent"] == 100
    assert full["all_missing"] == []
    empty = analyzer.analyze_gap([], role)
    assert empty["match_percent"] == 0
    assert set(empty["all_missing"]) == set(all_skills)


def test_estimate_timeline():
    t = analyzer.estimate_timeline(["A", "B", "C"])
    assert t["total_hours"] > 0
    assert t["months"] > 0
    assert len(t["per_skill"]) == 3


def test_jd_match_scores_coverage():
    jm = analyzer.jd_match(["Python"], "We are looking for Python and SQL developers.")
    assert "Python" in jm["matched"]
    assert "SQL" in jm["missing"]
    assert 0 <= jm["match_percent"] <= 100


def test_score_resume_quality_bounds():
    q = analyzer.score_resume_quality(
        "jane@example.com github.com/jane linkedin.com/in/jane summary projects "
        "education experience skills " + "content " * 200)
    assert 0 <= q["score"] <= 100
    assert isinstance(q["passed"], list)


def test_ats_score_bounds():
    a = analyzer.ats_score(
        "email@x.com +91 9876543210 skills experience education project "
        "github.com/x improved accuracy by 20% and cut runtime 2x " + "w " * 200,
        ["a", "b", "c", "d", "e"])
    assert 0 <= a["score"] <= 100


def test_extract_experience_detects_years():
    e = analyzer.extract_experience("I have 5 years of experience building Python systems.")
    assert e["years"] >= 5
    assert e["level"] in ("Mid", "Senior")
