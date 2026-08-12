"""Plan phase: a planner model produces an architecture plan from the architect prompt.

Session-isolated from implementation. The plan text is the only handoff artifact. The
planner may inspect the local repository with read-only Pi tools, but it must not edit
files.
"""

from __future__ import annotations

import time
from pathlib import Path

from duobench.config import Model
from duobench.cost import PhaseCost, compute_cost
from duobench.pi_rpc import PiSession
from duobench.transcript import new_transcript


def run_plan_phase(
    planner: Model,
    architect_prompt: str,
    out_dir: Path,
    *,
    workspace_dir: Path | None = None,
    timeout: float = 600.0,
    pin_temperature: bool = False,
    thinking_level: str | None = None,
    persist_pi_session: bool = False,
    session_name: str | None = None,
    ui=None,
) -> tuple[str, PhaseCost, float]:
    """Run the planner; write plan.md to out_dir. Returns (plan_text, cost, duration_s)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    transcript = new_transcript("planner", planner)
    if ui:
        ui.start_phase("Planning", planner.key)
    with PiSession(
        cwd=workspace_dir or out_dir,
        enable_tools=True,
        allowed_tools=["read", "grep", "find", "ls", "bash"],
        event_callback=getattr(ui, "on_rpc_event", None),
        raw_events_path=out_dir / "planner-events.jsonl",
        persist_session=persist_pi_session,
        session_name=session_name,
        initial_model=planner.model_id if not planner.provider else None,
    ) as s:
        if planner.provider:
            s.set_model(planner.provider, planner.model_id)
        if thinking_level is not None:
            s.set_thinking(thinking_level)
        elif pin_temperature and planner.provider:
            s.set_thinking("off")
        started = time.time()
        result = s.prompt(architect_prompt, timeout=timeout)
        ended = time.time()
        try:
            session_state = s.get_state()
        except Exception:
            session_state = {}

    cost = compute_cost(result.usage, planner)
    transcript.add_turn(
        kind="prompt",
        prompt=architect_prompt,
        result=result,
        cost=cost,
        started_at=started,
        ended_at=ended,
    )
    transcript.status = "complete"
    transcript.pi_session = _session_metadata(session_state, session_name)
    transcript.write(out_dir / "planner-transcript.json")
    if ui:
        ui.add_turn_result(result.usage, cost.usd, cost.reported_usd)
        ui.end_phase("complete")

    plan_path = out_dir / "plan.md"
    plan_path.write_text(result.text)
    return result.text, cost, ended - started


def _session_metadata(state: dict, requested_name: str | None) -> dict | None:
    if not state and not requested_name:
        return None
    return {
        "requested_name": requested_name,
        "name": state.get("sessionName") or requested_name,
        "session_file": state.get("sessionFile"),
        "session_id": state.get("sessionId"),
    }
