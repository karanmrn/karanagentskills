"""Judge phase: a configurable panel scores every solution on task-agnostic dimensions.

Each judge model scores task_completion / correctness / code_quality / verification
(1-10) as strict JSON. Cost efficiency is NOT judged — it's computed objectively in
results aggregation.

Inputs per build:

* The GitHub issue URL.
* The planner's handoff plan.
* Either the implementer-returned PR id (legacy ``pr`` mode) or the commit SHA
  (``local_commit`` mode, the default since #11). In local-commit mode the judge
  inspects the local commit, its diff, and the worktree state instead of a PR.
* The full diff / `git show --stat` text and worktree cleanliness status when in
  local-commit mode.
* Automated harness metadata when available.

Judges use local git and ``gh`` (read-only) to inspect artifacts. They must not
modify files, commit, push, or open PRs.

Scores are averaged across the panel. Raw per-judge scores are kept so a judge×build
self-bias matrix can be plotted.
"""

from __future__ import annotations

import base64
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from duobench.config import Config, Model
from duobench.cost import compute_cost
from duobench.pi_rpc import PiRpcError, PiSession
from duobench.transcript import new_transcript

DIMENSIONS = ("task_completion", "correctness", "code_quality", "verification")
_MAX_SOURCE_CHARS = 120_000           # cap concatenated source to stay within context
_SOURCE_EXTS = {
    ".html", ".css", ".js", ".mjs", ".jsx", ".ts", ".tsx",
    ".py", ".go", ".rs", ".java", ".rb", ".php", ".sh",
    ".json", ".yaml", ".yml", ".toml", ".md",
}
_SKIP_DIRS = {"node_modules", ".git", "screenshots"}


@dataclass
class JudgeScore:
    judge: str                        # model key
    task_completion: int
    correctness: int
    code_quality: int
    verification: int
    notes: str = ""
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "judge": self.judge,
            "task_completion": self.task_completion,
            "correctness": self.correctness,
            "code_quality": self.code_quality,
            "verification": self.verification,
            "notes": self.notes,
            "error": self.error,
        }


def collect_source(build_dir: Path) -> str:
    parts: list[str] = []
    total = 0
    for path in sorted(build_dir.rglob("*")):
        if any(d in path.parts for d in _SKIP_DIRS):
            continue
        if not path.is_file() or path.suffix.lower() not in _SOURCE_EXTS:
            continue
        try:
            text = path.read_text(errors="replace")
        except Exception:
            continue
        rel = path.relative_to(build_dir)
        chunk = f"\n===== FILE: {rel} =====\n{text}\n"
        if total + len(chunk) > _MAX_SOURCE_CHARS:
            parts.append(f"\n[...source truncated at {_MAX_SOURCE_CHARS} chars...]\n")
            break
        parts.append(chunk)
        total += len(chunk)
    return "".join(parts) if parts else "[no source files found]"


def _encode_images(screenshots: list[str], limit: int = 5) -> list[dict]:
    imgs: list[dict] = []
    for sp in screenshots[:limit]:
        p = Path(sp)
        if not p.is_file():
            continue
        try:
            data = base64.b64encode(p.read_bytes()).decode()
            imgs.append({"type": "image", "data": data, "mimeType": "image/png"})
        except Exception:
            continue
    return imgs


def _parse_scores(text: str, judge_key: str) -> JudgeScore:
    # Extract the first JSON object from the response.
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return JudgeScore(judge_key, 0, 0, 0, 0, error=f"no JSON in response: {text[:120]}")
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return JudgeScore(judge_key, 0, 0, 0, 0, error=f"bad JSON: {e}")

    def clamp(v) -> int:
        try:
            return max(1, min(10, int(round(float(v)))))
        except Exception:
            return 0

    return JudgeScore(
        judge=judge_key,
        task_completion=clamp(obj.get("task_completion")),
        correctness=clamp(obj.get("correctness")),
        code_quality=clamp(obj.get("code_quality")),
        verification=clamp(obj.get("verification")),
        notes=str(obj.get("notes", ""))[:500],
    )


