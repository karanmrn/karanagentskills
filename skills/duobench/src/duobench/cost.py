"""Token → dollar cost.

Prefer Pi/provider reported cost when available. Fall back to optional configured pricing
from models.yaml/costs.yaml. Unknown pricing records zero configured cost.
"""

from __future__ import annotations

from dataclasses import dataclass

from duobench.config import Model
from duobench.pi_rpc import Usage


@dataclass(frozen=True)
class PhaseCost:
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    usd: float
    reported_usd: float = 0.0
    source: str = "unknown"

    def to_dict(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_read_tokens": self.cache_read_tokens,
            "cache_write_tokens": self.cache_write_tokens,
            "usd": round(self.usd, 6),
            "reported_usd": round(self.reported_usd, 6),
            "source": self.source,
        }


def compute_cost(usage: Usage, model: Model) -> PhaseCost:
    """Cost in USD, preferring Pi-reported cost over configured fallback pricing."""
    if usage.reported_cost > 0:
        usd = usage.reported_cost
        source = "pi_reported"
    elif model.pricing is not None:
        rate_in = model.pricing.input / 1_000_000
        rate_out = model.pricing.output / 1_000_000
        rate_cache_read = (model.pricing.cache_read if model.pricing.cache_read is not None else model.pricing.input) / 1_000_000
        rate_cache_write = (model.pricing.cache_write if model.pricing.cache_write is not None else model.pricing.input) / 1_000_000
        usd = (
            usage.input * rate_in
            + usage.output * rate_out
            + usage.cache_read * rate_cache_read
            + usage.cache_write * rate_cache_write
        )
        source = "configured"
    else:
        usd = 0.0
        source = "unknown"
    return PhaseCost(
        input_tokens=usage.input,
        output_tokens=usage.output,
        cache_read_tokens=usage.cache_read,
        cache_write_tokens=usage.cache_write,
        usd=usd,
        reported_usd=usage.reported_cost,
        source=source,
    )
