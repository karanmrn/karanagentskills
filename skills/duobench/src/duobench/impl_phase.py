"""Implementation phase: a fresh implementer session completes the task from the plan.

The implementer never sees the planner's reasoning — only the user task and plan text.
Tools are enabled and the session CWD is the build dir, so the agent writes files there
directly.

No hard turn cap (per design): realistic looping behavior naturally inflates cost. The only
guardrail is a wall-clock timeout; a build that hits it is recorded as a `timeout`
failure-mode data point rather than crashing the suite. A bounded multi-turn loop nudges
the agent to keep working until it signals completion.

Two submission modes are supported:

* ``local_commit`` (default, see #11): the implementer creates a single local commit and
  returns the commit SHA. No push, no PR, no external side effects.
* ``pr`` (legacy): the implementer pushes a branch and opens a pull request, returning
  the PR id. Kept for backward compatibility with opt-in.
"""

from __future__ import annotations

import json
import subprocess
import time
import re
from dataclasses import dataclass, field
from pathlib import Path

from duobench.config import Model
from duobench.cost import PhaseCost, compute_cost
from duobench.pi_rpc import PiRpcError, PiRpcStalled, PiSession, TurnResult, Usage
from duobench.transcript import new_transcript

# Heuristic completion markers the implementer is asked to emit when done.
_PR_DONE_MARKERS = (
    "pr created", "pull request created", "opened pr", "created pr"
)
_COMMIT_DONE_MARKERS = (
    "commit created", "committed", "created commit", "made a commit",
)
_PR_CONTINUE_MSG = (
    "Continue working on the GitHub issue. If the PR has not been created yet, inspect the "
    "issue with gh, finish the code changes, run appropriate checks, commit, push, and open "
    "the PR. When the PR exists, reply with only the PR id."
)
_COMMIT_CONTINUE_MSG = (
    "Continue working on the GitHub issue. If you have not yet created a single local "
    "commit, finish the code changes, run appropriate checks, and create exactly one "
    "local commit. Do not push and do not open a PR. When the commit exists, reply with "
    "only the commit SHA."
)
_MAX_FOLLOW_UPS = 12  # safety bound on the nudge loop, not a per-agent turn cap
_FOLLOW_UP_IDLE_TIMEOUT = 120.0
_HEX_RE = re.compile(r"\b([0-9a-f]{7,40})\b")


@dataclass
class ImplResult:
    cost: PhaseCost
    turns: int
    status: str                      # "complete" | "timeout" | "stalled" | "stopped"
    final_text: str = ""
    pr_id: str = ""
    commit_sha: str = ""
    submission_mode: str = "local_commit"
    duration_s: float = 0.0
    notes: list[str] = field(default_factory=list)


def extract_pr_id(text: str) -> str:
    stripped = text.strip()
    url = re.search(r"https://github\.com/[^\s/]+/[^\s/]+/pull/(\d+)", stripped)
    if url:
        return url.group(1)
    number = re.search(r"(?:^|\s)#?(\d{1,10})(?:\s|$)", stripped)
    if number:
        return number.group(1)
    return ""


def extract_commit_sha(text: str) -> str:
    """Pull the most plausible commit SHA out of an implementer response.

    A full 40-char SHA anywhere in the text wins; otherwise the first short
    (7-39 char) hex token is returned as a fallback. Preferring the full SHA
    avoids latching onto an earlier short hex-looking token (e.g. a 7-digit
    issue number or timestamp) when the real SHA appears later in the reply.
    The parsed token is still validated against the repo by the caller (see
    ``_resolve_commit_sha``), so a non-SHA match cannot become the artifact.
    """
    short = ""
    for match in _HEX_RE.finditer(text):
        candidate = match.group(1)
        if len(candidate) == 40:
            return candidate
        if not short:
            short = candidate
    return short


def _looks_pr_done(text: str) -> bool:
    low = text.lower()
    return bool(extract_pr_id(text)) or any(m in low for m in _PR_DONE_MARKERS)


def _looks_commit_done(text: str) -> bool:
    return bool(extract_commit_sha(text))


def _git_stdout(args: list[str], cwd: Path, *, timeout: float = 15.0) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _detect_current_commit_sha(build_dir: Path, initial_head: str = "") -> str:
    """Return HEAD when the implementer created a new local commit."""
    head = _git_stdout(["rev-parse", "HEAD"], build_dir)
    if not head or (initial_head and head == initial_head):
        return ""
    return head


