"""Tests for evalmoraal.analysis.utils."""

from evalmoraal.analysis import (
    extract_cot_reasoning,
    extract_country_from_result,
    extract_topic_from_result,
    normalize_score,
)
from evalmoraal.analysis.utils import (
    format_score_for_display,
    get_model_short_name,
    parse_model_name,
)


class TestNormalizeScore:
    def test_already_normalized(self):
        assert normalize_score(0.5) == 0.5
        assert normalize_score(-1) == -1.0
        assert normalize_score(1) == 1.0

    def test_1_to_10_scale(self):
        assert normalize_score(10) == 1.0
        assert normalize_score(5.5, scale="1-10") == 0.0

    def test_1_to_7_scale(self):
        assert normalize_score(7) == 1.0
        assert normalize_score(4, scale="1-7") == 0.0

    def test_string_labels(self):
        assert normalize_score("never justifiable") == -1.0
        assert normalize_score("acceptable") == 1.0
        assert normalize_score("neutral") == 0.0

    def test_numeric_string(self):
        assert normalize_score("0.7") == 0.7

    def test_invalid(self):
        assert normalize_score(None) is None
        assert normalize_score("garbage") is None
        assert normalize_score(99) is None
        assert normalize_score([1]) is None


class TestExtractCotReasoning:
    def test_full_response(self):
        response = (
            "STEP 1: Norms in the Netherlands are progressive.\n"
            "STEP 2: The behavior is widely accepted.\n"
            "STEP 3: Therefore it is acceptable.\n"
            "SCORE = 0.8"
        )
        reasoning = extract_cot_reasoning(response)
        assert "progressive" in reasoning["step1"]
        assert "accepted" in reasoning["step2"]
        assert "acceptable" in reasoning["step3"]
        assert reasoning["score"] == 0.8

    def test_negative_score(self):
        reasoning = extract_cot_reasoning("STEP 1: x\nSCORE = -0.6")
        assert reasoning["score"] == -0.6

    def test_empty_response(self):
        reasoning = extract_cot_reasoning("")
        assert reasoning["score"] is None
        assert reasoning["step1"] == ""


class TestResultFieldExtraction:
    def test_country(self):
        assert extract_country_from_result({"country": "Japan"}) == "Japan"
        assert extract_country_from_result({"culture": "Japan"}) == "Japan"
        assert extract_country_from_result({}) is None

    def test_topic(self):
        assert extract_topic_from_result({"topic": "Divorce"}) == "Divorce"
        assert extract_topic_from_result({"question": "Divorce"}) == "Divorce"
        assert extract_topic_from_result({}) is None


class TestModelNames:
    def test_parse_with_provider(self):
        parsed = parse_model_name("meta-llama/Llama-3.3-70B-Instruct")
        assert parsed["provider"] == "meta-llama"
        assert parsed["model"] == "Llama-3.3-70B-Instruct"
        assert parsed["variant"] == "instruct"

    def test_parse_plain(self):
        parsed = parse_model_name("gpt-4o")
        assert parsed["provider"] == ""
        assert parsed["model"] == "gpt-4o"

    def test_short_name(self):
        assert get_model_short_name("meta-llama/Meta-Llama-3-8B-Instruct") == "Llama-3-8B-I"
        assert len(get_model_short_name("x" * 60)) <= 25


def test_format_score_for_display():
    assert format_score_for_display(0.12345) == "0.123"
    assert format_score_for_display(None) == "N/A"
