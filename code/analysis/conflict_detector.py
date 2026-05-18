"""
Conflict detection utilities for model evaluation results.

Identifies and categorizes conflicts between model predictions on moral judgment tasks.
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd


def extract_score(result: Dict) -> Optional[float]:
    """
    Extract score from result item.

    Args:
        result: Dictionary containing model result with score field

    Returns:
        Normalized score in [-1, 1] range, or None if extraction fails
    """
    # Try different score field names
    score_fields = ["logprob_score", "direct_score", "score", "judgment", "moral_score"]

    for field in score_fields:
        if field in result:
            score = result[field]
            # Normalize score to [-1, 1] range if needed
            if isinstance(score, (int, float)):
                if -1 <= score <= 1:
                    return float(score)
                elif 1 <= score <= 7:
                    # Convert 1-7 scale to -1 to 1
                    return (score - 4) / 3
                elif 1 <= score <= 10:
                    # Convert 1-10 scale to -1 to 1
                    return (score - 5.5) / 4.5

    return None


def calculate_severity(score_diff: float) -> str:
    """
    Categorize conflict severity based on score difference.

    Args:
        score_diff: Difference between two model scores

    Returns:
        Severity level: 'critical', 'high', 'medium', 'low', or 'negligible'
    """
    abs_diff = abs(score_diff)

    if abs_diff >= 1.0:
        return "critical"
    elif abs_diff >= 0.7:
        return "high"
    elif abs_diff >= 0.5:
        return "medium"
    elif abs_diff >= 0.3:
        return "low"
    else:
        return "negligible"


def detect_conflicts_between_models(
    model1_name: str,
    model1_data: Dict,
    model2_name: str,
    model2_data: Dict,
    min_severity: str = "low",
) -> List[Dict]:
    """
    Detect conflicts between two models on shared evaluation items.

    Args:
        model1_name: Name of first model
        model1_data: Results dictionary for first model
        model2_name: Name of second model
        model2_data: Results dictionary for second model
        min_severity: Minimum severity level to report (default: 'low')

    Returns:
        List of conflict dictionaries with details about each disagreement
    """
    severity_order = {"negligible": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    min_level = severity_order.get(min_severity, 1)

    conflicts = []

    # Extract results
    results1 = model1_data.get("results", [])
    results2 = model2_data.get("results", [])

    # Create lookup dictionaries
    lookup1 = {}
    for r in results1:
        key = f"{r.get('country')}_{r.get('topic')}"
        score = extract_score(r)
        if score is not None:
            lookup1[key] = (score, r.get("reasoning", ""))

    lookup2 = {}
    for r in results2:
        key = f"{r.get('country')}_{r.get('topic')}"
        score = extract_score(r)
        if score is not None:
            lookup2[key] = (score, r.get("reasoning", ""))

    # Find conflicts
    common_keys = set(lookup1.keys()) & set(lookup2.keys())

    for key in common_keys:
        score1, reasoning1 = lookup1[key]
        score2, reasoning2 = lookup2[key]

        score_diff = score1 - score2
        severity = calculate_severity(score_diff)

        # Only record conflicts above minimum severity
        if severity_order.get(severity, 0) >= min_level:
            country, topic = key.split("_", 1)

            conflict_id = hashlib.md5(
                f"{model1_name}_{model2_name}_{key}".encode()
            ).hexdigest()[:16]

            conflict = {
                "conflict_id": conflict_id,
                "model1": model1_name,
                "model2": model2_name,
                "country": country,
                "topic": topic,
                "score1": score1,
                "score2": score2,
                "score_diff": score_diff,
                "severity": severity,
                "reasoning1": reasoning1,
                "reasoning2": reasoning2,
                "detection_timestamp": datetime.now().isoformat(),
            }

            conflicts.append(conflict)

    return conflicts


def calculate_conflict_statistics(conflicts: List[Dict]) -> Dict:
    """
    Calculate detailed statistics about detected conflicts.

    Args:
        conflicts: List of conflict dictionaries

    Returns:
        Dictionary containing conflict statistics
    """
    if not conflicts:
        return {
            "total_conflicts": 0,
            "mean_score_difference": 0.0,
            "max_score_difference": 0.0,
            "severity_breakdown": {},
            "most_conflicted_countries": {},
            "most_conflicted_topics": {},
            "model_conflict_counts": {},
        }

    df = pd.DataFrame(conflicts)

    # Severity breakdown
    severity_counts = df["severity"].value_counts().to_dict()

    # Most conflicted countries and topics
    country_counts = df["country"].value_counts().head(10).to_dict()
    topic_counts = df["topic"].value_counts().head(10).to_dict()

    # Count conflicts per model
    model_counts = {}
    for _, row in df.iterrows():
        for model in [row["model1"], row["model2"]]:
            if model not in model_counts:
                model_counts[model] = 0
            model_counts[model] += 1

    stats = {
        "total_conflicts": len(conflicts),
        "mean_score_difference": float(df["score_diff"].abs().mean()),
        "max_score_difference": float(df["score_diff"].abs().max()),
        "severity_breakdown": severity_counts,
        "most_conflicted_countries": country_counts,
        "most_conflicted_topics": topic_counts,
        "model_conflict_counts": model_counts,
    }

    return stats


def group_conflicts_by_severity(conflicts: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group conflicts by severity level.

    Args:
        conflicts: List of conflict dictionaries

    Returns:
        Dictionary mapping severity levels to lists of conflicts
    """
    by_severity = {}
    for conflict in conflicts:
        severity = conflict["severity"]
        if severity not in by_severity:
            by_severity[severity] = []
        by_severity[severity].append(conflict)

    return by_severity


def get_conflict_summary(conflicts: List[Dict]) -> pd.DataFrame:
    """
    Create a summary DataFrame of conflicts for analysis.

    Args:
        conflicts: List of conflict dictionaries

    Returns:
        Summary DataFrame with key conflict information
    """
    if not conflicts:
        return pd.DataFrame()

    df = pd.DataFrame(conflicts)

    # Select key columns for summary
    summary_cols = [
        "conflict_id",
        "model1",
        "model2",
        "country",
        "topic",
        "score1",
        "score2",
        "score_diff",
        "severity",
    ]

    summary = df[summary_cols].copy()
    summary["abs_diff"] = summary["score_diff"].abs()
    summary = summary.sort_values("abs_diff", ascending=False)

    return summary
