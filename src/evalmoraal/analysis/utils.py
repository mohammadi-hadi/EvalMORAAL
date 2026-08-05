"""
Utility functions for EvalMORAAL analysis.

Provides functions for extracting and processing model outputs.
"""

import re
from typing import Any, Dict, Optional


def normalize_score(score: Any, scale: str = "auto") -> Optional[float]:
    """
    Normalize a score to the [-1, 1] range.

    Args:
        score: Input score (int, float, or string)
        scale: Scale type ('1-7', '1-10', '-1-1', or 'auto')

    Returns:
        Normalized score in [-1, 1] range, or None if invalid
    """
    if score is None:
        return None

    # Handle string scores
    if isinstance(score, str):
        score_lower = score.lower().strip()
        if score_lower in ["unacceptable", "morally unacceptable", "never justifiable"]:
            return -1.0
        elif score_lower in ["acceptable", "morally acceptable", "always justifiable"]:
            return 1.0
        elif score_lower in ["unknown", "neutral", "not a moral issue"]:
            return 0.0
        try:
            score = float(score)
        except ValueError:
            return None

    if not isinstance(score, (int, float)):
        return None

    # Auto-detect scale
    if scale == "auto":
        if -1 <= score <= 1:
            return float(score)
        elif 1 <= score <= 7:
            scale = "1-7"
        elif 1 <= score <= 10:
            scale = "1-10"
        else:
            return None

    # Apply scale normalization
    if scale == "1-7":
        return (score - 4) / 3
    elif scale == "1-10":
        return (score - 5.5) / 4.5
    elif scale == "-1-1":
        return float(score)
    else:
        return None


def extract_cot_reasoning(response: str) -> Dict[str, str]:
    """
    Extract Chain-of-Thought reasoning steps from model response.

    Args:
        response: Full model response text

    Returns:
        Dictionary with step1, step2, step3, and score fields
    """
    reasoning = {"step1": "", "step2": "", "step3": "", "score": None}

    if not response:
        return reasoning

    # Pattern for step extraction
    step_patterns = [
        (r"STEP\s*1[:\s]*(.+?)(?=STEP\s*2|$)", "step1"),
        (r"STEP\s*2[:\s]*(.+?)(?=STEP\s*3|$)", "step2"),
        (r"STEP\s*3[:\s]*(.+?)(?=SCORE|$)", "step3"),
    ]

    for pattern, key in step_patterns:
        match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
        if match:
            reasoning[key] = match.group(1).strip()

    # Extract score
    score_patterns = [
        r"SCORE\s*=\s*(-?[\d.]+)",
        r"Final\s*Score[:\s]*(-?[\d.]+)",
        r"Score[:\s]*(-?[\d.]+)",
    ]

    for pattern in score_patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            try:
                reasoning["score"] = float(match.group(1))
                break
            except ValueError:
                continue

    return reasoning


def extract_country_from_result(result: Dict) -> Optional[str]:
    """
    Extract country name from result dictionary.

    Args:
        result: Result dictionary

    Returns:
        Country name or None
    """
    country_fields = ["country", "Country", "country_name", "culture"]

    for field in country_fields:
        if field in result and result[field]:
            return str(result[field])

    return None


def extract_topic_from_result(result: Dict) -> Optional[str]:
    """
    Extract topic/question from result dictionary.

    Args:
        result: Result dictionary

    Returns:
        Topic name or None
    """
    topic_fields = ["topic", "Topic", "question", "moral_topic", "item"]

    for field in topic_fields:
        if field in result and result[field]:
            return str(result[field])

    return None


def format_score_for_display(score: float, precision: int = 3) -> str:
    """
    Format a score for display with appropriate precision.

    Args:
        score: Score value
        precision: Number of decimal places

    Returns:
        Formatted score string
    """
    if score is None:
        return "N/A"
    return f"{score:.{precision}f}"


def parse_model_name(full_name: str) -> Dict[str, str]:
    """
    Parse model name into components.

    Args:
        full_name: Full model name (e.g., 'meta-llama/Llama-3.3-70B-Instruct')

    Returns:
        Dictionary with 'provider', 'model', 'variant' fields
    """
    result = {"provider": "", "model": full_name, "variant": ""}

    # Check for provider prefix
    if "/" in full_name:
        parts = full_name.split("/", 1)
        result["provider"] = parts[0]
        result["model"] = parts[1]

    # Check for common variants
    model_lower = result["model"].lower()
    if "-instruct" in model_lower:
        result["variant"] = "instruct"
    elif "-chat" in model_lower:
        result["variant"] = "chat"
    elif "-base" in model_lower:
        result["variant"] = "base"

    return result


def get_model_short_name(model_name: str) -> str:
    """
    Get shortened version of model name for display.

    Args:
        model_name: Full model name

    Returns:
        Shortened name suitable for plots/tables
    """
    # Common patterns to simplify
    replacements = {
        "meta-llama/": "",
        "google/": "",
        "openai/": "",
        "anthropic/": "",
        "microsoft/": "",
        "Meta-Llama-": "Llama-",
        "-Instruct": "-I",
        "-instruct": "-i",
    }

    short_name = model_name
    for old, new in replacements.items():
        short_name = short_name.replace(old, new)

    # Truncate if still too long
    if len(short_name) > 25:
        short_name = short_name[:22] + "..."

    return short_name
