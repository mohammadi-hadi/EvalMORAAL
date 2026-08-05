"""Tests for evalmoraal.core.validation_suite (synthetic data only)."""

import numpy as np

from evalmoraal.core import ValidationSuite


def _make_results(offset=0.0, seed=0):
    rng = np.random.default_rng(seed)
    scores = []
    countries = ["Netherlands", "United States", "Japan", "Brazil"]
    topics = ["Divorce", "Abortion", "Euthanasia", "Suicide", "Homosexuality"]
    for country in countries:
        for topic in topics:
            truth = float(np.clip(rng.uniform(-0.9, 0.9), -1, 1))
            noise = float(rng.normal(0, 0.05))
            scores.append({
                "method": "direct",
                "country": country,
                "topic": topic,
                "model_score": float(np.clip(truth + noise + offset, -1, 1)),
                "ground_truth": truth,
            })
    return {"scores": scores}


def make_suite(tmp_path):
    return ValidationSuite(output_dir=str(tmp_path))


def test_validate_model_results(tmp_path):
    suite = make_suite(tmp_path)
    validation = suite.validate_model_results(_make_results(), "test-model")

    assert validation["model"] == "test-model"
    consistency = validation["internal_consistency"]
    assert bool(consistency["scores_in_range"])
    assert consistency["out_of_range_count"] == 0

    validity = validation["statistical_validity"]
    assert validity["correlations"]["pearson"]["r"] > 0.9
    assert validity["errors"]["mae"] < 0.2

    quality = validation["data_quality"]
    assert quality["total_samples"] == 20


def test_cross_model_agreement(tmp_path):
    suite = make_suite(tmp_path)
    all_results = {
        "model-a": _make_results(seed=1),
        "model-b": _make_results(offset=0.02, seed=1),
    }

    agreement = suite.validate_cross_model_agreement(all_results)
    pair = agreement["pairwise_correlations"]["model-a_vs_model-b"]
    assert pair["correlation"] > 0.9
    assert pair["n_samples"] == 20
    assert "consensus_metrics" in agreement


def test_statistical_tests_between_models(tmp_path):
    suite = make_suite(tmp_path)
    tests = suite.perform_statistical_tests(
        _make_results(seed=2),
        _make_results(offset=0.3, seed=2),
    )

    assert "paired_t_test" in tests
    assert tests["paired_t_test"]["better_model"] == "model1"
    assert "effect_size" in tests


def test_interpret_cohens_d(tmp_path):
    suite = make_suite(tmp_path)
    assert suite._interpret_cohens_d(0.1) == "negligible"
    assert suite._interpret_cohens_d(0.3) == "small"
    assert suite._interpret_cohens_d(-0.6) == "medium"
    assert suite._interpret_cohens_d(1.2) == "large"


def test_validation_report_and_save(tmp_path):
    suite = make_suite(tmp_path)
    validation = suite.validate_model_results(_make_results(), "test-model")
    all_validations = {"model_validations": {"test-model": validation}}

    report = suite.generate_validation_report(all_validations)
    assert "# Validation Report" in report
    assert "test-model" in report

    suite.save_validation_results(all_validations)
    assert list(tmp_path.glob("validation_results_*.json"))
    assert list(tmp_path.glob("validation_report_*.md"))
