# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "matplotlib>=3.9",
#     "numpy>=1.26",
#     "pandas>=2.0",
#     "seaborn>=0.13",
# ]
# ///
"""Seed duobench plots — run in place OR copy to runs/<ts>/plots.py and adapt.

Two ways to run (both work — the import below self-locates `plot_styles`):
    uv run "$SKILL_DIR"/scripts/plots_example.py runs/<ts>          # in place
    cp scripts/plots_example.py runs/<ts>/plots.py && uv run python runs/<ts>/plots.py runs/<ts>

The helpers in ``plot_styles`` return tidy DataFrames with dimension names read
dynamically, so novel requests ("only opus conditions", "correctness vs cost",
"facet by planner") are small seaborn edits to the blocks below, not rewrites.

Default plot set (all styled consistently: seaborn whitegrid/talk, soft panel,
white-edged marks, value labels, bold title + muted subtitle, despined):
  1. leaderboard      — quality per condition (sorted), with std error bars
  2. cost-vs-quality  — the money chart, with iso-efficiency guide lines + legend
  3. dimensions       — per-dimension grouped bars
  4. self-bias        — does each judge favor its OWN model? (own vs other bars)
  5. cost-breakdown   — plan vs implement cost per condition (sorted, labeled)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Self-locate plot_styles whether this file runs from scripts/ or a copy in runs/<ts>/.
_here = Path(__file__).resolve()
for _cand in (_here.parent, *_here.parents):
    if (_cand / "plot_styles.py").exists():
        sys.path.insert(0, str(_cand)); break
    if (_cand / "scripts" / "plot_styles.py").exists():
        sys.path.insert(0, str(_cand / "scripts")); break

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from plot_styles import (
    apply_duobench_theme,
    color_for,
    conditions_frame,
    dimension_names,
    dimensions_long,
    load_results,
    load_trials,
    palette_for,
    save,
    self_bias_frame,
)

RUN_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent

# shared styling tokens
PANEL = "#fbfbfd"
MUTED = "#6b7280"
EDGE = "#e2e5ea"


def _header(ax, title, subtitle):
    ax.set_title(title, fontweight="bold", pad=30, loc="left")
    ax.text(0, 1.03, subtitle, transform=ax.transAxes, fontsize=9.5, color=MUTED)


def main(run_dir: Path) -> None:
    apply_duobench_theme()
    results = load_results(run_dir)
    cdf = conditions_frame(results).sort_values("quality", ascending=False)
    if cdf.empty:
        print("no conditions in results.json; nothing to plot")
        return
    dims = dimension_names(results)
    cond_order = list(cdf["condition_id"])          # stable order reused below
    palette = palette_for(cond_order)

    # 1) Leaderboard ------------------------------------------------------- #
    with sns.axes_style("whitegrid"), sns.plotting_context("talk", font_scale=0.72):
        fig, ax = plt.subplots(figsize=(10, max(3.2, 0.62 * len(cdf) + 1.2)))
        fig.patch.set_facecolor("white"); ax.set_facecolor(PANEL)
        sns.barplot(data=cdf, y="condition_id", x="quality", order=cond_order,
                    hue="condition_id", palette=palette, legend=False, ax=ax,
                    edgecolor="white", linewidth=1.2, zorder=3)
        ax.errorbar(cdf["quality"], range(len(cdf)), xerr=cdf["quality_std"],
                    fmt="none", ecolor="#374151", elinewidth=1, capsize=4, zorder=4)
        for yi, q in enumerate(cdf["quality"]):
            ax.annotate(f"{q:.2f}", (q, yi), xytext=(6, 0), textcoords="offset points",
                        va="center", ha="left", fontsize=9.5, fontweight="bold", color="#374151")
        ax.set_xlim(0, 10.6)
        ax.set_xlabel("quality  (mean of judged dimensions)", labelpad=8)
        ax.set_ylabel("")
        _header(ax, "Leaderboard", "average quality per condition (higher = better)")
        sns.despine(ax=ax, left=True); ax.tick_params(axis="y", length=0)
        fig.tight_layout()
        save(fig, run_dir, "leaderboard", csv=cdf)

    # 2) Cost vs quality (the money chart) --------------------------------- #
    with sns.axes_style("whitegrid"), sns.plotting_context("talk", font_scale=0.72):
        fig, ax = plt.subplots(figsize=(10, 7.2))
        fig.patch.set_facecolor("white"); ax.set_facecolor(PANEL)
        xmax = float(cdf["cost_usd"].max()) * 1.15 or 1.0
        for eff_line in (10, 20, 30):
            ax.plot([0, xmax], [0, eff_line * xmax], color="#d8dde6", lw=1, ls=(0, (4, 4)), zorder=0)
            if eff_line * xmax >= 10:
                lx, ly, ha, va = 10 / eff_line, 9.85, "left", "top"
            else:
                lx, ly, ha, va = xmax, eff_line * xmax, "right", "bottom"
            ax.annotate(f"  {eff_line}× ", (lx, ly), color="#aab1bd", fontsize=9, ha=ha, va=va, zorder=0)
        for _, r in cdf.iterrows():
            eff = r.get("cost_efficiency", 0.0)
            ax.errorbar(r["cost_usd"], r["quality"], xerr=r["cost_std"], yerr=r["quality_std"],
                        fmt="o", markersize=15, color=color_for(r["condition_id"]),
                        markeredgecolor="white", markeredgewidth=1.6,
                        ecolor="#9aa1ad", elinewidth=1, capsize=3, zorder=5,
                        label=f"{r['condition_id']}  ·  Q {r['quality']:.2f}   ${r['cost_usd']:.2f}   eff {eff:.1f}")
        ax.annotate("better value", xy=(0.06, 0.95), xytext=(0.30, 0.86),
                    xycoords="axes fraction", textcoords="axes fraction",
                    fontsize=10, color=MUTED, fontstyle="italic", ha="center",
                    arrowprops=dict(arrowstyle="-|>", color="#9aa1ad", lw=1.4))
        ax.set_xlabel("cost  (USD)", labelpad=8); ax.set_ylabel("quality  (0–10)", labelpad=8)
        ax.set_xlim(0, xmax); ax.set_ylim(0, 10)
        _header(ax, "Cost vs. quality",
                "top-left is best $/quality  ·  dashed lines = iso-efficiency (quality ÷ cost)")
        sns.despine(ax=ax)
        h, lbl = ax.get_legend_handles_labels()
        leg_order = sorted(range(len(lbl)), key=lambda i: -cdf.iloc[i].get("cost_efficiency", 0.0))
        leg = ax.legend([h[i] for i in leg_order], [lbl[i] for i in leg_order],
                        title="condition  —  best $/quality first", title_fontsize=9.5, fontsize=8.5,
                        loc="lower center", borderaxespad=1.2, frameon=True, framealpha=0.96,
                        edgecolor=EDGE, handletextpad=0.6, labelspacing=0.55)
        leg.get_title().set_fontweight("bold"); leg.get_frame().set_facecolor("white")
        fig.tight_layout()
        save(fig, run_dir, "cost-vs-quality", csv=cdf[["condition_id", "cost_usd", "quality", "cost_efficiency"]])

    # 3) Per-dimension grouped bars ---------------------------------------- #
    long = dimensions_long(results)
    if not long.empty:
        with sns.axes_style("whitegrid"), sns.plotting_context("talk", font_scale=0.7):
            fig, ax = plt.subplots(figsize=(max(9, 1.7 * len(dims)), 6.2))
            fig.patch.set_facecolor("white"); ax.set_facecolor(PANEL)
            sns.barplot(data=long, x="dimension", y="score", hue="condition_id",
                        order=dims, hue_order=cond_order, palette=palette, ax=ax,
                        edgecolor="white", linewidth=0.8, zorder=3)
            ax.set_ylim(0, 10); ax.set_xlabel(""); ax.set_ylabel("score  (0–10)", labelpad=8)
            _header(ax, "Scores by dimension", "how each condition did on each judged dimension")
            ax.legend(title="", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8, frameon=False)
            sns.despine(ax=ax)
            fig.subplots_adjust(right=0.78)   # reserve room for outside legend (save() has no tight bbox)
            save(fig, run_dir, "dimensions", csv=long)

    # 4) Judge self-bias: does each judge favor its OWN model? -------------- #
    sb = self_bias_frame(results)
    if not sb.empty:
        rows = []
        for judge in sb.index:
            own, other = [], []
            for cid in sb.columns:
                val = sb.loc[judge, cid]
                if val is None or (isinstance(val, float) and np.isnan(val)):
                    continue
                impl = results["conditions"].get(cid, {}).get("implementer")
                (own if impl == judge else other).append(float(val))
            if own and other:
                rows.append((judge, sum(own) / len(own), sum(other) / len(other)))
        if rows:
            bias = pd.DataFrame(rows, columns=["judge", "own", "other"])
            bias["delta"] = bias["own"] - bias["other"]
            with sns.axes_style("whitegrid"), sns.plotting_context("talk", font_scale=0.72):
                c_own, c_other = "#ef6f6c", "#9aa7b8"
                fig, ax = plt.subplots(figsize=(max(8, 3.4 * len(bias)), 6))
                fig.patch.set_facecolor("white"); ax.set_facecolor(PANEL)
                x = np.arange(len(bias)); w = 0.34
                ax.bar(x - w / 2, bias["other"], w, color=c_other, edgecolor="white",
                       linewidth=1.2, label="scoring other models' code", zorder=3)
                ax.bar(x + w / 2, bias["own"], w, color=c_own, edgecolor="white",
                       linewidth=1.2, label="scoring its OWN model's code", zorder=3)
                for xi, (_, r) in zip(x, bias.iterrows()):
                    for xpos, val in ((xi - w / 2, r["other"]), (xi + w / 2, r["own"])):
                        ax.annotate(f"{val:.2f}", (xpos, val), xytext=(0, 4), textcoords="offset points",
                                    ha="center", va="bottom", fontsize=10, color="#374151")
                    d = r["delta"]
                    verdict = "self-favoring" if d > 0.05 else ("harsher on self" if d < -0.05 else "neutral")
                    col = "#c0392b" if d > 0.05 else ("#1e8449" if d < -0.05 else MUTED)
                    ax.annotate(f"{d:+.2f}\n{verdict}", (xi, max(r["own"], r["other"])), xytext=(0, 26),
                                textcoords="offset points", ha="center", va="bottom",
                                fontsize=10, fontweight="bold", color=col)
                lo = max(0.0, float(min(bias["own"].min(), bias["other"].min())) - 0.6)
                hi = float(max(bias["own"].max(), bias["other"].max())) + 1.1
                ax.set_ylim(lo, hi)
                ax.set_xticks(x); ax.set_xticklabels(bias["judge"])
                ax.set_ylabel("average score given", labelpad=8); ax.set_xlabel("")
                _header(ax, "Do judges favor their own model?",
                        "average score each judge gave, split by who wrote the code  ·  Δ = own − other")
                ax.legend(loc="upper right", frameon=True, framealpha=0.96, edgecolor=EDGE, fontsize=9)
                sns.despine(ax=ax, left=True); ax.tick_params(axis="y", length=0)
                ax.grid(axis="x", visible=False)
                fig.tight_layout()
                save(fig, run_dir, "self-bias", csv=bias)

    # 5) Plan vs implement cost breakdown ---------------------------------- #
    tdf = load_trials(run_dir)
    if not tdf.empty:
        agg = tdf.groupby("condition_id").agg(
            plan_cost=("plan_cost_usd", "mean"),
            total_cost=("cost_usd", "mean"),
        ).reindex(cond_order)
        agg["impl_cost"] = (agg["total_cost"] - agg["plan_cost"]).clip(lower=0)
        agg = agg.sort_values("total_cost", ascending=True)
        with sns.axes_style("whitegrid"), sns.plotting_context("talk", font_scale=0.72):
            c_plan, c_impl = "#5b8ff9", "#ef6f6c"
            fig, ax = plt.subplots(figsize=(10.5, max(3.2, 0.72 * len(agg) + 1.4)))
            fig.patch.set_facecolor("white"); ax.set_facecolor(PANEL)
            y = np.arange(len(agg))
            ax.barh(y, agg["plan_cost"], color=c_plan, label="plan",
                    edgecolor="white", linewidth=1.2, height=0.66, zorder=3)
            ax.barh(y, agg["impl_cost"], left=agg["plan_cost"], color=c_impl, label="implement",
                    edgecolor="white", linewidth=1.2, height=0.66, zorder=3)
            ax.set_yticks(y); ax.set_yticklabels(agg.index)
            for yi, tot in zip(y, agg["total_cost"]):
                ax.annotate(f"${tot:.2f}", (tot, yi), xytext=(7, 0), textcoords="offset points",
                            va="center", ha="left", fontsize=9.5, fontweight="bold", color="#374151")
            ax.margins(x=0.14)
            ax.set_xlabel("cost  (USD)", labelpad=8); ax.set_ylabel("")
            _header(ax, "Cost breakdown", "planner vs. implementer spend per condition")
            ax.legend(loc="lower right", frameon=True, framealpha=0.96, edgecolor=EDGE, fontsize=9.5)
            sns.despine(ax=ax, left=True); ax.tick_params(axis="y", length=0)
            ax.grid(axis="x", visible=False)
            fig.tight_layout()
            save(fig, run_dir, "cost-breakdown", csv=agg.reset_index())

    print(f"plots written to {(run_dir / 'results').resolve()}")


if __name__ == "__main__":
    main(RUN_DIR)
