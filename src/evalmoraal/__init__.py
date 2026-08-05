"""
EvalMORAAL: moral alignment evaluation for large language models.

Combines chain-of-thought elicitation with LLM-as-judge peer review to
evaluate how well LLMs reproduce human moral judgments from the World
Values Survey and PEW Global Attitudes Survey.

Subpackages
-----------
- ``evalmoraal.analysis``: conflict detection, score utilities, plotting
- ``evalmoraal.core``: WVS processing, dual scoring, peer review, validation
- ``evalmoraal.evaluation``: cross-evaluation, conflict resolution, dashboards
- ``evalmoraal.visualization``: figure and paper output generators

Paper: https://aclanthology.org/2026.starsem-conference.34/
"""

from importlib import import_module

__version__ = "1.1.0"

_SUBMODULES = ("analysis", "core", "evaluation", "visualization", "env")


def __getattr__(name):
    # Lazy submodule access so `import evalmoraal` stays lightweight.
    if name in _SUBMODULES:
        module = import_module(f".{name}", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(_SUBMODULES))
