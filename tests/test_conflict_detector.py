"""Tests for evalmoraal.analysis.conflict_detector."""

from evalmoraal.analysis import (
    calculate_conflict_statistics,
    calculate_severity,
    detect_conflicts_between_models,
    extract_score,
)
from evalmoraal.analysis.conflict_detector import (
    get_conflict_summary,
    group_conflicts_by_severity,
)


class TestExtractScore:
    def test_normalized_range(self):
        assert extract_score({"score": 0.4}) == 0.4
        assert extract_score({"score": -1}) == -1.0

    def test_1_to_7_scale(self):
        assert extract_score({"score": 5}) == (5 - 4) / 3

    def test_1_to_10_scale(self):
        assert extract_score({"score": 8}) == (8 - 5.5) / 4.5

    def test_field_priority(self):
        assert extract_score({"logprob_score": 0.1, "score": 0.9}) == 0.1

    def test_missing(self):
        assert extract_score({}) is None
        assert extract_score({"score": "text"}) is None


class TestCalculateSeverity:
    def test_levels(self):
        assert calculate_severity(1.2) == "critical"
        assert calculate_severity(1.0) == "critical"
        assert calculate_severity(0.7) == "high"
        assert calculate_severity(0.5) == "medium"
        assert calculate_severity(0.3) == "low"
        assert calculate_severity(0.29) == "negligible"

    def test_sign_ignored(self):
        assert calculate_severity(-0.8) == "high"


def _model_data(scores):
    return {
        "results": [
            {"country": c, "topic": t, "score": s, "reasoning": f"{c}-{t}"}
            for c, t, s in scores
        ]
    }


class TestDetectConflicts:
    def test_finds_conflict(self):
        m1 = _model_data([("Japan", "Divorce", 0.9), ("Brazil", "Divorce", 0.2)])
        m2 = _model_data([("Japan", "Divorce", -0.4), ("Brazil", "Divorce", 0.1)])

        conflicts = detect_conflicts_between_models("m1", m1, "m2", m2)

        assert len(conflicts) == 1
        conflict = conflicts[0]
        assert conflict["country"] == "Japan"
        assert conflict["topic"] == "Divorce"
        assert conflict["severity"] == "critical"
        assert conflict["score_diff"] == 0.9 - (-0.4)

    def test_min_severity_filter(self):
        m1 = _model_data([("Japan", "Divorce", 0.5)])
        m2 = _model_data([("Japan", "Divorce", 0.1)])  # diff 0.4 -> low

        assert detect_conflicts_between_models("m1", m1, "m2", m2, min_severity="medium") == []
        assert len(detect_conflicts_between_models("m1", m1, "m2", m2, min_severity="low")) == 1

    def test_conflict_id_deterministic(self):
        m1 = _model_data([("Japan", "Divorce", 0.9)])
        m2 = _model_data([("Japan", "Divorce", -0.9)])

        first = detect_conflicts_between_models("m1", m1, "m2", m2)[0]["conflict_id"]
        second = detect_conflicts_between_models("m1", m1, "m2", m2)[0]["conflict_id"]
        assert first == second
        assert len(first) == 16


class TestConflictStatistics:
    def test_empty(self):
        stats = calculate_conflict_statistics([])
        assert stats["total_conflicts"] == 0
        assert stats["severity_breakdown"] == {}

    def test_populated(self):
        m1 = _model_data([("Japan", "Divorce", 0.9), ("Brazil", "Abortion", 0.8)])
        m2 = _model_data([("Japan", "Divorce", -0.4), ("Brazil", "Abortion", 0.2)])
        conflicts = detect_conflicts_between_models("m1", m1, "m2", m2)

        stats = calculate_conflict_statistics(conflicts)
        assert stats["total_conflicts"] == 2
        assert stats["model_conflict_counts"] == {"m1": 2, "m2": 2}
        assert stats["max_score_difference"] == 1.3


def test_group_by_severity():
    conflicts = [{"severity": "high"}, {"severity": "low"}, {"severity": "high"}]
    grouped = group_conflicts_by_severity(conflicts)
    assert len(grouped["high"]) == 2
    assert len(grouped["low"]) == 1


def test_conflict_summary_sorted():
    m1 = _model_data([("Japan", "Divorce", 0.9), ("Brazil", "Abortion", 0.5)])
    m2 = _model_data([("Japan", "Divorce", -0.9), ("Brazil", "Abortion", 0.1)])
    conflicts = detect_conflicts_between_models("m1", m1, "m2", m2)

    summary = get_conflict_summary(conflicts)
    assert list(summary["abs_diff"]) == sorted(summary["abs_diff"], reverse=True)
    assert get_conflict_summary([]).empty
