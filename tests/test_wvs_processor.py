"""Tests for evalmoraal.core.wvs_processor with a synthetic WVS file."""

import pandas as pd
import pytest

from evalmoraal.core import WVSProcessor


@pytest.fixture
def wvs_dir(tmp_path):
    rows = []
    for code, scores in [(528, [10, 9, 8]), (840, [2, 3, 1])]:
        for score in scores:
            rows.append({"B_COUNTRY": code, "Q182": score, "Q184": score, "Q183": -1})
    pd.DataFrame(rows).to_csv(tmp_path / "WVS_Moral.csv", index=False)
    return tmp_path


@pytest.fixture
def processor(wvs_dir):
    return WVSProcessor(data_dir=wvs_dir)


def test_load_data_cleans_special_codes(processor):
    data = processor.load_data()
    assert len(data) == 6
    # -1 codes must become NaN
    assert data["Q183"].isna().all()


def test_process_moral_scores_normalization(processor):
    processed = processor.process_moral_scores()

    # Q183 was invalid everywhere; only Q182 and Q184 remain (6 rows each)
    assert set(processed["topic_code"].unique()) == {"Q182", "Q184"}
    assert len(processed) == 12

    # WVS scale 1..10 maps to [-1, 1]
    ten = processed[processed["raw_score"] == 10]["normalized_score"].iloc[0]
    one = processed[processed["raw_score"] == 1]["normalized_score"].iloc[0]
    assert ten == 1.0
    assert one == -1.0

    # Country and region mapping
    assert set(processed["country"].unique()) == {"Netherlands", "United States"}
    assert set(processed["region"].unique()) == {"Europe", "North America"}


def test_country_and_region_fallbacks(processor):
    assert processor.get_country_name(999) == "Country_999"
    assert processor.get_region(999) == "Other"


def test_country_topic_means(processor):
    means = processor.get_country_topic_means()
    nl_row = means[(means["country"] == "Netherlands") & (means["topic_code"] == "Q182")]
    assert nl_row["n_samples"].iloc[0] == 3
    assert nl_row["raw_score"].iloc[0] == pytest.approx(9.0)


def test_create_evaluation_dataset_stratified(processor):
    eval_data = processor.create_evaluation_dataset(n_samples=4, stratified=True)
    assert len(eval_data) <= 4
    assert eval_data["country"].nunique() == 2


def test_create_prompts(processor):
    eval_data = processor.create_evaluation_dataset(n_samples=2, stratified=False)
    prompts = processor.create_prompts_for_evaluation(eval_data)

    # One chain-of-thought and one direct prompt per sample
    assert len(prompts) == 2 * len(eval_data)
    types = {p["type"] for p in prompts}
    assert types == {"chain_of_thought", "direct"}
    assert all(p["country"] in p["prompt"] for p in prompts)


def test_human_baseline(processor):
    baseline = processor.calculate_human_baseline()
    assert -1 <= baseline["overall_mean"] <= 1
    assert "Homosexuality" in baseline["by_topic"]
    assert baseline["by_country"]["Netherlands"]["n"] == 6


def test_save_processed_data(processor, tmp_path):
    out = tmp_path / "processed"
    processor.process_moral_scores()
    processor.save_processed_data(output_dir=out)

    assert (out / "wvs_processed.csv").exists()
    assert (out / "country_topic_means.csv").exists()
    assert (out / "human_baseline.json").exists()
