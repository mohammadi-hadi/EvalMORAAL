<div align="center">

# EvalMORAAL Framework for Moral Alignment Evaluation in Large Language Models

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20292113.svg)](https://doi.org/10.5281/zenodo.20292113)
[![arXiv](https://img.shields.io/badge/arXiv-2510.05942-b31b1b.svg)](https://arxiv.org/abs/2510.05942)
[![CI](https://github.com/mohammadi-hadi/EvalMORAAL/actions/workflows/ci.yml/badge.svg)](https://github.com/mohammadi-hadi/EvalMORAAL/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://github.com/mohammadi-hadi/EvalMORAAL)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Chain-of-Thought reasoning + LLM-as-judge peer review for moral alignment evaluation.*

</div>

## Paper

|                  |                                                                          |
| ---------------- | ------------------------------------------------------------------------ |
| **Title**        | EvalMORAAL: Interpretable Chain-of-Thought and LLM-as-Judge Evaluation for Moral Alignment in Large Language Models |
| **Authors**      | Hadi Mohammadi, Anastasia Giachanou, Robert A. Bagheri |
| **Affiliation**  | Utrecht University, The Netherlands |
| **Venue**        | Proceedings of the 15th Joint Conference on Lexical and Computational Semantics (*SEM 2026), ACL 2026, pp. 497–515 |
| **ACL Anthology**| [2026.starsem-conference.34](https://aclanthology.org/2026.starsem-conference.34/) · DOI [10.18653/v1/2026.starsem-conference.34](https://doi.org/10.18653/v1/2026.starsem-conference.34) |
| **arXiv**        | [2510.05942](https://arxiv.org/abs/2510.05942) (preprint) |
| **Code archive** | [10.5281/zenodo.20292113](https://doi.org/10.5281/zenodo.20292113) (this repository, snapshot v1.0-thesis) |

> This repository accompanies **Chapter 7** of the PhD thesis
> *Let Me Explain! Explainable NLP for Understanding Large Language Models* (Hadi Mohammadi, Utrecht University, 2026).

## Abstract

EvalMORAAL is a moral-alignment evaluation framework for large language models that combines chain-of-thought (CoT) elicitation with LLM-as-judge peer review. Evaluating 20 models against the World Values Survey (64 countries) and PEW Global Attitudes Survey (27 topics, 5 repetitions per cell), we find that explicit CoT reasoning consistently improves alignment over implicit log-probability scoring, while peer-review judging by GPT-4o reproduces human preferences more reliably than naive aggregation. A persistent Western / non-Western gap remains across model families and scales.

## Citation

If you use this code or data, please cite **both** the paper and this code archive:

```bibtex
@inproceedings{mohammadi2026evalmoraal,
  title         = {EvalMORAAL: Interpretable Chain-of-Thought and LLM-as-Judge Evaluation for Moral Alignment in Large Language Models},
  author        = {Mohammadi, Hadi and Giachanou, Anastasia and Bagheri, Robert A.},
  editor        = {Mohammad, Saif M. and Ousidhoum, Nedjma},
  booktitle     = {Proceedings of the 15th Joint Conference on Lexical and Computational Semantics (*SEM 2026)},
  month         = jul,
  year          = {2026},
  address       = {San Diego, California, United States},
  publisher     = {Association for Computational Linguistics},
  pages         = {497--515},
  doi           = {10.18653/v1/2026.starsem-conference.34},
  url           = {https://aclanthology.org/2026.starsem-conference.34/}
}

@software{mohammadi_evalmoraal_2026,
  author    = {Mohammadi, Hadi and Giachanou, Anastasia and Bagheri, Robert A.},
  title     = {EvalMORAAL Framework for Moral Alignment Evaluation in Large Language Models},
  year      = {2026},
  publisher = {Zenodo},
  version   = {v1.0-thesis},
  doi       = {10.5281/zenodo.20292113},
  url       = {https://doi.org/10.5281/zenodo.20292113}
}
```

---

## Overview

EvalMORAAL is a comprehensive evaluation framework for assessing moral alignment in Large Language Models across diverse cultural contexts. We evaluate 20 LLMs using data from the World Values Survey (WVS) and PEW Global Attitudes Survey.

## Key Features

- **Dual Elicitation**: Combines log-probability scoring with chain-of-thought reasoning
- **LLM-as-Judge**: Peer review system where models evaluate each other's moral reasoning
- **Cross-Cultural Analysis**: Evaluates performance across 64 countries and 23 moral topics
- **Interpretable Metrics**: Self-consistency (SC), peer-agreement (Am), and human alignment (Hm)

## Framework

<div align="center">
<img src="figures/cover.png" alt="EvalMORAAL Framework" width="800"/>
</div>

### Evaluation Pipeline

1. **Survey Data Processing**: Extract moral judgment data from WVS (2017-2022) and PEW surveys
2. **Dual Scoring**:
   - Log-probability method: Compare probabilities between moral framings
   - Chain-of-thought: 3-step reasoning (norms → reasoning → score)
3. **Peer Review**: Models critique each other's reasoning with VALID/INVALID verdicts
4. **Conflict Detection**: Identify cases where dual scores diverge (>0.4 threshold)
5. **Human Arbitration**: Dashboard-based evaluation for conflict resolution

## Key Findings

| Tier | Models | WVS Correlation | PEW Correlation |
|------|--------|-----------------|-----------------|
| High | Claude-3-Opus, GPT-4o, Gemini-Pro | r ≥ 0.90 | r ≥ 0.85 |
| Mid-High | GPT-4, Mistral-Large, Phi-3 | 0.80 ≤ r < 0.90 | 0.75 ≤ r < 0.85 |
| Mid-Lower | Claude-3-Haiku, o1-mini | 0.70 ≤ r < 0.80 | 0.65 ≤ r < 0.75 |
| Lower | Smaller open models | r < 0.70 | r < 0.65 |

### Regional Performance Gap
- **Western contexts**: r = 0.82
- **Non-Western contexts**: r = 0.61
- **Gap**: 21 percentage points

<div align="center">
<img src="figures/scatter_tiers_WVS.png" alt="Model Performance Tiers" width="600"/>
<br><i>Model performance tiers based on WVS correlation</i>
</div>

## Installation

EvalMORAAL is a regular Python package (Python 3.9+):

```bash
pip install "evalmoraal @ git+https://github.com/mohammadi-hadi/EvalMORAAL.git"
```

Optional extras:

```bash
# API clients for model scoring and peer review (OpenAI, Anthropic, Google)
pip install "evalmoraal[api] @ git+https://github.com/mohammadi-hadi/EvalMORAAL.git"

# Streamlit dashboard for human arbitration
pip install "evalmoraal[dashboards] @ git+https://github.com/mohammadi-hadi/EvalMORAAL.git"
```

Or work from a clone:

```bash
git clone https://github.com/mohammadi-hadi/EvalMORAAL.git
cd EvalMORAAL
pip install -e ".[api,dashboards,dev]"
pytest   # run the test suite
```

Prebuilt wheels are attached to [GitHub Releases](https://github.com/mohammadi-hadi/EvalMORAAL/releases).

## Quick Start

### Conflict Detection

```python
from evalmoraal.analysis import (
    extract_score,
    calculate_severity,
    detect_conflicts_between_models,
    calculate_conflict_statistics,
)

# Detect conflicts between two model outputs
conflicts = detect_conflicts_between_models(
    "GPT-4o", gpt4_results,
    "Claude-3-Opus", claude_results,
    min_severity="medium",
)

# Calculate statistics
stats = calculate_conflict_statistics(conflicts)
print(f"Total conflicts: {stats['total_conflicts']}")
print(f"Severity breakdown: {stats['severity_breakdown']}")
```

### Visualization

```python
from evalmoraal.analysis import plot_country_heatmap, plot_topic_heatmap

# Create country-wise correlation heatmap
plot_country_heatmap(
    data=results_df,
    value_col="correlation",
    title="Model Performance by Country",
    save_path="figures/country_heatmap.png",
)
```

### Working with survey data

```python
from evalmoraal.core import WVSProcessor

processor = WVSProcessor(data_dir="sample_data")
processor.load_data()
scores = processor.process_moral_scores()          # normalized to [-1, 1]
eval_data = processor.create_evaluation_dataset(n_samples=100)
```

### Peer review (LLM-as-judge)

```python
from evalmoraal.core import ModelJudge

judge = ModelJudge()   # reads OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY
critique_df = judge.run_reciprocal_critique(models, reasoning_traces)
agreement = judge.calculate_peer_agreement_rates(critique_df)
```

## Command Line

The full pipeline (dual scoring, conflict detection, peer review, reports)
runs from the command line:

```bash
export OPENAI_API_KEY=sk-...
evalmoraal run --models gpt-4o-mini --samples 10 --data-dir sample_data
```

Review conflicts in the human arbitration dashboard:

```bash
evalmoraal dashboard          # requires the 'dashboards' extra
evalmoraal dashboard --judge  # extended judge dashboard
```

## Data

The pipeline expects a `WVS_Moral.csv` file inside `--data-dir` with a
`B_COUNTRY` column (numeric WVS country codes) and the moral question
columns `Q176`-`Q198` on the original 1-10 scale. The survey data itself
is distributed by the [World Values Survey](https://www.worldvaluessurvey.org/)
and is not bundled with this repository.

## Package Structure

```
EvalMORAAL/
├── pyproject.toml                    # package metadata (pip install evalmoraal)
├── src/evalmoraal/
│   ├── analysis/                     # conflict detection, score utils, plotting
│   ├── core/                         # WVS processing, dual scoring, judge, pipeline
│   ├── evaluation/                   # cross-evaluation, conflict resolution, dashboards
│   ├── visualization/                # figure and paper output generators
│   ├── cli.py                        # the `evalmoraal` command
│   └── env.py                        # API key handling (.env support)
├── tests/                            # unit tests (no API calls needed)
└── figures/                          # README images (full figures are in the paper)
```

## Figures

### Main Figures
- Framework overview diagram
- Tier-based scatter plots (WVS/PEW)
- Country alignment heatmaps
- Topic difficulty heatmaps
- Conflict distribution histogram

### Appendix Figures
- Per-model scatter plots
- Full country heatmaps
- Error distribution analysis

## Related Work

This work builds upon our previous study on cultural moral judgments:
- [Exploring Cultural Variations in Moral Judgments with LLMs](https://arxiv.org/abs/2506.12433)

## License

This project is licensed under the MIT License.

## Contact

- **Hadi Mohammadi** — Utrecht University
- Website: [mohammadi.cv](https://mohammadi.cv)

## Acknowledgments

We thank the World Values Survey and PEW Research Center for making their cross-cultural survey data publicly available.
