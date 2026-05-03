"""Deterministic verifier for vanilla coupon bond pricing.

A coupon bond's price is closed-form:

    P = sum_{t=1..T} C / (1+y)^t  +  F / (1+y)^T

The verifier extracts the model's numeric answer and compares it to the analytical
price within a tolerance. It is a pure function: same inputs in, same reward out.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class BondInputs:
    face: float
    coupon_rate: float   # annual, decimal (e.g. 0.05 for 5%)
    ytm: float           # annual, decimal
    years: int
    freq: int = 1        # coupons per year


def analytical_price(b: BondInputs) -> float:
    periods = b.years * b.freq
    period_rate = b.ytm / b.freq
    coupon = b.face * b.coupon_rate / b.freq
    pv_coupons = sum(coupon / (1 + period_rate) ** t for t in range(1, periods + 1))
    pv_face = b.face / (1 + period_rate) ** periods
    return pv_coupons + pv_face


_NUM_RE = re.compile(r"-?\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?")


def _extract_final_number(completion: str) -> float | None:
    """Pull the last number from the completion (typical 'answer = X' position)."""
    matches = _NUM_RE.findall(completion)
    if not matches:
        return None
    raw = matches[-1].replace("$", "").replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return None


def verifier(
    inputs: BondInputs,
    completion: str,
    *,
    tolerance: float = 0.01,
) -> dict[str, float]:
    """Return reward components for a bond-pricing completion.

    The composite ``reward`` is 1.0 if the answer is within ``tolerance`` (relative)
    of the analytical price, scaled smoothly otherwise.
    """
    truth = analytical_price(inputs)
    guess = _extract_final_number(completion)

    if guess is None:
        return {"reward": 0.0, "relative_error": 1.0, "extracted": float("nan")}

    rel_err = abs(guess - truth) / max(abs(truth), 1e-9)
    if rel_err <= tolerance:
        reward = 1.0
    else:
        reward = max(0.0, 1.0 - rel_err / 0.10)  # falls to 0 by 10% error

    return {"reward": reward, "relative_error": rel_err, "extracted": guess}
