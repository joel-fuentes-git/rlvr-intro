"""Triangular verifier for trade signals (Trade-R1 inspired).

Three sub-verifiers — evidence, reasoning, outcome — combine via geometric
mean. A reward-hacking strategy fails (1) or (2) and the geometric mean
collapses, regardless of (3).

The sub-verifiers below are deliberately rule-based for transparency. In a
real system, the reasoning verifier could be a constrained LLM-as-judge.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

DECISION_RE = re.compile(r"\b(BUY|SELL|HOLD)\b", re.IGNORECASE)


def _extract_decision(completion: str) -> str | None:
    matches = DECISION_RE.findall(completion)
    return matches[-1].upper() if matches else None


@dataclass(frozen=True)
class TradeContext:
    ticker: str
    forward_excess_return: float
    # Numbers / ratios the model is allowed to cite. The evidence verifier
    # checks that any cited number rounds to one of these.
    cited_facts: dict[str, float] = field(default_factory=dict)


_NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
_CONNECTIVES = (
    "because", "since", "therefore", "implies", "suggests", "given that",
    "due to", "as a result",
)


def evidence_verifier(ctx: TradeContext, completion: str) -> float:
    """Fraction of cited numbers that match the allowed facts within 1%."""
    nums = [float(m) for m in _NUM_RE.findall(completion)]
    if not nums:
        return 0.0
    allowed = list(ctx.cited_facts.values())
    if not allowed:
        return 0.0
    hits = 0
    for n in nums:
        if any(abs(n - a) / max(abs(a), 1e-9) <= 0.01 for a in allowed):
            hits += 1
    return hits / len(nums)


def reasoning_verifier(completion: str) -> float:
    """Crude proxy: rewards reasoning that uses connectives AND cites numbers.

    Real systems use an LLM-as-judge with a rubric; this rule-based stand-in
    is enough for the pedagogical point.
    """
    text = completion.lower()
    has_connective = any(c in text for c in _CONNECTIVES)
    has_numbers = bool(_NUM_RE.search(completion))
    has_decision = _extract_decision(completion) is not None
    score = 0.0
    if has_connective:
        score += 0.4
    if has_numbers:
        score += 0.3
    if has_decision:
        score += 0.3
    return score


def outcome_verifier(ctx: TradeContext, completion: str) -> float:
    """Same signal as the naive verifier but mapped to [0, 1]."""
    decision = _extract_decision(completion)
    ret = ctx.forward_excess_return
    if decision == "BUY":
        signed = ret
    elif decision == "SELL":
        signed = -ret
    else:
        signed = 0.0
    return max(0.0, min(1.0, 0.5 + signed * 5))


def verifier(ctx: TradeContext, completion: str) -> dict[str, float]:
    e = evidence_verifier(ctx, completion)
    r = reasoning_verifier(completion)
    o = outcome_verifier(ctx, completion)
    composite = (max(e, 1e-3) * max(r, 1e-3) * max(o, 1e-3)) ** (1 / 3)
    return {
        "reward": composite,
        "evidence": e,
        "reasoning": r,
        "outcome": o,
        "decision": _extract_decision(completion) or "NONE",
    }
