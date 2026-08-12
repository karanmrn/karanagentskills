"""duobench engine: stateless, per-unit benchmark operations.

This module holds the reusable building blocks the benchmark needs, with NO
orchestration of its own. The agent (via the ``duobench`` skill) sequences the
phases by launching ``scripts/run_phase.py`` jobs; this module provides the
functions those jobs call.

Three per-unit runners — one Pi RPC session each:

* :func:`plan_one`      — run the planner, write ``plan.md`` + transcript.
* :func:`implement_one` — set up an isolated worktree (with local-commit safety
  wrappers), run the implementer, capture the commit, write ``trial.json``.
* :func:`judge_one`     — run one judge over one build, write its transcript.

Plus :func:`assemble_results` — pure, no model calls — which folds every
``trial.json`` into ``results.json`` (the agent runs this between judging and
plotting).

Everything here works headless (``ui=None``); there is no Rich dashboard and no
in-process parallelism — parallelism lives in the agent/tmux layer.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from duobench.aggregate import TrialRecord, aggregate
from duobench.config import SKILL_ROOT, Condition, Config, ConfigError, Model
from duobench.cost import compute_cost
from duobench.fingerprint import make_benchmark_fingerprint
from duobench.impl_phase import run_impl_phase
from duobench.judge import (
    DIMENSIONS,
    JudgeScore,
    average_dimensions,
    collect_source,
    judge_build,
)
from duobench.pi_rpc import PiSession
from duobench.plan_phase import run_plan_phase

DEFAULT_ISSUE_URL = "https://github.com/example/repo/issues/1"

# Captured commit metadata caps (see _capture_commit_artifacts).
_MAX_DIFF_CHARS = 200_000
_MAX_STAT_CHARS = 30_000


# --------------------------------------------------------------------------- #
# Prompts / config helpers
# --------------------------------------------------------------------------- #


def _load_prompt(name: str) -> str:
    """Load a prompt bundled with the skill (cwd is the target repo, never consulted)."""
    return (SKILL_ROOT / "prompts" / name).read_text()


def load_prompts(submission_mode: str, issue_url: str) -> dict[str, str]:
    """Resolve the prompt set for a submission mode.

    ``local_commit`` uses the commit-oriented implementer/judge prompts; ``pr``
    uses the legacy PR-creating prompts.
    """
    if submission_mode not in {"local_commit", "pr"}:
        raise ConfigError(f"unknown submission_mode: {submission_mode!r}")
    implement_name = "implement_local_commit.md" if submission_mode == "local_commit" else "implement.md"
    judge_name = "judge_local_commit.md" if submission_mode == "local_commit" else "judge.md"
    return {
        "issue_url": issue_url,
        "architect": _load_prompt("architect.md"),
        "implement": _load_prompt(implement_name),
        "judge": _load_prompt(judge_name),
    }


def _issue_url_from(prompts: dict[str, str]) -> str:
    return prompts.get("issue_url", DEFAULT_ISSUE_URL)


def _format_prompt_template(template: str, **values: str) -> str:
    try:
        return template.format(**values)
    except KeyError as e:
        missing = e.args[0]
        raise ConfigError(f"prompt template references unknown placeholder {{{missing}}}") from e


def load_issue_url(issue: str) -> str:
    text = issue.strip()
    if text:
        return text
    raise ConfigError("--issue is required; duobench is coupled to the GitHub issue workflow")


def check_issue_prereqs() -> None:
    if shutil.which("git") is None:
        raise ConfigError("git is required for real GitHub issue runs")
    if shutil.which("gh") is None:
        raise ConfigError("gh CLI is required for real GitHub issue runs")
    _git(["rev-parse", "--show-toplevel"], Path.cwd())


def _is_unknown_model(cfg: Config, spec: str) -> bool:
    """True when the spec has no registry entry in models.yaml."""
    return spec.partition(":")[0] not in cfg.models


def _merge_cost_source(*sources: str) -> str:
    """Combine per-phase cost sources: any 'unknown' dominates, then 'configured'."""
    if any(s == "unknown" for s in sources):
        return "unknown"
    if any(s == "configured" for s in sources):
        return "configured"
    return "pi_reported"


# --------------------------------------------------------------------------- #
# Matrix expansion
# --------------------------------------------------------------------------- #


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _dedupe_ordered(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _validate_model_specs(keys: list[str], flag: str) -> list[str]:
    keys = _dedupe_ordered(keys)
    if not keys:
        raise ConfigError(f"{flag} must include at least one Pi model spec")
    return keys


def select_conditions(cfg: Config, only: list[str] | None) -> list[Condition]:
    if not only:
        return cfg.conditions
    by_id = {c.id: c for c in cfg.conditions}
    missing = [o for o in only if o not in by_id]
    if missing:
        raise ConfigError(f"unknown condition id(s): {', '.join(missing)}")
    return [by_id[o] for o in only]


def make_matrix_conditions(cfg: Config, planners: list[str], implementers: list[str]) -> list[Condition]:
    """Generate the full planner×implementer matrix for the requested Pi model specs."""
    planners = _validate_model_specs(planners, "--planners/--models")
    implementers = _validate_model_specs(implementers, "--implementers/--models")
    conditions: list[Condition] = []
    used_ids: set[str] = set()
    for planner in planners:
        for implementer in implementers:
            base = (
                f"{_safe_path_part(planner)}-solo"
                if planner == implementer
                else f"{_safe_path_part(planner)}-x-{_safe_path_part(implementer)}"
            )
            cid = base
            suffix = 2
            while cid in used_ids:
                cid = f"{base}-{suffix}"
                suffix += 1
            used_ids.add(cid)
            conditions.append(Condition(id=cid, planner=planner, implementer=implementer))
    return conditions


def select_run_conditions(
    cfg: Config,
    *,
    condition_ids: list[str] | None = None,
    model_keys: list[str] | None = None,
    planner_keys: list[str] | None = None,
    implementer_keys: list[str] | None = None,
) -> tuple[list[Condition], str]:
    """Resolve a selection into concrete planner×implementer conditions."""
    condition_ids = condition_ids or []
    model_keys = model_keys or []
    planner_keys = planner_keys or []
    implementer_keys = implementer_keys or []

    matrix_requested = bool(model_keys or planner_keys or implementer_keys)
    if condition_ids and matrix_requested:
        raise ConfigError("use either --conditions or matrix flags (--models/--planners/--implementers), not both")

    if condition_ids:
        return select_conditions(cfg, condition_ids), "explicit conditions from conditions.yaml"

    if model_keys:
        if planner_keys or implementer_keys:
            raise ConfigError("--models cannot be combined with --planners or --implementers; use one style")
        keys = _validate_model_specs(model_keys, "--models")
        return make_matrix_conditions(cfg, keys, keys), f"full matrix from --models ({len(keys)} models)"

    if planner_keys or implementer_keys:
        if not planner_keys or not implementer_keys:
            raise ConfigError("provide both --planners and --implementers, or use --models for a square matrix")
        planners = _validate_model_specs(planner_keys, "--planners")
        implementers = _validate_model_specs(implementer_keys, "--implementers")
        return make_matrix_conditions(cfg, planners, implementers), (
            f"rectangular matrix from --planners/--implementers ({len(planners)}×{len(implementers)})"
        )

    return cfg.conditions, "explicit conditions from conditions.yaml"


def _unique_planners(conditions: list[Condition]) -> list[str]:
    planners: list[str] = []
    seen: set[str] = set()
    for cond in conditions:
        if cond.planner not in seen:
            seen.add(cond.planner)
            planners.append(cond.planner)
    return planners


def _safe_path_part(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in value)


def condition_id_for(planner: str, implementer: str) -> str:
    """The canonical directory/join-key id for a planner×implementer pairing."""
    if planner == implementer:
        return f"{_safe_path_part(planner)}-solo"
    return f"{_safe_path_part(planner)}-x-{_safe_path_part(implementer)}"


# --------------------------------------------------------------------------- #
# git / gh helpers + worktree safety scaffolding
# --------------------------------------------------------------------------- #


def _git(args: list[str], cwd: Path, *, timeout: float = 60.0) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise ConfigError(f"git {' '.join(args)} failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout.strip()


def _gh(args: list[str], cwd: Path, *, timeout: float = 60.0) -> str:
    proc = subprocess.run(
        ["gh", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise ConfigError(f"gh {' '.join(args)} failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout.strip()


def _origin_repo_slug(remote_url: str) -> str:
    """Return owner/repo from a GitHub remote URL."""
    remote_url = remote_url.strip()
    patterns = (
        r"^git@github\.com:([^/]+/[^/]+?)(?:\.git)?$",
        r"^https://github\.com/([^/]+/[^/]+?)(?:\.git)?/?$",
        r"^ssh://git@github\.com/([^/]+/[^/]+?)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.match(pattern, remote_url)
        if match:
            return match.group(1)
    raise ConfigError(f"could not infer GitHub repository from origin remote: {remote_url}")


def _harness_dir_for(worktree_dir: Path) -> Path:
    """Return the per-trial harness directory outside the solution worktree."""
    return worktree_dir.parent / ".duobench-harness"


def _install_origin_only_push_guard(worktree_dir: Path) -> Path:
    hooks_dir = _harness_dir_for(worktree_dir) / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook = hooks_dir / "pre-push"
    hook.write_text(
        """#!/bin/sh
