"""
Visualization utilities for EvalMORAAL results.

Provides functions for creating publication-ready plots from evaluation data.
"""

import os
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def setup_plotting_style():
    """Set up consistent plotting style for publication-ready figures."""
    try:
        plt.style.use("seaborn-v0_8-whitegrid")
    except:
        plt.style.use("seaborn-whitegrid")

    sns.set_context("paper", font_scale=1.2)
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["savefig.dpi"] = 300
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans"]


def plot_country_heatmap(
    data: pd.DataFrame,
    value_col: str,
    title: str,
    save_path: Optional[str] = None,
    figsize: tuple = (12, 8),
) -> None:
    """
    Create heatmap showing performance across countries and models.

    Args:
        data: DataFrame with country, model, and value columns
        value_col: Name of column containing values to plot
        title: Plot title
        save_path: Path to save figure (optional)
        figsize: Figure size tuple
    """
    setup_plotting_style()

    # Pivot for heatmap
    pivot_df = data.pivot_table(
        values=value_col, index="country", columns="model", aggfunc="mean"
    )

    fig, ax = plt.subplots(figsize=figsize)

    sns.heatmap(
        pivot_df,
        cmap="RdBu_r",
        center=0.5,
        vmin=0,
        vmax=1,
        cbar_kws={"label": "Pearson Correlation"},
        annot=False,
        ax=ax,
    )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Country", fontsize=12)

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved plot to {save_path}")

    plt.show()
    plt.close()


def plot_error_distribution(
    errors: np.ndarray,
    title: str,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
    color: str = "steelblue",
) -> None:
    """
    Plot distribution of absolute errors.

    Args:
        errors: Array of error values
        title: Plot title
        save_path: Path to save figure (optional)
        figsize: Figure size tuple
        color: Bar color
    """
    setup_plotting_style()

    fig, ax = plt.subplots(figsize=figsize)

    ax.hist(errors, bins=50, alpha=0.7, color=color, edgecolor="black", density=True)
    ax.axvline(
        np.mean(errors),
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Mean: {np.mean(errors):.3f}",
    )
    ax.axvline(
        np.median(errors),
        color="green",
        linestyle="--",
        linewidth=2,
        label=f"Median: {np.median(errors):.3f}",
    )

    ax.set_xlabel("Absolute Error", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved plot to {save_path}")

    plt.show()
    plt.close()


def plot_topic_heatmap(
    data: pd.DataFrame,
    value_col: str,
    title: str,
    save_path: Optional[str] = None,
    figsize: tuple = (14, 8),
) -> None:
    """
    Create heatmap showing model performance across topics.

    Args:
        data: DataFrame with topic, model, and value columns
        value_col: Name of column containing values to plot
        title: Plot title
        save_path: Path to save figure (optional)
        figsize: Figure size tuple
    """
    setup_plotting_style()

    # Pivot for heatmap
    pivot_df = data.pivot_table(
        values=value_col, index="topic", columns="model", aggfunc="mean"
    )

    fig, ax = plt.subplots(figsize=figsize)

    sns.heatmap(
        pivot_df,
        cmap="YlOrRd",
        vmin=0,
        vmax=1,
        cbar_kws={"label": "Mean Absolute Error"},
        annot=False,
        ax=ax,
    )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Topic", fontsize=12)

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved plot to {save_path}")

    plt.show()
    plt.close()


def plot_model_comparison(
    metrics_df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    save_path: Optional[str] = None,
    figsize: tuple = (12, 8),
) -> None:
    """
    Create scatter plot comparing model performance on two metrics.

    Args:
        metrics_df: DataFrame with model metrics
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Plot title
        save_path: Path to save figure (optional)
        figsize: Figure size tuple
    """
    setup_plotting_style()

    fig, ax = plt.subplots(figsize=figsize)

    ax.scatter(
        metrics_df[x_col],
        metrics_df[y_col],
        s=100,
        alpha=0.6,
        c=range(len(metrics_df)),
        cmap="viridis",
    )

    # Add diagonal line for reference
    lims = [0, 1]
    ax.plot(lims, lims, "k--", alpha=0.5, label="y=x")

    # Annotate top models
    for idx, row in metrics_df.head(5).iterrows():
        model_label = row.get("model", str(idx))
        if len(model_label) > 15:
            model_label = model_label[:12] + "..."
        ax.annotate(
            model_label,
            (row[x_col], row[y_col]),
            fontsize=8,
            alpha=0.7,
        )

    ax.set_xlabel(x_col.replace("_", " ").title(), fontsize=12)
    ax.set_ylabel(y_col.replace("_", " ").title(), fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved plot to {save_path}")

    plt.show()
    plt.close()


def plot_score_distributions(
    data: pd.DataFrame,
    score_cols: List[str],
    group_col: str,
    title: str,
    save_path: Optional[str] = None,
    figsize: tuple = (14, 10),
) -> None:
    """
    Plot score distributions by group (e.g., model category).

    Args:
        data: DataFrame with score columns and group column
        score_cols: List of score column names to plot
        group_col: Column to group by
        title: Plot title
        save_path: Path to save figure (optional)
        figsize: Figure size tuple
    """
    setup_plotting_style()

    groups = data[group_col].unique()[:4]  # Max 4 groups for 2x2 grid
    n_groups = len(groups)

    fig, axes = plt.subplots(2, 2, figsize=figsize)
    axes = axes.flatten()

    colors = ["steelblue", "coral", "seagreen", "purple"]

    for idx, (ax, group) in enumerate(zip(axes[:n_groups], groups)):
        group_data = data[data[group_col] == group]

        for i, col in enumerate(score_cols[:2]):  # Max 2 score types
            if col in group_data.columns:
                ax.hist(
                    group_data[col].dropna(),
                    bins=30,
                    alpha=0.5,
                    label=col.replace("_", " ").title(),
                    color=colors[i],
                    density=True,
                )

        ax.set_xlabel("Score", fontsize=11)
        ax.set_ylabel("Density", fontsize=11)
        ax.set_title(f"{group}", fontsize=12, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-1, 1)

    # Hide unused subplots
    for ax in axes[n_groups:]:
        ax.set_visible(False)

    plt.suptitle(title, fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved plot to {save_path}")

    plt.show()
    plt.close()


def create_latex_table(
    data: pd.DataFrame,
    columns: List[str],
    caption: str,
    label: str,
    save_path: Optional[str] = None,
    float_format: str = "%.3f",
) -> str:
    """
    Generate LaTeX table from DataFrame.

    Args:
        data: DataFrame to convert
        columns: Columns to include
        caption: Table caption
        label: Table label for LaTeX
        save_path: Path to save .tex file (optional)
        float_format: Format string for floating point numbers

    Returns:
        LaTeX table string
    """
    # Filter columns
    table_data = data[columns].copy()

    # Generate LaTeX
    latex = table_data.to_latex(
        index=False,
        float_format=float_format,
        caption=caption,
        label=label,
        escape=False,
    )

    # Add booktabs-style formatting
    latex = latex.replace("\\toprule", "\\toprule")
    latex = latex.replace("\\midrule", "\\midrule")
    latex = latex.replace("\\bottomrule", "\\bottomrule")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as f:
            f.write(latex)
        print(f"Saved LaTeX table to {save_path}")

    return latex