def _resolve_commit_sha(build_dir: Path, candidate: str, initial_head: str) -> str:
    """Confirm a parsed SHA against the repo, else fall back to a moved HEAD.

    ``candidate`` comes from :func:`extract_commit_sha`, which can match a stray
    hex-looking token (a 7+ digit issue number, a timestamp). We trust it only
    when it resolves to a real commit object, normalizing to the canonical
    40-char SHA. Otherwise we fall back to HEAD when the implementer actually
    advanced it past ``initial_head`` — so a mis-parse can no longer shadow the
    reliable HEAD detection (#11). Returns "" when nothing real is found.
    """
    if candidate:
        resolved = _git_stdout(
            ["rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}"], build_dir
        )
        if resolved:
            return resolved
    return _detect_current_commit_sha(build_dir, initial_head)


def _detect_existing_pr_id(build_dir: Path) -> str:
    """Best-effort reality check for a PR created by the current worktree branch."""
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=build_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15.0,
        )
        if branch.returncode != 0 or not branch.stdout.strip():
            return ""
        prs = subprocess.run(
            ["gh", "pr", "list", "--head", branch.stdout.strip(), "--json", "number,url", "--limit", "1"],
            cwd=build_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30.0,
        )
        if prs.returncode != 0:
            return ""
        data = json.loads(prs.stdout or "[]")
    except Exception:
        return ""
    if not isinstance(data, list) or not data:
        return ""
    number = data[0].get("number")
    return str(number) if number else extract_pr_id(str(data[0].get("url", "")))


