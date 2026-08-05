"""
Core evaluation pipeline for EvalMORAAL.

Provides:
- WVS survey data processing (WVSProcessor)
- Dual scoring: log-probability and chain-of-thought (MoralAlignmentTester)
- LLM-as-judge peer review (ModelJudge)
- Statistical validation (ValidationSuite)
- The full pipeline that ties them together (FullValidationPipeline)
"""

from .model_judge import CritiqueResult, ModelJudge, ReasoningTrace
from .moral_alignment_tester import MoralAlignmentTester
from .pipeline import FullValidationPipeline
from .validation_suite import ValidationSuite
from .wvs_processor import WVSProcessor

__all__ = [
    "CritiqueResult",
    "FullValidationPipeline",
    "ModelJudge",
    "MoralAlignmentTester",
    "ReasoningTrace",
    "ValidationSuite",
    "WVSProcessor",
]