remote_name="$1"
remote_url="$2"

if [ "$remote_name" != "origin" ]; then
  echo "duobench: refusing to push to '$remote_name' ($remote_url); push implementer PRs to origin only" >&2
  exit 1
fi
""",
        encoding="utf-8",
    )
    hook.chmod(0o755)
    _git(["config", "--worktree", "core.hooksPath", str(hooks_dir)], worktree_dir)
    return hooks_dir


# PATH-prepended wrappers installed outside the implementer worktree. They take
# precedence over system git/gh for bare command names; the agent could still
# call absolute paths, so they are defense-in-depth alongside prompt guidance
# and the upstream-remote removal below, not a hard sandbox.
_GIT_WRAPPER_BODY = """#!/bin/sh
# duobench local-commit safety wrapper for `git`. Blocks `git push` so the
# implementer cannot publish branches; all other git commands pass through.
# Set DUOBENCH_BLOCK_GIT_PUSH=0 to disable (e.g. in PR submission mode).
if [ "${DUOBENCH_BLOCK_GIT_PUSH:-1}" = "1" ]; then
  for arg in "$@"; do
    case "$arg" in
      push)
        echo "duobench: 'git push' is disabled in local-commit benchmark mode (set DUOBENCH_BLOCK_GIT_PUSH=0 to override)" >&2
        exit 1
        ;;
    esac
  done
