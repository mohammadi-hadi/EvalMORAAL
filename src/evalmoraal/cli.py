"""
Command line interface for EvalMORAAL.

Commands:
    evalmoraal run        Run the full validation pipeline
    evalmoraal dashboard  Launch the human evaluation dashboard (streamlit)
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from . import __version__

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evalmoraal",
        description="EvalMORAAL: moral alignment evaluation for large language models",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser(
        "run",
        help="Run the full validation pipeline (dual scoring, peer review, conflicts)",
    )
    run.add_argument(
        "--models",
        nargs="+",
        default=None,
        help="Models to test (default: pick from configured API keys)",
    )
    run.add_argument(
        "--samples",
        type=int,
        default=10,
        help="Number of samples to test (default: 10)",
    )
    run.add_argument(
        "--data-dir",
        default="sample_data",
        help="Directory with WVS data files (default: sample_data)",
    )
    run.add_argument(
        "--output-dir",
        default="outputs/full_validation",
        help="Directory for pipeline outputs (default: outputs/full_validation)",
    )
    run.add_argument(
        "--skip-peer-review",
        action="store_true",
        help="Skip reciprocal model critique",
    )
    run.add_argument(
        "--skip-human-prep",
        action="store_true",
        help="Skip preparing data for human review",
    )

    dashboard = sub.add_parser(
        "dashboard",
        help="Launch the human evaluation dashboard (requires the 'dashboards' extra)",
    )
    dashboard.add_argument(
        "--judge",
        action="store_true",
        help="Launch the extended human judge dashboard instead",
    )

    return parser


def _run_pipeline(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.INFO)

    from .core.pipeline import FullValidationPipeline

    pipeline = FullValidationPipeline(output_dir=args.output_dir, data_dir=args.data_dir)
    results = pipeline.run_pipeline(
        models=args.models,
        n_samples=args.samples,
        run_peer_review=not args.skip_peer_review,
        save_for_human_review=not args.skip_human_prep,
    )

    if not results:
        logger.error("Validation pipeline produced no results")
        return 1

    logger.info("Validation complete. See the output directory for reports and figures.")
    return 0


def _run_dashboard(args: argparse.Namespace) -> int:
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print(
            "The dashboard needs streamlit. Install it with:\n"
            '    pip install "evalmoraal[dashboards]"',
            file=sys.stderr,
        )
        return 1

    name = "human_judge_dashboard.py" if args.judge else "human_dashboard.py"
    app = Path(__file__).parent / "evaluation" / name
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(app)])


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return _run_pipeline(args)
    if args.command == "dashboard":
        return _run_dashboard(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
