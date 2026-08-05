"""
Cross-evaluation and conflict resolution for EvalMORAAL.

Provides:
- Peer evaluation between models (CrossEvaluator)
- Conflict detection and resolution strategies (ConflictResolver)

The streamlit dashboards (human_dashboard, human_judge_dashboard) are
apps, not library modules; launch them with `evalmoraal dashboard`.
"""

from .conflict_resolver import Conflict, ConflictResolver
from .cross_evaluation import CrossEvaluator, DisagreementCase, EvaluationPair

__all__ = [
    "Conflict",
    "ConflictResolver",
    "CrossEvaluator",
    "DisagreementCase",
    "EvaluationPair",
]