fi
exec "__DUOBENCH_REAL_GIT__" "$@"
"""

_GH_WRAPPER_BODY = """#!/bin/sh
# duobench local-commit safety wrapper for `gh`. Blocks `gh pr create|edit|...`
# (anything that opens or mutates a pull request) so the implementer cannot
# publish PRs. Read-only `gh issue view` / `gh pr view` remain available.
# Set DUOBENCH_BLOCK_GH_PR=0 to disable (e.g. in PR submission mode).
if [ "${DUOBENCH_BLOCK_GH_PR:-1}" = "1" ]; then
  # Find the first non-flag positional argument: that's the gh subcommand.
  subcommand=""
  for arg in "$@"; do
    case "$arg" in
      -*) continue ;;
      *) subcommand="$arg"; break ;;
    esac
  done
  if [ "$subcommand" = "pr" ]; then
    # Find the first non-flag positional argument after `pr`: that's the pr verb.
    next=""
    saw_pr=0
    for arg in "$@"; do
      if [ $saw_pr -eq 0 ]; then
        if [ "$arg" = "pr" ] || [ "$arg" = "-h" ] || [ "$arg" = "--help" ]; then
          if [ "$arg" = "pr" ]; then saw_pr=1; fi
          continue
        fi
      else
        case "$arg" in
          -*) continue ;;
          *) next="$arg"; break ;;
        esac
      fi
    done
    case "$next" in
      create|edit|close|reopen|merge|ready|review|comment|lock|unlock|delete-branch|update-branch)
        echo "duobench: 'gh pr $next' is disabled in local-commit benchmark mode (set DUOBENCH_BLOCK_GH_PR=0 to override)" >&2
        exit 1
        ;;
    esac
  fi
