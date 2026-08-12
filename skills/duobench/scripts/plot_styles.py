"""Shared seaborn theme + tidy data loaders for duobench plots.

Import this from a run's ``plots.py`` (copied from ``scripts/plots_example.py``);
do NOT edit it per-run — keep the look consistent across every chart. The loaders
return tidy pandas DataFrames and read dimension names dynamically from the data
(the on-disk schema has drifted historically — never hardcode dimension names).

Typical use:

    from plot_styles import (
        apply_duobench_theme, load_results, load_trials,
        dimension_names, color_for, save,
    )
    apply_duobench_theme()
    results = load_results(RUN_DIR)
    df = load_trials(RUN_DIR)
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Judged dimensions are read from the data; this is only a stable display order
# fallback when a dimension set can't be inferred.
_FALLBACK_DIMENSIONS = ("task_completion", "correctness", "code_quality", "verification")

# Deterministic, colorblind-safe color per model key, so the same model is the
# same color in every chart of a run. Filled lazily by color_for().
_PALETTE_CACHE: dict[str, tuple[float, float, float]] = {}


def apply_duobench_theme() -> None:
    """Apply the shared seaborn/matplotlib theme. Call once before plotting."""
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update({
        "figure.dpi": 130,
        "savefig.dpi": 130,
        "savefig.bbox": "tight",
        "figure.autolayout": True,
        "axes.titleweight": "bold",
        "axes.titlesize": "large",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 11,
        "legend.frameon": False,
    })


def color_for(key: str) -> tuple[float, float, float]:
    """Stable colorblind-safe color for a model/condition key."""
    if key not in _PALETTE_CACHE:
        palette = sns.color_palette("colorblind", n_colors=max(10, len(_PALETTE_CACHE) + 1))
        # Assign by stable sorted position so colors don't shuffle between calls.
        for i, k in enumerate(sorted({*_PALETTE_CACHE, key})):
            _PALETTE_CACHE[k] = palette[i % len(palette)]
    return _PALETTE_CACHE[key]


def palette_for(keys: list[str]) -> dict[str, tuple[float, float, float]]:
    """A {key: color} mapping for a set of conditions/models (stable across runs)."""
    return {k: color_for(k) for k in keys}


# --------------------------------------------------------------------------- #
# Loaders
# --------------------------------------------------------------------------- #


def load_results(run_dir: str | Path) -> dict:
    """Load results.json (the aggregate() output)."""
    return json.loads((Path(run_dir) / "results.json").read_text())


def dimension_names(results: dict) -> list[str]:
    """Judged dimension names, read dynamically from results.json."""
    for c in (results.get("conditions") or {}).values():
        dims = c.get("dimensions") or {}
        if dims:
            return list(dims.keys())
    return list(_FALLBACK_DIMENSIONS)


def conditions_frame(results: dict) -> pd.DataFrame:
    """Per-condition wide DataFrame from results.json (one row per condition)."""
    rows = []
    for cid, c in (results.get("conditions") or {}).items():
        row = {
            "condition_id": cid,
            "planner": c.get("planner", ""),
            "implementer": c.get("implementer", ""),
            "quality": c.get("quality", 0.0),
            "quality_std": c.get("quality_std", 0.0),
            "cost_usd": c.get("cost_usd", 0.0),
            "cost_std": c.get("cost_std", 0.0),
            "cost_efficiency": c.get("cost_efficiency", 0.0),
            "trials": c.get("trials", 0),
            "cost_source": c.get("cost_source", "unknown"),
            "impl_statuses": ",".join(c.get("impl_statuses", []) or []),
            "plan_duration_s": c.get("plan_duration_s", 0.0),
            "impl_duration_s": c.get("impl_duration_s", 0.0),
        }
        for d, v in (c.get("dimensions") or {}).items():
            row[d] = v
        rows.append(row)
    return pd.DataFrame(rows)


def dimensions_long(results: dict) -> pd.DataFrame:
    """Melted (condition_id, dimension, score) frame for grouped/faceted plots."""
    dims = dimension_names(results)
    df = conditions_frame(results)
    present = [d for d in dims if d in df.columns]
    return df.melt(
        id_vars=["condition_id", "planner", "implementer"],
        value_vars=present,
        var_name="dimension",
        value_name="score",
    )


def self_bias_frame(results: dict) -> pd.DataFrame:
    """Judge × condition matrix (rows=judges, cols=conditions) of avg scores."""
    sb = results.get("self_bias") or {}
    return pd.DataFrame(sb).T  # judges as rows


def load_trials(run_dir: str | Path) -> pd.DataFrame:
    """Tidy per-trial DataFrame from every conditions/*/trial-*/trial.json.

    Columns: condition_id, planner, implementer, trial, cost_usd, impl_status,
    cost_source, plan_duration_s, impl_duration_s, plan_cost_usd, commit_sha,
    plus one column per judged dimension (averaged across that trial's judges).
    """
    rows = []
    for tp in sorted((Path(run_dir) / "conditions").glob("*/trial-*/trial.json")):
        trial = json.loads(tp.read_text())
        rec = trial.get("record", {})
        artifacts = trial.get("artifacts", {})
        meta = trial.get("meta", {})
        row = {
            "condition_id": rec.get("condition_id", ""),
            "planner": rec.get("planner", ""),
            "implementer": rec.get("implementer", ""),
            "trial": rec.get("trial", 0),
            "cost_usd": rec.get("cost_usd", 0.0),
            "impl_status": rec.get("impl_status", ""),
            "cost_source": rec.get("cost_source", "unknown"),
            "plan_duration_s": rec.get("plan_duration_s", 0.0),
            "impl_duration_s": rec.get("impl_duration_s", 0.0),
            "plan_cost_usd": (artifacts.get("plan") or {}).get("cost_usd", 0.0),
            "commit_sha": meta.get("commit_sha", ""),
        }
        for d, v in (rec.get("dimensions") or {}).items():
            row[d] = v
        rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Saving
# --------------------------------------------------------------------------- #


def save(fig, run_dir: str | Path, name: str, *, csv: pd.DataFrame | None = None) -> Path:
    """Save a figure to runs/<ts>/results/<name>.png (+ optional <name>.csv)."""
    out = Path(run_dir) / "results"
    out.mkdir(parents=True, exist_ok=True)
    png = out / f"{name}.png"
    fig.savefig(png)
    plt.close(fig)
    if csv is not None:
        csv.to_csv(out / f"{name}.csv", index=False)
    return png
