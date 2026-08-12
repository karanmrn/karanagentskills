"""Aggregate per-condition/per-trial records into the final results structure.

Input: a list of trial records (see TrialRecord). Output: results dict consumed by
charts.py. Cost efficiency is computed here (quality per dollar), NOT model-judged.

results.json shape:
{
  "conditions": {
     "<cond_id>": {
        "planner": str, "implementer": str,
        "dimensions": {"task_completion": float, "correctness": float, "code_quality": float, "verification": float},
        "dimensions_std": {...},                 # across trials (0 if single trial)
        "quality": float,                        # mean of 3 judged dims
        "quality_std": float,
        "cost_usd": float, "cost_std": float,
        "cost_efficiency": float,                # quality / cost_usd
        "trials": int,
     }, ...
  },
  "self_bias": { "<judge_key>": { "<cond_id>": float(avg judged dimensions), ... } },
  "judges": [ ... ],
}
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from duobench.judge import DIMENSIONS


@dataclass
class TrialRecord:
    condition_id: str
    planner: str
    implementer: str
    trial: int
    cost_usd: float
    # averaged judged dimensions for this single build (across judges)
    dimensions: dict[str, float]
    # raw per-judge dimension scores for self-bias: {judge_key: {dim: int}}
    per_judge: dict[str, dict[str, float]] = field(default_factory=dict)
    impl_status: str = "complete"
    # "pi_reported" | "configured" | "unknown" — see cost.compute_cost()
    cost_source: str = "unknown"
    # wall-clock seconds per phase (0.0 if not measured, e.g. older runs)
    plan_duration_s: float = 0.0
    impl_duration_s: float = 0.0


def _mean(xs: list[float], digits: int = 2) -> float:
    return round(statistics.fmean(xs), digits) if xs else 0.0


def _std(xs: list[float], digits: int = 2) -> float:
    return round(statistics.pstdev(xs), digits) if len(xs) > 1 else 0.0


def _majority_source(records: list[TrialRecord]) -> str:
    """Return the most common cost source across trials ('unknown' if none)."""
    if not records:
        return "unknown"
    return statistics.mode(r.cost_source for r in records)


def aggregate(records: list[TrialRecord], judges: list[str]) -> dict:
    by_cond: dict[str, list[TrialRecord]] = {}
    for r in records:
        by_cond.setdefault(r.condition_id, []).append(r)

    conditions: dict[str, dict] = {}
    for cid, trs in by_cond.items():
        dims = {
            d: _mean([t.dimensions.get(d, 0.0) for t in trs]) for d in DIMENSIONS
        }
        dims_std = {
            d: _std([t.dimensions.get(d, 0.0) for t in trs]) for d in DIMENSIONS
        }
        qualities = [
            statistics.fmean([t.dimensions.get(d, 0.0) for d in DIMENSIONS]) for t in trs
        ]
        costs = [t.cost_usd for t in trs]
        durations = [t.plan_duration_s + t.impl_duration_s for t in trs]
        quality = _mean(qualities)
        cost_usd = _mean(costs, 4)
        conditions[cid] = {
            "planner": trs[0].planner,
            "implementer": trs[0].implementer,
            "dimensions": dims,
            "dimensions_std": dims_std,
            "quality": quality,
            "quality_std": _std(qualities),
            "cost_usd": cost_usd,
            "cost_std": _std(costs, 4),
            "cost_efficiency": round(quality / cost_usd, 1) if cost_usd > 0 else 0.0,
            "trials": len(trs),
            "impl_statuses": [t.impl_status for t in trs],
            "cost_source": _majority_source(trs),
            "duration_s": _mean(durations),
            "duration_std": _std(durations),
            "plan_duration_s": _mean([t.plan_duration_s for t in trs]),
            "impl_duration_s": _mean([t.impl_duration_s for t in trs]),
        }

    # Self-bias: for each judge, its average overall score per condition.
    self_bias: dict[str, dict[str, float]] = {j: {} for j in judges}
    bias_acc: dict[str, dict[str, list[float]]] = {j: {} for j in judges}
    for r in records:
        for jkey, dimscores in r.per_judge.items():
            if jkey not in bias_acc:
                bias_acc[jkey] = {}
            overall = statistics.fmean([dimscores.get(d, 0.0) for d in DIMENSIONS]) if dimscores else 0.0
            bias_acc[jkey].setdefault(r.condition_id, []).append(overall)
    for jkey, cond_map in bias_acc.items():
        self_bias[jkey] = {cid: _mean(vals) for cid, vals in cond_map.items()}

    return {"conditions": conditions, "self_bias": self_bias, "judges": judges}
