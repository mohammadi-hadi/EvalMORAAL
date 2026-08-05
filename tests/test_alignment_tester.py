"""Tests for evalmoraal.core.moral_alignment_tester (no API calls)."""

import json

import pandas as pd

from evalmoraal.core import MoralAlignmentTester


def make_tester(tmp_path):
    return MoralAlignmentTester(
        sample_size=5,
        output_dir=str(tmp_path / "out"),
        data_dir=str(tmp_path),
    )


def test_extract_reasoning_steps(tmp_path):
    tester = make_tester(tmp_path)
    response = (
        "STEP 1: Norms are progressive.\n"
        "More detail here.\n"
        "STEP 2: Reasoning about acceptance.\n"
        "STEP 3: Conclusion.\n"
        "SCORE = 0.8"
    )
    steps = tester._extract_reasoning_steps(response)
    assert len(steps) == 3
    assert "More detail here." in steps[0]


def test_calculate_summary_stats(tmp_path):
    tester = make_tester(tmp_path)
    scores = pd.DataFrame([
        {"method": "direct", "country": "NL", "topic": "Divorce",
         "model_score": 0.8, "ground_truth": 0.7},
        {"method": "direct", "country": "US", "topic": "Divorce",
         "model_score": -0.5, "ground_truth": -0.4},
        {"method": "logprob", "country": "NL", "topic": "Divorce",
         "model_score": 0.6, "ground_truth": 0.7},
        {"method": "logprob", "country": "US", "topic": "Divorce",
         "model_score": -0.3, "ground_truth": -0.4},
    ])

    summary = tester._calculate_summary_stats(scores)
    assert summary["n_samples"] == 4
    assert summary["pearson_correlation"] > 0.9
    assert "direct_correlation" in summary
    assert "logprob_correlation" in summary
    assert tester._calculate_summary_stats(pd.DataFrame()) == {}


def _model_results():
    def entry(model_score, country="Netherlands", topic="Divorce"):
        return {
            "method": "direct",
            "country": country,
            "topic": topic,
            "model_score": model_score,
            "reasoning": "because",
        }

    return {
        "model-a": {"scores": [entry(0.9), entry(0.5, country="Japan")]},
        "model-b": {"scores": [entry(-0.2), entry(0.4, country="Japan")]},
    }


def test_detect_conflicts(tmp_path):
    tester = make_tester(tmp_path)
    conflicts = tester.detect_conflicts(_model_results())

    # Netherlands differs by 1.1 (> 0.4); Japan differs by 0.1 (no conflict)
    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict["country"] == "Netherlands"
    assert conflict["difference"] == 0.9 - (-0.2)
    assert {conflict["model1"], conflict["model2"]} == {"model-a", "model-b"}


def test_save_conflicts_for_review(tmp_path):
    tester = make_tester(tmp_path)
    conflicts = tester.detect_conflicts(_model_results())
    tester.save_conflicts_for_review(conflicts)

    json_path = tester.output_dir / "conflicts_for_review.json"
    csv_path = tester.output_dir / "conflicts_for_review.csv"
    assert json_path.exists()
    assert csv_path.exists()

    saved = json.loads(json_path.read_text())
    assert saved["metadata"]["n_conflicts"] == 1
    assert saved["metadata"]["threshold"] == 0.4