fi
exec "__DUOBENCH_REAL_GH__" "$@"
"""


def _install_local_commit_safety(worktree_dir: Path) -> Path:
    """Install per-trial `git`/`gh` wrappers outside the solution worktree.

    Returns the bin directory path; the harness prepends it to PATH for the
    implementer Pi subprocess. Keeping these files outside ``worktree_dir``
    prevents benchmark infrastructure from being accidentally committed and
    judged as part of the candidate solution.
    """
    bin_dir = _harness_dir_for(worktree_dir) / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    git_bin = shutil.which("git") or "git"
    gh_bin = shutil.which("gh") or "gh"
    wrappers = (
        ("git", _GIT_WRAPPER_BODY.replace("__DUOBENCH_REAL_GIT__", git_bin)),
        ("gh", _GH_WRAPPER_BODY.replace("__DUOBENCH_REAL_GH__", gh_bin)),
    )
    for name, body in wrappers:
        path = bin_dir / name
        path.write_text(body, encoding="utf-8")
        path.chmod(0o755)
    return bin_dir


def _remove_upstream_remote(worktree_dir: Path) -> None:
    """Best-effort removal of the `upstream` remote so the agent can't push to it."""
    try:
        _git(["remote", "remove", "upstream"], worktree_dir, timeout=15.0)
    except ConfigError:
        pass


def prepare_worktree(
    repo_dir: Path,
    worktree_dir: Path,
    *,
    branch: str,
    submission_mode: str = "local_commit",
) -> Path:
    """Create an isolated git worktree for one implementer trial.

    In ``local_commit`` mode this installs PATH-prepended git/gh safety
    wrappers outside the worktree, removes the ``upstream`` remote, and keeps
    the origin-only pre-push hook outside the worktree. In ``pr`` mode only the
    pre-push hook is installed.
    """
    _git(["rev-parse", "--show-toplevel"], repo_dir)
    worktree_dir.parent.mkdir(parents=True, exist_ok=True)
    if worktree_dir.exists():
        shutil.rmtree(worktree_dir)
    # Prune any stale worktree registration left by a crashed/removed run so
    # `git worktree add -B` does not fail with "already registered".
    try:
        _git(["worktree", "prune"], repo_dir, timeout=30.0)
    except ConfigError:
        pass
    _git(["worktree", "add", "-B", branch, str(worktree_dir), "HEAD"], repo_dir, timeout=120.0)
    origin_repo = _origin_repo_slug(_git(["remote", "get-url", "origin"], worktree_dir))
    _gh(["repo", "set-default", origin_repo], worktree_dir)
    _install_origin_only_push_guard(worktree_dir)
    if submission_mode == "local_commit":
        _install_local_commit_safety(worktree_dir)
        _remove_upstream_remote(worktree_dir)
    return worktree_dir


def _pi_session_name(run_label: str, role: str, model_key: str, *, trial: int, condition_id: str | None = None) -> str:
    parts = ["duobench", run_label, role]
    if condition_id:
        parts.append(condition_id)
    parts += [model_key, f"trial-{trial}"]
    return " ".join(parts)


# --------------------------------------------------------------------------- #
# Commit artifact capture
# --------------------------------------------------------------------------- #


