# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""Run ONE duobench phase as ONE Pi RPC instance, then write a result.json sentinel.

This is the atomic unit the duobench skill launches (one per tmux session):

    uv run "$SKILL_DIR"/scripts/run_phase.py --phase plan      --planner kimi-k2.6  ...
    uv run "$SKILL_DIR"/scripts/run_phase.py --phase implement --planner kimi-k2.6 --implementer gpt-5.5 ...
    uv run "$SKILL_DIR"/scripts/run_phase.py --phase judge     --judge-key gpt-5.5  ...

The script's LAST action is an atomic write of ``<out-dir>/result.json`` (or, for
judge jobs, ``<out-dir>/results/judge-<key>.json``). Its mere presence is the
completion signal the agent polls for; on any failure the script still writes a
``status:"error"`` sentinel and exits non-zero. Parallelism, sequencing, and
aggregation live in the agent/tmux layer — this script does exactly one unit.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

# Allow `uv run "$SKILL_DIR"/scripts/run_phase.py` without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from duobench import engine  # noqa: E402
from duobench.config import load_config  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _result_path(phase: str, out_dir: Path, judge_key: str | None) -> Path:
    if phase == "judge":
        return out_dir / "results" / f"judge-{judge_key}.json"
    return out_dir / "result.json"


def _write_result_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, default=str))
    os.replace(tmp, path)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="run_phase", description="Run one duobench phase as one Pi RPC instance.")
    ap.add_argument("--phase", required=True, choices=["plan", "implement", "judge"])
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--issue", default="")
    ap.add_argument("--trial", type=int, default=0)
    ap.add_argument("--condition", default="")
    ap.add_argument("--submission-mode", default="local_commit", choices=["local_commit", "pr"])
    ap.add_argument("--no-pi-sessions", action="store_true", help="do not persist Pi sessions")
    ap.add_argument("--models-config", default=None, help="defaults to the skill's config/models.yaml")
    ap.add_argument("--conditions-config", default=None, help="defaults to the skill's config/conditions.yaml")
    ap.add_argument("--costs-config", default="costs.yaml")
    ap.add_argument("--timeout", type=float, default=None, help="phase wall-clock timeout (defaults per phase)")
    # plan
    ap.add_argument("--planner", default="")
    # implement
    ap.add_argument("--implementer", default="")
    ap.add_argument("--plan-path", default="")
    # judge
    ap.add_argument("--judge-key", default="")
    ap.add_argument("--build-dir", default="")
    ap.add_argument("--commit-sha", default="")
    ap.add_argument("--pr-id", default="")
    return ap.parse_args(argv)


def _default_timeout(phase: str, override: float | None) -> float:
    if override is not None:
        return override
    return {"plan": 600.0, "implement": 1800.0, "judge": 300.0}[phase]


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    out_dir = Path(args.out_dir)
    run_dir = Path(args.run_dir)
    result_path = _result_path(args.phase, out_dir, args.judge_key or None)
    save_pi_sessions = not args.no_pi_sessions
    run_label = run_dir.name
    timeout = _default_timeout(args.phase, args.timeout)
    started = time.monotonic()
    started_at = _now()

    base = {
        "schema": 1,
        "phase": args.phase,
        "run_dir": str(run_dir),
        "condition_id": args.condition,
        "trial": args.trial,
        "started_at": started_at,
    }

    try:
        issue_url = engine.load_issue_url(args.issue)
        cfg = load_config(args.models_config, args.conditions_config, args.costs_config)
        prompts = engine.load_prompts(args.submission_mode, issue_url)

        if args.phase == "plan":
            if not args.planner:
                raise SystemExit("--planner is required for --phase plan")
            outcome = engine.plan_one(
                cfg, prompts, args.planner,
                out_dir=out_dir, trial=args.trial, timeout=timeout,
                save_pi_sessions=save_pi_sessions, run_label=run_label,
            )
        elif args.phase == "implement":
            if not (args.planner and args.implementer and args.condition and args.plan_path):
                raise SystemExit("--phase implement requires --planner --implementer --condition --plan-path")
            outcome = engine.implement_one(
                cfg, prompts,
                planner_key=args.planner, implementer_key=args.implementer,
                condition_id=args.condition, plan_path=Path(args.plan_path),
                out_dir=out_dir, trial=args.trial,
                impl_timeout=timeout, submission_mode=args.submission_mode,
                save_pi_sessions=save_pi_sessions, run_label=run_label,
            )
        else:  # judge
            if not (args.judge_key and args.build_dir and args.condition):
                raise SystemExit("--phase judge requires --judge-key --build-dir --condition")
            outcome = engine.judge_one(
                cfg, prompts,
                judge_key=args.judge_key, build_dir=Path(args.build_dir),
                out_dir=out_dir, condition_id=args.condition, trial=args.trial,
                issue_url=issue_url, commit_sha=args.commit_sha, pr_id=args.pr_id,
                timeout=timeout, save_pi_sessions=save_pi_sessions, run_label=run_label,
            )

        payload = {
            **base,
            "status": outcome.status,
            "exit_ok": True,
            "ended_at": _now(),
            "duration_s": round(time.monotonic() - started, 2),
            "cost_usd": outcome.cost_usd,
            "cost_source": outcome.cost_source,
            "artifact": outcome.artifact,
            "error": None,
            "notes": outcome.notes,
        }
        _write_result_atomic(result_path, payload)
        # A non-"complete" status (timeout/stalled) is still a valid data point:
        # exit 0 so the agent treats the job as finished and reads status.
        return 0
    except BaseException as e:  # noqa: BLE001 — sentinel must always be written
        payload = {
            **base,
            "status": "error",
            "exit_ok": False,
            "ended_at": _now(),
            "duration_s": round(time.monotonic() - started, 2),
            "cost_usd": 0.0,
            "cost_source": "unknown",
            "artifact": {},
            "error": f"{type(e).__name__}: {e}",
            "notes": [traceback.format_exc()],
        }
        try:
            _write_result_atomic(result_path, payload)
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
