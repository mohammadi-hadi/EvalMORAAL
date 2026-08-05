"""Package-level checks: version, lazy submodules, import safety."""

import evalmoraal


def test_version():
    assert isinstance(evalmoraal.__version__, str)
    assert evalmoraal.__version__.count(".") == 2


def test_lazy_submodule_access():
    assert hasattr(evalmoraal.analysis, "detect_conflicts_between_models")
    assert hasattr(evalmoraal.env, "get_env_loader")


def test_unknown_attribute():
    try:
        evalmoraal.does_not_exist
    except AttributeError:
        pass
    else:
        raise AssertionError("expected AttributeError")


def test_core_imports_without_api_extras():
    # Core must be importable even when openai/anthropic/google SDKs are absent
    from evalmoraal.core import (
        CritiqueResult,
        FullValidationPipeline,
        ModelJudge,
        MoralAlignmentTester,
        ReasoningTrace,
        ValidationSuite,
        WVSProcessor,
    )

    for obj in (CritiqueResult, FullValidationPipeline, ModelJudge,
                MoralAlignmentTester, ReasoningTrace, ValidationSuite, WVSProcessor):
        assert obj is not None


def test_evaluation_imports():
    from evalmoraal.evaluation import ConflictResolver, CrossEvaluator

    assert ConflictResolver is not None
    assert CrossEvaluator is not None


def test_visualization_imports():
    from evalmoraal.visualization import (
        MoralVisualizationEngine,
        OutputGenerator,
        PaperOutputGenerator,
        VisualizationEngine,
    )

    for obj in (MoralVisualizationEngine, OutputGenerator,
                PaperOutputGenerator, VisualizationEngine):
        assert obj is not None