def run_impl_phase(
    implementer: Model,
    implement_prompt_template: str,
    plan_text: str,
    build_dir: Path,
    *,
    timeout: float = 1800.0,
    pin_temperature: bool = False,
    thinking_level: str | None = None,
    persist_pi_session: bool = False,
    session_name: str | None = None,
    submission_mode: str = "local_commit",
    extra_path: str | Path | None = None,
    ui=None,
) -> ImplResult:
    """Complete the task in build_dir. Accumulates usage across the multi-turn loop.

    ``submission_mode`` selects the implementer's contract:

    * ``"local_commit"`` (default): looks for a commit SHA, nudges with a commit-focused
      continue message, and never asks the agent to push or open a PR.
    * ``"pr"``: legacy behavior — looks for a PR id, nudges with a PR-focused message.

    ``extra_path`` is prepended to PATH in the Pi subprocess environment so the
    harness can install safety wrappers that block ``git push`` and ``gh pr create``
    in local-commit mode (defense in depth, see #11).
    """
    if submission_mode not in {"local_commit", "pr"}:
        raise ValueError(f"unknown submission_mode: {submission_mode!r}")
    if submission_mode == "local_commit":
        looks_done = _looks_commit_done
        continue_msg = _COMMIT_CONTINUE_MSG
    else:
        looks_done = _looks_pr_done
        continue_msg = _PR_CONTINUE_MSG

    build_dir.mkdir(parents=True, exist_ok=True)
    prompt = implement_prompt_template.replace("{plan}", plan_text)
    initial_head = _git_stdout(["rev-parse", "HEAD"], build_dir)

    total = Usage()
    turns = 0
    status = "stopped"
    final_text = ""
    pr_id = ""
    commit_sha = ""
    notes: list[str] = []
    session_state: dict = {}

    transcript = new_transcript("implementer", implementer)
    if ui:
        ui.start_phase("Implementing", implementer.key)

    phase_started = time.monotonic()
    deadline = phase_started + timeout

    def remaining_timeout() -> float:
        return max(1.0, deadline - time.monotonic())

    def idle_timeout() -> float:
        return min(_FOLLOW_UP_IDLE_TIMEOUT, remaining_timeout())

    with PiSession(
        cwd=build_dir,
        enable_tools=True,
        event_callback=getattr(ui, "on_rpc_event", None),
        raw_events_path=build_dir.parent / "implementer-events.jsonl",
        persist_session=persist_pi_session,
        session_name=session_name,
        initial_model=implementer.model_id if not implementer.provider else None,
        extra_path=extra_path,
    ) as s:
        if implementer.provider:
            s.set_model(implementer.provider, implementer.model_id)
        if thinking_level is not None:
            s.set_thinking(thinking_level)
        elif pin_temperature and implementer.provider:
            s.set_thinking("off")

        def _do_turn(kind: str, message: str) -> TurnResult:
            """Drive one turn (initial prompt or follow-up) with idle-timeout retry."""
            if kind == "prompt":
                return s.prompt(message, timeout=remaining_timeout(), idle_timeout=idle_timeout())
            try:
                return s.follow_up(message, timeout=remaining_timeout(), idle_timeout=idle_timeout())
            except PiRpcStalled as e:
                notes.append(f"follow-up stalled: {e}; retrying as fresh prompt")
                return s.prompt(message, timeout=remaining_timeout(), idle_timeout=idle_timeout())

        try:
            started = time.time()
            result = _do_turn("prompt", prompt)
            ended = time.time()
            turns += 1
            total.add(result.usage)
            turn_cost = compute_cost(result.usage, implementer)
            transcript.add_turn(kind="prompt", prompt=prompt, result=result, cost=turn_cost, started_at=started, ended_at=ended)
            if ui:
                ui.add_turn_result(result.usage, turn_cost.usd, turn_cost.reported_usd)
            final_text = result.text
            if submission_mode == "local_commit":
                commit_sha = _resolve_commit_sha(build_dir, extract_commit_sha(result.text), initial_head)
            else:
                pr_id = extract_pr_id(result.text)
                if not pr_id and not looks_done(result.text):
                    pr_id = _detect_existing_pr_id(build_dir)
                    if pr_id:
                        notes.append("completion detected from existing PR rather than final response text")
            if looks_done(result.text) or (submission_mode == "local_commit" and commit_sha):
                status = "complete"
            elif pr_id:
                status = "complete"
            else:
                for _ in range(_MAX_FOLLOW_UPS):
                    if time.monotonic() >= deadline:
                        status = "timeout"
                        notes.append(f"implementation exceeded total wall-clock timeout of {timeout}s")
                        break
                    started = time.time()
                    try:
                        result = _do_turn("follow_up", continue_msg)
                    except PiRpcStalled as retry_error:
                        status = "stalled"
                        notes.append(f"fresh prompt after stalled follow-up also stalled: {retry_error}")
                        break
                    ended = time.time()
                    turns += 1
                    total.add(result.usage)
                    turn_cost = compute_cost(result.usage, implementer)
                    transcript.add_turn(kind="follow_up", prompt=continue_msg, result=result, cost=turn_cost, started_at=started, ended_at=ended)
                    if ui:
                        ui.add_turn_result(result.usage, turn_cost.usd, turn_cost.reported_usd)
                    final_text = result.text
                    if submission_mode == "local_commit":
                        commit_sha = (
                            _resolve_commit_sha(build_dir, extract_commit_sha(result.text), initial_head)
                            or commit_sha
                        )
                    else:
                        pr_id = extract_pr_id(result.text) or pr_id
                        if not pr_id and not looks_done(result.text):
                            pr_id = _detect_existing_pr_id(build_dir)
                            if pr_id:
                                notes.append("completion detected from existing PR rather than final response text")
                    if looks_done(result.text) or (submission_mode == "local_commit" and commit_sha):
                        status = "complete"
                        break
                    if pr_id:
                        status = "complete"
                        break
                else:
                    status = "stopped"
                    notes.append(f"hit max follow-ups ({_MAX_FOLLOW_UPS}) without completion signal")
        except PiRpcStalled as e:
            status = "stalled"
            notes.append(f"pi_rpc stalled: {e}")
        except PiRpcError as e:
            status = "timeout"
            notes.append(f"pi_rpc error/timeout: {e}")
        try:
            session_state = s.get_state()
        except Exception:
            session_state = {}

    if status == "complete":
        if submission_mode == "local_commit" and not commit_sha:
            notes.append("completion detected but no commit SHA could be parsed from the final response")
        if submission_mode == "pr" and not pr_id:
            notes.append("completion detected but no PR id could be parsed from the final response")

    transcript.status = status
    transcript.notes = notes
    transcript.pi_session = _session_metadata(session_state, session_name)
    transcript.write(build_dir.parent / "implementer-transcript.json")
    if ui:
        ui.end_phase(status)

    return ImplResult(
        cost=compute_cost(total, implementer),
        turns=turns,
        status=status,
        final_text=final_text,
        pr_id=pr_id,
        commit_sha=commit_sha,
        submission_mode=submission_mode,
        duration_s=time.monotonic() - phase_started,
        notes=notes,
    )


def _session_metadata(state: dict, requested_name: str | None) -> dict | None:
    if not state and not requested_name:
        return None
    return {
        "requested_name": requested_name,
        "name": state.get("sessionName") or requested_name,
        "session_file": state.get("sessionFile"),
        "session_id": state.get("sessionId"),
    }
