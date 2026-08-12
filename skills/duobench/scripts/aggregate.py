# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""Assemble results.json from a run dir's trial.json files. Pure: NO model calls.

    uv run "$SKILL_DIR"/scripts/aggregate.py runs/<ts> [--judges kimi-k2.6,gpt-5.5]

Run this after all judge jobs for a run have finished (and again after adding a
new condition). It folds every conditions/*/trial-*/trial.json into the judged
record, writes judge_scores back into each trial.json, and (over)writes
results.json. Then prints a leaderboard. Safe to re-run; it rescans the whole
run dir each time so old + newly-added conditions merge automatically.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `uv run "$SKILL_DIR"/scripts/aggregate.py` without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from duobench import engine  # noqa: E402


def _print_leaderboard(results: dict) -> None:
    conditions = results.get("conditions", {})
    if not conditions:
        print("no conditions found; nothing to rank")
        return
    ranked = sorted(conditions.items(), key=lambda kv: kv[1].get("quality", 0.0), reverse=True)
    print("\nleaderboard (quality | cost$ | source | efficiency | statuses):")
    unknown: list[str] = []
    for cid, c in ranked:
        source = c.get("cost_source", "unknown")
        if source == "unknown":
            unknown.append(cid)
        statuses = ",".join(c.get("impl_statuses", []) or [])
        print(
            f"  {cid:28} {c.get('quality', 0):5.2f} | {c.get('cost_usd', 0):.4f} | "
            f"{source:11} | {c.get('cost_efficiency', 0):7.2f} | {statuses}"
        )
    if unknown:
        print(
            "\nwarning: cost$ source 'unknown' (no registry pricing) for: "
            + ", ".join(unknown)
            + ". Add the model key(s) to config/models.yaml or costs.yaml; "
            "cost_efficiency is meaningless until pricing is set."
        )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="aggregate", description="Rebuild results.json from trial.json files.")
    ap.add_argument("run_dir")
    ap.add_argument("--judges", default="", help="comma-separated judge keys; default: discover from disk")
    args = ap.parse_args(argv)

    run_dir = Path(args.run_dir)
    if not (run_dir / "conditions").is_dir():
        print(f"error: {run_dir}/conditions not found", file=sys.stderr)
        return 1
    judges = engine._parse_csv(args.judges) or None
    results = engine.assemble_results(run_dir, judges)
    _print_leaderboard(results)
    print(f"\nresults.json written: {(run_dir / 'results.json').resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