def _capture_commit_artifacts(
    worktree_dir: Path,
    commit_sha: str,
    *,
    trial_dir: Path | None = None,
) -> dict:
    """Record a local commit's metadata, diff, and worktree cleanliness.

    JSON-serializable; written to ``<trial_dir>/commit.json`` when ``trial_dir``
    is given. Errors are recorded in ``notes`` but never raise.
    """
    artifact: dict = {
        "commit_sha": commit_sha,
        "worktree": str(worktree_dir),
        "diff": "",
        "stat": "",
        "worktree_clean": True,
        "uncommitted_files": [],
        "branch": "",
        "notes": [],
    }
    if not commit_sha or not worktree_dir.exists():
        artifact["notes"].append("missing commit_sha or worktree dir; nothing captured")
        return artifact

    try:
        artifact["branch"] = _git(["branch", "--show-current"], worktree_dir, timeout=15.0)
    except ConfigError as e:
        artifact["notes"].append(f"branch detection failed: {e}")
    try:
        status = _git(["status", "--porcelain"], worktree_dir, timeout=15.0)
        artifact["worktree_clean"] = status.strip() == ""
        artifact["uncommitted_files"] = [line for line in status.splitlines() if line.strip()]
    except ConfigError as e:
        artifact["notes"].append(f"worktree status failed: {e}")
        artifact["worktree_clean"] = False

    try:
        stat = _git(["show", "--stat", "--no-color", "--format=", commit_sha], worktree_dir, timeout=30.0)
        if len(stat) > _MAX_STAT_CHARS:
            stat = stat[:_MAX_STAT_CHARS] + f"\n[...stat truncated at {_MAX_STAT_CHARS} chars...]\n"
        artifact["stat"] = stat
    except ConfigError as e:
        artifact["notes"].append(f"git show --stat failed: {e}")

    try:
        diff = _git(["show", "--no-color", "--format=", commit_sha], worktree_dir, timeout=60.0)
        if len(diff) > _MAX_DIFF_CHARS:
            diff = diff[:_MAX_DIFF_CHARS] + f"\n[...diff truncated at {_MAX_DIFF_CHARS} chars...]\n"
        artifact["diff"] = diff
    except ConfigError as e:
        artifact["notes"].append(f"git show diff failed: {e}")

    if trial_dir is not None:
        _write_json_atomic(trial_dir / "commit.json", artifact)
    return artifact


# --------------------------------------------------------------------------- #
# Small JSON / transcript IO
# --------------------------------------------------------------------------- #


def _write_json_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, default=str))
    os.replace(tmp, path)


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _transcript_cost(path: Path) -> tuple[float, str]:
    """Return (usd, cost_source) from a written transcript, best-effort."""
    data = _read_json(path)
    usd = float((data.get("stats") or {}).get("usd", 0.0) or 0.0)
    turns = data.get("turns") or []
    source = "unknown"
    if turns:
        source = (turns[-1].get("cost") or {}).get("source", "unknown")
    return usd, source


def _copy_plan_artifacts(plan_source_dir: Path, plan_text: str, trial_dir: Path) -> None:
    trial_dir.mkdir(parents=True, exist_ok=True)
    for name in ("plan.md", "planner-transcript.json", "planner-events.jsonl"):
        src = plan_source_dir / name
        if src.exists():
            shutil.copy(src, trial_dir / name)
    if not (trial_dir / "plan.md").exists():
        (trial_dir / "plan.md").write_text(plan_text)


# --------------------------------------------------------------------------- #
# Per-unit phase runners
# --------------------------------------------------------------------------- #


@dataclass
class PhaseOutcome:
    """What a single phase job produced — wrapped into result.json by the script."""

    status: str                       # "complete" | "timeout" | "stalled" | "stopped" | "error"
    cost_usd: float = 0.0
    cost_source: str = "unknown"
    artifact: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def plan_one(
    cfg: Config,
    prompts: dict[str, str],
    planner_key: str,
    *,
    out_dir: Path,
    trial: int,
    timeout: float,
    save_pi_sessions: bool = False,
    run_label: str = "run",
    workspace_dir: Path | None = None,
) -> PhaseOutcome:
    """Run the planner for one (planner, trial). Writes plan.md + shared-plan.json."""
    planner = cfg.model(planner_key)
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_text, pc, duration = run_plan_phase(
        planner,
        _format_prompt_template(prompts["architect"], issue_url=_issue_url_from(prompts)),
        out_dir,
        workspace_dir=workspace_dir or Path.cwd(),
        timeout=timeout,
        pin_temperature=True,
        thinking_level=planner.thinking_level,
        persist_pi_session=save_pi_sessions,
        session_name=_pi_session_name(run_label, "planner", planner_key, trial=trial),
        ui=None,
    )
    _write_json_atomic(out_dir / "shared-plan.json", {
        "planner": planner_key,
        "trial": trial,
        "cost_usd": round(pc.usd, 6),
        "cost_source": pc.source,
        "duration_s": round(duration, 2),
        "plan_dir": str(out_dir),
    })
    return PhaseOutcome(
        status="complete",
        cost_usd=round(pc.usd, 6),
        cost_source=pc.source,
        artifact={"plan_path": str(out_dir / "plan.md"), "duration_s": round(duration, 2)},
    )


