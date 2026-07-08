"""Tests for planner.py — week-by-week plan + .ics export."""
import planner


def test_weekly_plan_preserves_hours_and_respects_budget():
    weeks = planner.build_weekly_plan([("A", 10), ("B", 6), ("C", 4)], hours_per_week=10)
    assert weeks
    assert sum(w["hours"] for w in weeks) == 20
    assert all(w["hours"] <= 10 for w in weeks)
    assert [w["week"] for w in weeks] == list(range(1, len(weeks) + 1))


def test_big_skill_splits_across_weeks():
    weeks = planner.build_weekly_plan([("Big", 25)], hours_per_week=10)
    assert len(weeks) >= 3
    assert sum(h for w in weeks for _, h in w["items"]) == 25


def test_ics_structure_is_valid():
    weeks = planner.build_weekly_plan([("A", 10), ("B", 5)], hours_per_week=10)
    ics = planner.plan_to_ics(weeks, title="Test")
    assert ics.startswith("BEGIN:VCALENDAR")
    assert "END:VCALENDAR" in ics
    assert ics.count("BEGIN:VEVENT") == len(weeks) == ics.count("END:VEVENT")


def test_ics_escapes_special_characters():
    weeks = planner.build_weekly_plan([("C++, Node; Go", 10)], hours_per_week=10)
    ics = planner.plan_to_ics(weeks)
    assert ("\\," in ics) or ("\\;" in ics)


def test_empty_inputs():
    assert planner.build_weekly_plan([]) == []
    assert "Nothing" in planner.plan_to_markdown([])
