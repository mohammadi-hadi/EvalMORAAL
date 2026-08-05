"""Smoke tests for evalmoraal.analysis.visualization plotting helpers."""

import pandas as pd

from evalmoraal.analysis import (
    plot_country_heatmap,
    plot_model_comparison,
    plot_score_distributions,
    plot_topic_heatmap,
)


def _results_df():
    rows = []
    for model in ["model-a", "model-b"]:
        for country in ["Netherlands", "Japan", "Brazil"]:
            for topic in ["Divorce", "Abortion"]:
                rows.append({
                    "model": model,
                    "country": country,
                    "topic": topic,
                    "correlation": 0.5 if model == "model-a" else 0.7,
                    "score": 0.2,
                })
    return pd.DataFrame(rows)


def test_country_heatmap(tmp_path):
    path = tmp_path / "country.png"
    plot_country_heatmap(_results_df(), value_col="correlation",
                         title="by country", save_path=str(path))
    assert path.exists()


def test_topic_heatmap(tmp_path):
    path = tmp_path / "topic.png"
    plot_topic_heatmap(_results_df(), value_col="correlation",
                       title="by topic", save_path=str(path))
    assert path.exists()


def test_model_comparison(tmp_path):
    scores = pd.DataFrame({
        "model": ["model-a", "model-b"],
        "logprob_correlation": [0.4, 0.6],
        "direct_correlation": [0.5, 0.7],
    })
    path = tmp_path / "models.png"
    plot_model_comparison(scores, x_col="logprob_correlation",
                          y_col="direct_correlation",
                          title="method comparison", save_path=str(path))
    assert path.exists()


def test_score_distributions(tmp_path):
    path = tmp_path / "dist.png"
    plot_score_distributions(_results_df(), score_cols=["score"],
                             group_col="model", title="distributions",
                             save_path=str(path))
    assert path.exists()