def implement_one(
    cfg: Config,
    prompts: dict[str, str],
    *,
    planner_key: str,
    implementer_key: str,
    condition_id: str,
    plan_path: Path,
    out_dir: Path,
    trial: int,
    impl_timeout: float,
    plan_timeout: float = 600.0,
    judge_timeout: float = 300.0,
    submission_mode: str = "local_commit",
    save_pi_sessions: bool = False,
    run_label: str = "run",
    repo_dir: Path | None = None,
) -> PhaseOutcome:
    """Run the implementer for one condition×trial in an isolated worktree.

    Writes the worktree, implementer transcript, commit.json, verify.json, and
    trial.json (with dimensions zeroed — judging fills them via assemble_results).
    """
    repo_dir = repo_dir or Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)
    cond = Condition(id=condition_id, planner=planner_key, implementer=implementer_key)
    benchmark = make_benchmark_fingerprint(
        cfg, cond, prompts,
        dry_run=False,
        plan_timeout=plan_timeout,
        impl_timeout=impl_timeout,
        judge_timeout=judge_timeout,
    )
    implementer = cfg.model(implementer_key)

    # plan handoff: copy artifacts into the trial dir + recover plan cost
    plan_path = Path(plan_path)
    plan_text = plan_path.read_text() if plan_path.exists() else ""
    plan_meta = _read_json(plan_path.parent / "shared-plan.json")
    plan_cost = float(plan_meta.get("cost_usd", 0.0) or 0.0)
    plan_source = plan_meta.get("cost_source", "unknown")
    plan_duration = float(plan_meta.get("duration_s", 0.0) or 0.0)
    _copy_plan_artifacts(plan_path.parent, plan_text, out_dir)

    build_dir = out_dir / "worktree"
    branch = _safe_path_part(f"duobench/{run_label}/{condition_id}/trial-{trial}")
    worktree_dir = prepare_worktree(repo_dir, build_dir, branch=branch, submission_mode=submission_mode)
    local_bin_dir = _harness_dir_for(worktree_dir) / "bin"
    extra_path = local_bin_dir if local_bin_dir.is_dir() else None

    impl = run_impl_phase(
        implementer,
        _format_prompt_template(prompts["implement"], issue_url=_issue_url_from(prompts), plan=plan_text),
        plan_text,
        worktree_dir,
        timeout=impl_timeout,
        pin_temperature=True,
        thinking_level=implementer.thinking_level,
        persist_pi_session=save_pi_sessions,
        session_name=_pi_session_name(run_label, "implementer", implementer_key, trial=trial, condition_id=condition_id),
        submission_mode=submission_mode,
        extra_path=extra_path,
        ui=None,
    )
    commit_sha = impl.commit_sha
    pr_id = impl.pr_id

    # capture artifact + verify.json
    if submission_mode == "local_commit":
        commit_artifact = _capture_commit_artifacts(worktree_dir, commit_sha, trial_dir=out_dir)
        if not commit_artifact.get("worktree_clean"):
            commit_artifact.setdefault("notes", []).append("worktree is dirty beyond the recorded commit")
        verify_payload = {
            "submission_mode": "local_commit",
            "commit_sha": commit_sha,
            "worktree": str(worktree_dir),
            "worktree_clean": commit_artifact.get("worktree_clean"),
            "uncommitted_files": commit_artifact.get("uncommitted_files", []),
            "branch": commit_artifact.get("branch", ""),
            "commit": commit_artifact,
            "notes": [
                "Local-commit benchmark mode: implementer produces a local commit; "
                "judge evaluates the commit, diff, and worktree state."
            ],
        }
    else:
        verify_payload = {
            "submission_mode": "pr",
            "pr_id": pr_id,
            "worktree": str(worktree_dir),
            "notes": ["Implementation agent is responsible for tests, commit, push, and PR creation."],
        }
    _write_json_atomic(out_dir / "verify.json", verify_payload)

    record = TrialRecord(
        condition_id=condition_id,
        planner=planner_key,
        implementer=implementer_key,
        trial=trial,
        cost_usd=round(plan_cost + impl.cost.usd, 6),
        dimensions={d: 0.0 for d in DIMENSIONS},   # filled by assemble_results after judging
        per_judge={},
        impl_status=impl.status,
        cost_source=_merge_cost_source(plan_source, impl.cost.source),
        plan_duration_s=round(plan_duration, 2),
        impl_duration_s=round(impl.duration_s, 2),
    )
    record_meta = {
        "build_dir": str(worktree_dir),
        "pr_id": pr_id,
        "commit_sha": commit_sha,
        "smoke_summary": json.dumps(verify_payload, indent=2),
        "screenshots": [],
        "submission_mode": submission_mode,
    }
    artifacts = {
        "plan": {
            "shared": True,
            "planner": planner_key,
            "trial": trial,
            "source_dir": str(plan_path.parent),
            "cost_usd": round(plan_cost, 6),
        },
        "submission_mode": submission_mode,
    }
    if submission_mode == "local_commit":
        artifacts["commit"] = {"sha": commit_sha, "worktree": str(worktree_dir)}
    else:
        artifacts["pr"] = {"id": pr_id}
    _write_json_atomic(out_dir / "trial.json", {
        "benchmark": benchmark.to_dict(),
        "artifacts": artifacts,
        "record": record.__dict__,
        "meta": record_meta,
    })

    return PhaseOutcome(
        status=impl.status,
        cost_usd=round(impl.cost.usd, 6),
        cost_source=impl.cost.source,
        artifact={
            "commit_sha": commit_sha,
            "pr_id": pr_id,
            "impl_status": impl.status,
            "build_dir": str(worktree_dir),
        },
        notes=list(impl.notes),
    )