def judge_build(
    judge_model: Model,
    judge_key: str,
    judge_prompt_template: str,
    source: str,
    smoke_summary: str,
    screenshots: list[str],
    *,
    issue_url: str,
    pr_id: str = "",
    commit_sha: str = "",
    plan: str = "",
    timeout: float = 300.0,
    transcript_path: Path | None = None,
    persist_pi_session: bool = False,
    session_name: str | None = None,
    ui=None,
) -> JudgeScore:
    """Score one build. Either ``pr_id`` (PR mode) or ``commit_sha`` (local-commit mode)
    must be provided so the judge prompt has a concrete artifact to inspect. When the
    prompt template uses ``{commit_sha}`` (local-commit variant) the commit SHA is
    substituted; when it uses ``{pr_id}`` (PR variant) the PR id is substituted. Both
    placeholders are left as-is for whichever one the prompt does not use."""
    prompt = (
        judge_prompt_template
        .replace("{issue_url}", issue_url)
        .replace("{pr_id}", pr_id)
        .replace("{commit_sha}", commit_sha)
        .replace("{plan}", plan)
        .replace("{smoke_results}", smoke_summary)
    )
    images = _encode_images(screenshots)
    transcript = new_transcript("judge", judge_model)
    session_state: dict = {}
    if ui:
        ui.start_phase("Judging", judge_key)
    raw_events_path = transcript_path.with_suffix(".events.jsonl") if transcript_path else None
    with PiSession(
        cwd=Path.cwd(),
        enable_tools=True,
        allowed_tools=["read", "grep", "find", "ls", "bash"],
        event_callback=getattr(ui, "on_rpc_event", None),
        raw_events_path=raw_events_path,
        persist_session=persist_pi_session,
        session_name=session_name,
        initial_model=judge_model.model_id if not judge_model.provider else None,
    ) as s:
        if judge_model.provider:
            s.set_model(judge_model.provider, judge_model.model_id)
        if judge_model.thinking_level is not None:
            s.set_thinking(judge_model.thinking_level)
        elif judge_model.provider:
            s.set_thinking("off")  # determinism best-effort fallback for legacy config models
        try:
            # Try with images first; fall back to text-only if the build/model rejects it.
            try:
                s._send({"type": "prompt", "message": prompt, "images": images} if images
                         else {"type": "prompt", "message": prompt})
                s._await_response("prompt", timeout=15.0)
                started = time.time()
                result = s._collect_until_agent_end(timeout=timeout)
                ended = time.time()
            except PiRpcError:
                started = time.time()
                result = s.prompt(prompt, timeout=timeout)
                ended = time.time()
        except PiRpcError as e:
            transcript.status = "error"
            transcript.notes = [str(e)]
            try:
                session_state = s.get_state()
            except Exception:
                session_state = {}
            transcript.pi_session = _session_metadata(session_state, session_name)
            if transcript_path:
                transcript.write(transcript_path)
            if ui:
                ui.end_phase("error")
            return JudgeScore(judge_key, 0, 0, 0, 0, error=str(e))
        try:
            session_state = s.get_state()
        except Exception:
            session_state = {}
    cost = compute_cost(result.usage, judge_model)
    transcript.add_turn(kind="prompt", prompt=prompt, result=result, cost=cost, started_at=started, ended_at=ended)
    if ui:
        ui.add_turn_result(result.usage, cost.usd, cost.reported_usd)
    score = _parse_scores(result.text, judge_key)
    transcript.status = "complete" if score.error is None else "error"
    if score.error:
        transcript.notes = [score.error]
    transcript.pi_session = _session_metadata(session_state, session_name)
    if transcript_path:
        transcript.write(transcript_path)
    if ui:
        ui.end_phase(transcript.status)
    return score


def judge_panel(
    cfg: Config,
    judge_prompt_template: str,
    build_dir: Path,
    smoke_summary: str,
    screenshots: list[str],
    *,
    issue_url: str = "",
    pr_id: str = "",
    commit_sha: str = "",
    plan: str = "",
    timeout: float = 300.0,
    transcripts_dir: Path | None = None,
    persist_pi_session: bool = False,
    session_name_prefix: str | None = None,
    ui=None,
) -> list[JudgeScore]:
    """Run every configured judge over one build.

    Pass ``pr_id`` for PR-mode trials or ``commit_sha`` for local-commit trials
    (see #11). The judge prompt's ``{pr_id}``/``{commit_sha}`` placeholder
    decides which one the model actually inspects.
    """
    source = collect_source(build_dir)
    scores: list[JudgeScore] = []
    for judge_key in cfg.judges:
        model = cfg.model(judge_key)
        transcript_path = transcripts_dir / f"{judge_key}.json" if transcripts_dir else None
        session_name = f"{session_name_prefix} judge={judge_key}" if session_name_prefix else None
        scores.append(
            judge_build(
                model, judge_key, judge_prompt_template,
                source, smoke_summary, screenshots,
                issue_url=issue_url,
                pr_id=pr_id,
                commit_sha=commit_sha,
                plan=plan,
                timeout=timeout,
                transcript_path=transcript_path,
                persist_pi_session=persist_pi_session,
                session_name=session_name,
                ui=ui,
            )
        )
    return scores


def _session_metadata(state: dict, requested_name: str | None) -> dict | None:
    if not state and not requested_name:
        return None
    return {
        "requested_name": requested_name,
        "name": state.get("sessionName") or requested_name,
        "session_file": state.get("sessionFile"),
        "session_id": state.get("sessionId"),
    }


def average_dimensions(scores: list[JudgeScore]) -> dict[str, float]:
    """Average each dimension across judges that returned valid (non-error) scores."""
    valid = [s for s in scores if s.error is None]
    if not valid:
        return {d: 0.0 for d in DIMENSIONS}
    return {
        d: round(sum(getattr(s, d) for s in valid) / len(valid), 3)
        for d in DIMENSIONS
    }
