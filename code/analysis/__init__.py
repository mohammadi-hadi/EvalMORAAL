"""
Analysis utilities for EvalMORAAL evaluation framework.

This module provides utilities for:
- Conflict detection between model predictions
- Visualization of evaluation results
- Score extraction and processing
"""

from .conflict_detector import (
    calculate_conflict_statistics,
    calculate_severity,
    detect_conflicts_between_models,
    extract_score,
)
from .utils import (
    extract_cot_reasoning,
    extract_country_from_result,
    extract_topic_from_result,
    normalize_score,
)
from .visualization import (
    plot_country_heatmap,
    plot_error_distribution,
    plot_model_comparison,
    plot_score_distributions,
    plot_topic_heatmap,
)

__version__ = "1.0.0"
__all__ = [
    # Conflict detection
    "extract_score",
    "calculate_severity",
    "detect_conflicts_between_models",
    "calculate_conflict_statistics",
    # Utils
    "normalize_score",
    "extract_cot_reasoning",
    "extract_country_from_result",
    "extract_topic_from_result",
    # Visualization
    "plot_country_heatmap",
    "plot_error_distribution",
    "plot_model_comparison",
    "plot_score_distributions",
    "plot_topic_heatmap",
]