def judge_one(
    cfg: Config,
    prompts: dict[str, str],
    *,
    judge_key: str,
    build_dir: Path,
    out_dir: Path,
    condition_id: str,
    trial: int,
    issue_url: str = "",
    commit_sha: str = "",
    pr_id: str = "",
    timeout: float = 300.0,
    save_pi_sessions: bool = False,
    run_label: str = "run",
) -> PhaseOutcome:
    """Run one judge over one build. Writes judge-transcripts/<judge>.json."""
    out_dir.mkdir(parents=True, exist_ok=True)
    build_dir = Path(build_dir)
    source = collect_source(build_dir)
    verify_path = out_dir / "verify.json"
    smoke_summary = verify_path.read_text() if verify_path.exists() else "{}"
    plan_path = out_dir / "plan.md"
    plan = plan_path.read_text() if plan_path.exists() else ""
    transcript_path = out_dir / "judge-transcripts" / f"{judge_key}.json"

    score = judge_build(
        cfg.model(judge_key),
        judge_key,
        prompts["judge"],
        source,
        smoke_summary,
        [],
        issue_url=issue_url or _issue_url_from(prompts),
        pr_id=pr_id,
        commit_sha=commit_sha,
        plan=plan,
        timeout=timeout,
        transcript_path=transcript_path,
        persist_pi_session=save_pi_sessions,
        session_name=_pi_session_name(run_label, "judge", judge_key, trial=trial, condition_id=condition_id),
        ui=None,
    )
    cost_usd, cost_source = _transcript_cost(transcript_path)
    return PhaseOutcome(
        status="error" if score.error else "complete",
        cost_usd=cost_usd,
        cost_source=cost_source,
        artifact={"judge_key": judge_key, "scores": score.to_dict()},
        notes=[score.error] if score.error else [],
    )


# --------------------------------------------------------------------------- #
# Results assembly (pure — no model calls)
# --------------------------------------------------------------------------- #


def _trial_record_from_dict(rec: dict) -> TrialRecord:
    return TrialRecord(
        condition_id=rec.get("condition_id", ""),
        planner=rec.get("planner", ""),
        implementer=rec.get("implementer", ""),
        trial=int(rec.get("trial", 0)),
        cost_usd=float(rec.get("cost_usd", 0.0) or 0.0),
        dimensions=dict(rec.get("dimensions", {}) or {}),
        per_judge=dict(rec.get("per_judge", {}) or {}),
        impl_status=rec.get("impl_status", "complete"),
        cost_source=rec.get("cost_source", "unknown"),
        plan_duration_s=float(rec.get("plan_duration_s", 0.0) or 0.0),
        impl_duration_s=float(rec.get("impl_duration_s", 0.0) or 0.0),
    )


