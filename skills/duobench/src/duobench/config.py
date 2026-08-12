"""Config loading + fail-fast validation for models.yaml and conditions.yaml."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import yaml

# The installed skill directory (skills/duobench/). Configs and prompts ship
# inside it, so defaults resolve here — never against the caller's cwd, which
# is the benchmark target repo.
SKILL_ROOT = Path(__file__).resolve().parents[2]


class ConfigError(Exception):
    """Raised when config is malformed or references unknown model keys."""


@dataclass(frozen=True)
class Pricing:
    input: float                # $/MTok
    output: float               # $/MTok
    cache_read: float | None = None   # $/MTok; defaults to input rate when omitted
    cache_write: float | None = None  # $/MTok; defaults to input rate when omitted


@dataclass(frozen=True)
class Model:
    key: str
    provider: str
    model_id: str
    pricing: Pricing | None = None
    thinking_level: str | None = None

    @property
    def spec(self) -> str:
        return self.model_id if not self.provider else self.key


@dataclass(frozen=True)
class Condition:
    id: str
    planner: str       # model key
    implementer: str   # model key


@dataclass(frozen=True)
class Config:
    models: dict[str, Model]
    judges: list[str]            # model keys
    conditions: list[Condition]

    costs: dict[str, Pricing] | None = None

    def model(self, key: str) -> Model:
        # The CLI accepts Pi-style specs with an optional `:thinking` suffix
        # (e.g. `kimi-coding/kimi-for-coding:high`). Split the suffix first,
        # then look up the registry; the registry is keyed by the spec form
        # the user originally wrote (full Pi spec OR short alias).
        spec_key, _, suffix = key.partition(":")
        cli_thinking = _validate_thinking(suffix) if suffix else None
        if spec_key in self.models:
            base = self.models[spec_key]
            if cli_thinking is not None and cli_thinking != base.thinking_level:
                return replace(base, key=key, thinking_level=cli_thinking)
            return base if key == spec_key else replace(base, key=key)
        # Fall back to interpreting the spec as `provider/model_id` (Pi's CLI form).
        # A bare spec with no slash is treated as model_id only, leaving the
        # provider empty so Pi can try to resolve it.
        provider, _, model_id = spec_key.partition("/")
        provider = provider if model_id else ""
        pricing = (self.costs or {}).get(key) or (self.costs or {}).get(spec_key)
        return Model(
            key=key,
            provider=provider,
            model_id=model_id or spec_key,
            pricing=pricing,
            thinking_level=cli_thinking,
        )


THINKING_LEVELS = {"off", "minimal", "low", "medium", "high", "xhigh"}


def _validate_thinking(value: str) -> str:
    """Return the thinking level from a `:suffix`, raising ConfigError if invalid."""
    level = value.strip().lower()
    if level not in THINKING_LEVELS:
        raise ConfigError(
            f"unknown thinking level {value!r}; expected one of {', '.join(sorted(THINKING_LEVELS))}"
        )
    return level


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ConfigError(msg)


def _read_config_text(path: str | Path | None, default_name: str) -> str:
    """Read an explicit config path, or the skill's bundled config when omitted."""
    if path is None:
        path = SKILL_ROOT / "config" / default_name
    path = Path(path)
    if path.is_file():
        return path.read_text()
    raise ConfigError(f"config not found: {path}")


def load_costs(costs_path: str | Path = "costs.yaml") -> dict[str, Pricing]:
    path = Path(costs_path)
    if not path.is_file():
        return {}
    raw = yaml.safe_load(path.read_text()) or {}
    raw_models = raw.get("models", raw)
    _require(isinstance(raw_models, dict), "costs.yaml must be a mapping or contain a 'models' mapping")
    costs: dict[str, Pricing] = {}
    for key, spec in raw_models.items():
        _require(isinstance(spec, dict), f"cost '{key}': entry must be a mapping")
        _require("input" in spec and "output" in spec, f"cost '{key}': missing input/output rates")
        costs[str(key)] = Pricing(
            input=float(spec["input"]),
            output=float(spec["output"]),
            cache_read=float(spec["cache_read"]) if "cache_read" in spec else None,
            cache_write=float(spec["cache_write"]) if "cache_write" in spec else None,
        )
    return costs


