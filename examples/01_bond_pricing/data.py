"""Cached pedagogical artifacts for the bond pricing example.

We do NOT actually fine-tune a model. The point of the example is the *dynamics*
of a clean RLVR loop. The training curve and completions below are synthetic but
shaped to match what a small model trained on this task actually produces.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def training_curve_df(n_steps: int = 400, seed: int = 7) -> pd.DataFrame:
    """Synthetic mean-reward-per-step curve.

    Starts near 0.05 (random guessing rarely lands in tolerance), climbs as the
    model learns the discounting structure, plateaus near 0.92.
    """
    rng = np.random.default_rng(seed)
    steps = np.arange(n_steps)
    # Logistic climb from 0.05 to 0.92, knee around step 120
    base = 0.05 + (0.92 - 0.05) / (1 + np.exp(-(steps - 120) / 25))
    noise = rng.normal(0, 0.04, size=n_steps)
    reward = np.clip(base + noise, 0, 1)
    return pd.DataFrame({"step": steps, "reward": reward})


def density_curve_df(n_steps: int = 400, seed: int = 11) -> pd.DataFrame:
    """Fraction of sampled completions earning reward > 0.5.

    This is the *density* signal RLVR depends on. It climbs alongside the reward
    curve but is more interpretable to a non-RL audience.
    """
    rng = np.random.default_rng(seed)
    steps = np.arange(n_steps)
    base = 0.10 + (0.95 - 0.10) / (1 + np.exp(-(steps - 110) / 22))
    noise = rng.normal(0, 0.03, size=n_steps)
    return pd.DataFrame({"step": steps, "density": np.clip(base + noise, 0, 1)})


SAMPLE_PROMPT = (
    "A bond has face value $1,000, an annual coupon rate of 5%, "
    "yield-to-maturity of 6%, and matures in 5 years (annual coupons). "
    "What is its fair price?"
)

SAMPLE_INPUTS = dict(face=1000.0, coupon_rate=0.05, ytm=0.06, years=5, freq=1)

# What an untrained model often produces: confident, fluent, wrong.
COMPLETION_BEFORE = (
    "The bond pays $50 per year for 5 years and returns $1,000 at maturity. "
    "Adding these up: $50 x 5 = $250 in coupons, plus $1,000 face value = $1,250.\n\n"
    "Answer: $1,250.00"
)

# After training: the discounting structure shows up, the answer is correct.
COMPLETION_AFTER = (
    "Coupon C = 1000 x 0.05 = 50 per year. YTM y = 0.06. T = 5.\n"
    "PV(coupons) = sum_{t=1..5} 50 / (1.06)^t\n"
    "  t=1: 47.17\n"
    "  t=2: 44.50\n"
    "  t=3: 41.98\n"
    "  t=4: 39.60\n"
    "  t=5: 37.36\n"
    "  sum  = 210.62\n"
    "PV(face) = 1000 / (1.06)^5 = 747.26\n"
    "P = 210.62 + 747.26\n\n"
    "Answer: 957.88"
)