def _score_from_judge_sentinel(path: Path) -> JudgeScore | None:
    data = _read_json(path)
    scores = (data.get("artifact") or {}).get("scores")
    if not isinstance(scores, dict):
        return None
    return JudgeScore(
        judge=scores.get("judge", ""),
        task_completion=int(scores.get("task_completion", 0) or 0),
        correctness=int(scores.get("correctness", 0) or 0),
        code_quality=int(scores.get("code_quality", 0) or 0),
        verification=int(scores.get("verification", 0) or 0),
        notes=scores.get("notes", "") or "",
        error=scores.get("error"),
    )


def _score_from_transcript(path: Path, judge_key: str) -> JudgeScore | None:
    from duobench.judge import _parse_scores  # local import: internal helper

    data = _read_json(path)
    turns = data.get("turns") or []
    if not turns:
        return None
    text = turns[-1].get("assistant_text", "") or ""
    score = _parse_scores(text, judge_key)
    # Honor a recorded error status from the transcript.
    if data.get("status") == "error" and score.error is None:
        score.error = "; ".join(data.get("notes", []) or []) or "judge transcript marked error"
    return score


def _collect_trial_scores(trial_dir: Path, judges: list[str] | None) -> list[JudgeScore]:
    """Gather judge scores for one trial: prefer per-judge sentinels, fall back to transcripts."""
    results_dir = trial_dir / "results"
    transcripts_dir = trial_dir / "judge-transcripts"
    keys = list(judges) if judges else []
    if not keys:
        seen: list[str] = []
        for p in sorted(results_dir.glob("judge-*.json")) if results_dir.is_dir() else []:
            seen.append(p.stem[len("judge-"):])
        for p in sorted(transcripts_dir.glob("*.json")) if transcripts_dir.is_dir() else []:
            if p.stem not in seen:
                seen.append(p.stem)
        keys = seen

    scores: list[JudgeScore] = []
    for key in keys:
        score = None
        sentinel = results_dir / f"judge-{key}.json"
        if sentinel.is_file():
            score = _score_from_judge_sentinel(sentinel)
        if score is None:
            transcript = transcripts_dir / f"{key}.json"
            if transcript.is_file():
                score = _score_from_transcript(transcript, key)
        if score is not None:
            scores.append(score)
    return scores


def _run_metadata(run_dir: Path) -> dict:
    """Best-effort run metadata copied from the agent-authored run_state.json."""
    state = _read_json(run_dir / "run_state.json")
    keys = (
        "issue",
        "issue_created_at",
        "issue_selected_at",
        "base_commit_sha",
        "fix_commit_sha",
        "fix_pr_url",
        "target_repo",
        "target_repo_dir",
    )
    return {k: state[k] for k in keys if state.get(k)}


def assemble_results(run_dir: Path, judges: list[str] | None = None) -> dict:
    """Fold every conditions/*/trial-*/trial.json into results.json (no model calls).

    For each trial: collect judge scores (sentinels preferred), set the trial's
    averaged dimensions + per-judge map, and write them back into trial.json.
    Then aggregate across conditions and write results.json.
    """
    run_dir = Path(run_dir)
    trial_paths = sorted((run_dir / "conditions").glob("*/trial-*/trial.json"))
    records: list[TrialRecord] = []
    discovered_judges: list[str] = []

    for tp in trial_paths:
        trial = _read_json(tp)
        rec = _trial_record_from_dict(trial.get("record", {}))
        scores = _collect_trial_scores(tp.parent, judges)
        for s in scores:
            if s.judge and s.judge not in discovered_judges:
                discovered_judges.append(s.judge)
        rec.per_judge = {
            s.judge: {d: getattr(s, d) for d in DIMENSIONS} for s in scores if s.error is None
        }
        rec.dimensions = average_dimensions(scores)
        records.append(rec)
        # write scores back into trial.json (single post-judge writer)
        trial["record"] = rec.__dict__
        trial["judge_scores"] = [s.to_dict() for s in scores]
        _write_json_atomic(tp, trial)

    judge_list = list(judges) if judges else discovered_judges
    results = aggregate(records, judge_list)
    meta = _run_metadata(run_dir)
    if meta:
        results["run"] = meta
    _write_json_atomic(run_dir / "results.json", results)
    return results