def load_config(
    models_path: str | Path | None = None,
    conditions_path: str | Path | None = None,
    costs_path: str | Path = "costs.yaml",
) -> Config:
    """Load and validate both config files. Fails fast with a clear error.

    When a path is omitted, the config bundled with the skill (under
    ``SKILL_ROOT/config/``) is used — the caller's cwd is never consulted.
    """
    models_raw = yaml.safe_load(_read_config_text(models_path, "models.yaml")) or {}
    conditions_raw = yaml.safe_load(_read_config_text(conditions_path, "conditions.yaml")) or {}
    costs = load_costs(costs_path)

    # --- models ---
    raw_models = models_raw.get("models")
    _require(isinstance(raw_models, dict) and raw_models, "models.yaml: 'models' must be a non-empty mapping")

    models: dict[str, Model] = {}
    for key, spec in raw_models.items():
        _require(isinstance(spec, dict), f"model '{key}': entry must be a mapping")
        for field in ("provider", "model_id", "pricing"):
            _require(field in spec, f"model '{key}': missing required field '{field}'")
        pricing = spec["pricing"]
        _require(
            isinstance(pricing, dict) and "input" in pricing and "output" in pricing,
            f"model '{key}': pricing must have 'input' and 'output'",
        )
        thinking_level = spec["thinking"] if "thinking" in spec else spec.get("thinking_level")
        if isinstance(thinking_level, bool):
            # YAML 1.1 parses unquoted `off` as False. Accept it because it is a
            # natural way to write Pi's thinking level in YAML.
            thinking_level = "off" if thinking_level is False else "on"
        if thinking_level is not None:
            thinking_level = str(thinking_level)
            _require(
                thinking_level in THINKING_LEVELS,
                f"model '{key}': thinking must be one of {', '.join(sorted(THINKING_LEVELS))}",
            )
        models[key] = Model(
            key=key,
            provider=str(spec["provider"]),
            model_id=str(spec["model_id"]),
            pricing=Pricing(
                input=float(pricing["input"]),
                output=float(pricing["output"]),
                cache_read=float(pricing["cache_read"]) if "cache_read" in pricing else None,
                cache_write=float(pricing["cache_write"]) if "cache_write" in pricing else None,
            ),
            thinking_level=thinking_level,
        )

    # --- judges ---
    judges = models_raw.get("judges")
    _require(isinstance(judges, list) and judges, "models.yaml: 'judges' must be a non-empty list")
    for j in judges:
        _require(j in models, f"judge '{j}' is not defined in models")

    # --- conditions ---
    raw_conditions = conditions_raw.get("conditions")
    _require(isinstance(raw_conditions, list) and raw_conditions, "conditions.yaml: 'conditions' must be a non-empty list")

    conditions: list[Condition] = []
    seen_ids: set[str] = set()
    for c in raw_conditions:
        _require(isinstance(c, dict), "each condition must be a mapping")
        for field in ("id", "planner", "implementer"):
            _require(field in c, f"condition {c!r}: missing required field '{field}'")
        cid = str(c["id"])
        _require(cid not in seen_ids, f"duplicate condition id: '{cid}'")
        seen_ids.add(cid)
        # planner/implementer accept either a registry key OR a direct Pi spec
        # (e.g. `kimi-coding/kimi-for-coding` or `kimi-coding/kimi-for-coding:high`).
        # Validate the thinking suffix here so typos fail fast.
        for role in ("planner", "implementer"):
            value = str(c[role])
            spec, _, suffix = value.partition(":")
            if spec not in models and "/" not in spec:
                raise ConfigError(
                    f"condition '{cid}': {role} '{value}' is not a known model key and "
                    f"has no provider prefix; register it in models.yaml or use the "
                    f"'provider/model_id' form"
                )
            if suffix:
                _validate_thinking(suffix)
        conditions.append(
            Condition(
                id=cid,
                planner=str(c["planner"]),
                implementer=str(c["implementer"]),
            )
        )

    return Config(models=models, judges=list(judges), conditions=conditions, costs=costs)
