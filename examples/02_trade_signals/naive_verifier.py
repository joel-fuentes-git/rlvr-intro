"""Naive trade-signal verifier: forward 21-day excess return.

This is the verifier that *will* fail. The reward is honest — it really is
the next month's excess return — but the proxy is a lie. Excess return on
one stock over one month is dominated by noise. The model that maximizes it
is the model that learns to game it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

DECISION_RE = re.compile(r"\b(BUY|SELL|HOLD)\b", re.IGNORECASE)


@dataclass(frozen=True)
class MarketContext:
    ticker: str
    forward_excess_return: float  # already-computed forward 21-day excess return


def _extract_decision(completion: str) -> str | None:
    matches = DECISION_RE.findall(completion)
    return matches[-1].upper() if matches else None


def verifier(ctx: MarketContext, completion: str) -> dict[str, float]:
    """Reward = signed forward excess return, capped to [-1, 1].

    BUY pays +ret, SELL pays -ret, HOLD pays 0. Naive but legitimate.
    The point of the example is that this verifier is *too noisy* and
    *too gameable* to drive useful learning.
    """
    decision = _extract_decision(completion)
    ret = ctx.forward_excess_return
    if decision == "BUY":
        raw = ret
    elif decision == "SELL":
        raw = -ret
    else:
        raw = 0.0
    reward = max(-1.0, min(1.0, raw * 10))  # scale so 10% move → 1.0 reward
    return {"reward": reward, "decision": decision or "NONE", "outcome": ret}
