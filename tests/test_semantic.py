"""Tests for semantic.py — sentence-level RAG matching, with a stubbed embedder."""
import json
import math
import os

import semantic


def _write_fake_index(tmp_path):
    idx = {"model": "gemini-embedding-001", "dim": 3, "vectors": {
        "Deep Learning": semantic._normalize([1.0, 0.0, 0.0]),
        "SQL": semantic._normalize([0.0, 1.0, 0.0]),
        "Docker": semantic._normalize([0.0, 0.0, 1.0])}}
    p = os.path.join(str(tmp_path), "idx.json")
    with open(p, "w") as f:
        json.dump(idx, f)
    semantic.INDEX_PATH = p
    semantic._load_index.cache_clear()
    return idx


def test_normalize_and_dot():
    u = semantic._normalize([3.0, 4.0])
    assert abs(math.hypot(*u) - 1.0) < 1e-9
    assert abs(semantic._dot([1, 0, 0], [1, 0, 0]) - 1.0) < 1e-9
    assert abs(semantic._dot([1, 0], [0, 1])) < 1e-9


def test_split_sentences_filters_and_caps():
    s = semantic._split_sentences("I built CNN models. I deployed containers; ran clusters")
    assert len(s) >= 2
    assert all(len(x.split()) >= semantic.MIN_WORDS for x in s)


def test_infer_no_index(tmp_path):
    semantic.INDEX_PATH = os.path.join(str(tmp_path), "missing.json")
    semantic._load_index.cache_clear()
    added, meta = semantic.infer_skills("anything here now", [], "KEY")
    assert added == [] and meta["source"] == "no_index"


def test_infer_matches_by_sentence(tmp_path, monkeypatch):
    _write_fake_index(tmp_path)

    def fake_embed_texts(texts, api_key, model=None, output_dim=None, task_type="RETRIEVAL_QUERY"):
        if not api_key:
            return None, None, "no_key"
        # every sentence points mostly along the "Deep Learning" axis
        return [semantic._normalize([0.9, 0.4, 0.0]) for _ in texts], model, None

    monkeypatch.setattr(semantic, "embed_texts", fake_embed_texts)
    added, meta = semantic.infer_skills(
        "I trained deep neural networks. I did more work here.", ["Python"], "KEY", threshold=0.5)
    assert "Deep Learning" in added
    assert "Docker" not in added
    assert meta["backend"] == "bruteforce"
    assert meta["model"] == "gemini-embedding-001"    # pinned from index


def test_infer_no_key(tmp_path):
    _write_fake_index(tmp_path)
    added, meta = semantic.infer_skills("some real sentence text", [], "", threshold=0.5)
    assert added == [] and meta["source"] == "error"


def test_infer_excludes_already_found(tmp_path, monkeypatch):
    _write_fake_index(tmp_path)
    monkeypatch.setattr(
        semantic, "embed_texts",
        lambda texts, api_key, model=None, output_dim=None, task_type="RETRIEVAL_QUERY":
        ([semantic._normalize([0.9, 0.4, 0.0]) for _ in texts], model, None) if api_key
        else (None, None, "no_key"))
    added, _ = semantic.infer_skills(
        "deep learning sentence here", ["Deep Learning"], "KEY", threshold=0.5)
    assert "Deep Learning" not in added


def test_bruteforce_scores_direct():
    idx = {"vectors": {"A": semantic._normalize([1.0, 0.0]),
                       "B": semantic._normalize([0.0, 1.0])}}
    scores = semantic._bruteforce_scores([semantic._normalize([1.0, 0.1])], idx, set())
    assert scores["A"] > scores["B"]
