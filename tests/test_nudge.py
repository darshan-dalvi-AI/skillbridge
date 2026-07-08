"""Tests for send_nudge.compose_nudge (pure text builder)."""
import send_nudge


def test_compose_nudge_contains_key_facts():
    body = send_nudge.compose_nudge("Darshan", "AI Engineer", 62, ["Docker", "SQL", "MLOps"])
    assert "Darshan" in body
    assert "AI Engineer" in body
    assert "62%" in body
    assert "Docker" in body


def test_compose_nudge_handles_empty_skills():
    body = send_nudge.compose_nudge("", "Data Analyst", 0, [])
    assert "Data Analyst" in body
    assert "0%" in body
