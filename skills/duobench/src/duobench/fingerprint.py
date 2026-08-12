"""Deterministic benchmark fingerprints.

A fingerprint identifies the benchmark configuration that materially affects a trial so
future runs can detect compatible previous results. It includes prompt *content* hashes,
not just prompt filenames, so editing a prompt automatically changes the key.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from duobench.config import Condition, Config, Model


FINGERPRINT_SCHEMA_VERSION = 1
DEFAULT_TASK_ID = "minidesk"
DEFAULT_TASK_VERSION = 1


@dataclass(frozen=True)
class BenchmarkFingerprint:
    """Stable ID for one task × condition × execution config."""

    key: str
    label: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"key": self.key, "label": self.label, "payload": self.payload}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _model_payload(model: Model) -> dict[str, Any]:
    return {
        "key": model.key,
        "provider": model.provider,
        "model_id": model.model_id,
        "thinking_level": model.thinking_level,
    }


def make_benchmark_fingerprint(
    cfg: Config,
    cond: Condition,
    prompts: dict[str, str],
    *,
    dry_run: bool,
    plan_timeout: float,
    impl_timeout: float,
    judge_timeout: float,
    task_id: str = DEFAULT_TASK_ID,
    task_version: int = DEFAULT_TASK_VERSION,
    pin_temperature: bool = True,
) -> BenchmarkFingerprint:
    """Create a deterministic fingerprint for a condition under the current prompts.

    The returned ``key`` is a full SHA-256 hash of the canonical payload. Multiple trials
    of the same configuration intentionally share this key; they are separate stochastic
    samples of the same benchmark unit.
    """

    planner = cfg.model(cond.planner)
    implementer = cfg.model(cond.implementer)
    prompt_hashes = {name: sha256_text(text) for name, text in sorted(prompts.items())}
    judge_payloads = [_model_payload(cfg.model(j)) for j in cfg.judges]

    payload: dict[str, Any] = {
        "schema_version": FINGERPRINT_SCHEMA_VERSION,
        "task": {"id": task_id, "version": task_version},
        "prompts": prompt_hashes,
        "condition": {
            "id": cond.id,
            "planner": _model_payload(planner),
            "implementer": _model_payload(implementer),
        },
        "judging": {"judges": judge_payloads},
        "execution": {
            "dry_run": dry_run,
            "pin_temperature": pin_temperature,
            "plan_timeout": plan_timeout,
            "impl_timeout": impl_timeout,
            "judge_timeout": judge_timeout,
        },
    }
    key = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    label = f"{task_id}-v{task_version}__{planner.key}-x-{implementer.key}__{key[:12]}"
    return BenchmarkFingerprint(key=key, label=label, payload=payload)
