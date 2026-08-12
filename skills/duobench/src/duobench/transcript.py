"""Transcript persistence and metrics for Pi sessions."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from duobench.config import Model
from duobench.cost import PhaseCost
from duobench.pi_rpc import TurnResult


@dataclass
class TranscriptTurn:
    kind: str
    prompt: str
    assistant_text: str
    messages: list[Any]
    usage: dict
    cost: dict
    started_at: float
    ended_at: float
    duration_s: float


@dataclass
class Transcript:
    phase: str
    model_key: str
    provider: str
    model_id: str
    turns: list[TranscriptTurn] = field(default_factory=list)
    status: str = "unknown"
    notes: list[str] = field(default_factory=list)
    pi_session: dict[str, Any] | None = None

    def add_turn(
        self,
        *,
        kind: str,
        prompt: str,
        result: TurnResult,
        cost: PhaseCost,
        started_at: float,
        ended_at: float,
    ) -> None:
        self.turns.append(
            TranscriptTurn(
                kind=kind,
                prompt=prompt,
                assistant_text=result.text,
                messages=result.raw_messages,
                usage={
                    "input_tokens": result.usage.input,
                    "output_tokens": result.usage.output,
                    "cache_read_tokens": result.usage.cache_read,
                    "cache_write_tokens": result.usage.cache_write,
                    "reported_usd": round(result.usage.reported_cost, 6),
                },
                cost=cost.to_dict(),
                started_at=started_at,
                ended_at=ended_at,
                duration_s=round(ended_at - started_at, 3),
            )
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["stats"] = transcript_stats(d)
        return d

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str))


def new_transcript(phase: str, model: Model) -> Transcript:
    return Transcript(
        phase=phase,
        model_key=model.key,
        provider=model.provider,
        model_id=model.model_id,
    )


def _content_blocks(message: dict) -> list[dict]:
    content = message.get("content")
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    return []


def _is_tool_block(block: dict) -> bool:
    btype = str(block.get("type", "")).lower()
    return "tool" in btype or "function" in btype


def transcript_stats(transcript: dict) -> dict:
    turns = transcript.get("turns", []) or []
    messages = [m for t in turns for m in (t.get("messages") or []) if isinstance(m, dict)]
    assistant_messages = [m for m in messages if m.get("role") == "assistant"]
    user_messages = [m for m in messages if m.get("role") == "user"]
    tool_blocks = [b for m in messages for b in _content_blocks(m) if _is_tool_block(b)]
    return {
        "turns": len(turns),
        "messages": len(messages),
        "assistant_messages": len(assistant_messages),
        "user_messages": len(user_messages),
        "tool_calls": len(tool_blocks),
        "duration_s": round(sum(float(t.get("duration_s", 0) or 0) for t in turns), 3),
        "input_tokens": sum(int((t.get("usage") or {}).get("input_tokens", 0) or 0) for t in turns),
        "output_tokens": sum(int((t.get("usage") or {}).get("output_tokens", 0) or 0) for t in turns),
        "cache_read_tokens": sum(int((t.get("usage") or {}).get("cache_read_tokens", 0) or 0) for t in turns),
        "cache_write_tokens": sum(int((t.get("usage") or {}).get("cache_write_tokens", 0) or 0) for t in turns),
        "usd": round(sum(float((t.get("cost") or {}).get("usd", 0) or 0) for t in turns), 6),
        "reported_usd": round(sum(float((t.get("cost") or {}).get("reported_usd", 0) or 0) for t in turns), 6),
    }
