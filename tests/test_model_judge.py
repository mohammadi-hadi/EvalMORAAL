"""Tests for evalmoraal.core.model_judge (no API calls)."""

import pandas as pd

from evalmoraal.core import CritiqueResult, ModelJudge, ReasoningTrace


def make_judge():
    return ModelJudge(api_keys={})


def test_dataclasses():
    trace = ReasoningTrace(
        model="gpt-4o",
        country="Netherlands",
        topic="Divorce",
        reasoning_steps=["step 1", "step 2", "step 3"],
        final_score=0.5,
        method="direct",
        raw_response="...",
    )
    assert trace.timestamp  # auto-filled

    critique = CritiqueResult(
        judge_model="gpt-4o",
        target_model="gpt-3.5-turbo",
        country="Netherlands",
        topic="Divorce",
        verdict="VALID",
        justification="ok",
        confidence=0.8,
    )
    assert critique.verdict == "VALID"


def test_init_without_keys():
    judge = make_judge()
    assert judge.clients == {}


class TestParseCritiqueResponse:
    def test_valid(self):
        verdict, justification, confidence = make_judge()._parse_critique_response(
            "VERDICT: VALID\nJUSTIFICATION: Reasoning is culturally accurate."
        )
        assert verdict == "VALID"
        assert justification == "Reasoning is culturally accurate."
        assert confidence == 0.8

    def test_invalid(self):
        verdict, justification, _ = make_judge()._parse_critique_response(
            "VERDICT: INVALID\nJUSTIFICATION: Misrepresents local norms."
        )
        assert verdict == "INVALID"
        assert "Misrepresents" in justification

    def test_malformed_defaults_to_invalid(self):
        verdict, _, confidence = make_judge()._parse_critique_response("no idea")
        assert verdict == "INVALID"
        assert confidence == 0.5

    def test_justification_fallback(self):
        verdict, justification, _ = make_judge()._parse_critique_response(
            "VERDICT: VALID\nThe reasoning holds up."
        )
        assert verdict == "VALID"
        assert "reasoning holds up" in justification


def _critique_df():
    rows = [
        ("j1", "m1", "NL", "Divorce", "VALID"),
        ("j2", "m1", "NL", "Divorce", "VALID"),
        ("j1", "m2", "NL", "Abortion", "VALID"),
        ("j2", "m2", "NL", "Abortion", "INVALID"),
    ]
    return pd.DataFrame(
        rows, columns=["judge_model", "target_model", "country", "topic", "verdict"]
    )


def test_peer_agreement_rates():
    rates = make_judge().calculate_peer_agreement_rates(_critique_df())
    assert rates["m1"] == 1.0
    assert rates["m2"] == 0.5


def test_identify_contentious_cases():
    contentious = make_judge().identify_contentious_cases(_critique_df(), min_disagreement=0.5)
    # Only the Abortion case has a 0.5 valid rate; Divorce is unanimous
    assert len(contentious) == 1
    assert contentious.iloc[0]["topic"] == "Abortion"


def test_save_critique_results(tmp_path):
    judge = make_judge()
    df = _critique_df()
    rates = judge.calculate_peer_agreement_rates(df)
    contentious = judge.identify_contentious_cases(df)

    judge.save_critique_results(df, rates, contentious, output_dir=tmp_path)

    assert (tmp_path / "all_critiques.csv").exists()
    assert (tmp_path / "peer_agreement_rates.csv").exists()
    assert (tmp_path / "critique_summary.json").exists()
