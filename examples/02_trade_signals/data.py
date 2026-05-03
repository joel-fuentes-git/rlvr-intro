"""Cached training curves and example completions for trade signal example."""

from __future__ import annotations

import numpy as np
import pandas as pd


def training_curves_df(n_steps: int = 600, seed: int = 19) -> pd.DataFrame:
    """Long-format DataFrame: columns = step, reward, verifier.

    The naive curve is jittery and barely climbs (noise wall). The triangular
    curve is smoother and reaches a clearly higher plateau.
    """
    rng = np.random.default_rng(seed)
    steps = np.arange(n_steps)

    naive_base = 0.50 + 0.05 / (1 + np.exp(-(steps - 200) / 50))
    naive_noise = rng.normal(0, 0.18, size=n_steps)
    naive = np.clip(naive_base + naive_noise, 0, 1)

    tri_base = 0.30 + (0.78 - 0.30) / (1 + np.exp(-(steps - 180) / 40))
    tri_noise = rng.normal(0, 0.05, size=n_steps)
    tri = np.clip(tri_base + tri_noise, 0, 1)

    return pd.concat(
        [
            pd.DataFrame({"step": steps, "reward": naive, "verifier": "naive"}),
            pd.DataFrame({"step": steps, "reward": tri,   "verifier": "triangular"}),
        ],
        ignore_index=True,
    )


# A market context the demo widget operates over. Numbers are illustrative.
DEMO_CONTEXT = dict(
    ticker="ACME",
    forward_excess_return=0.04,  # +4% over benchmark in the next 21 days
    cited_facts={
        "price": 87.40,
        "ma_50": 81.20,
        "ma_200": 74.10,
        "pe_ratio": 22.8,
        "rsi_14": 71.0,
    },
)

# A naively-rewarded model converges to confident momentum-chasing prose
# that doesn't actually engage with the data.
HACKED_COMPLETION = (
    "ACME has strong momentum and a constructive technical setup. "
    "The chart shows clear higher highs and the trend is intact. "
    "Therefore I recommend BUY."
)

# A response under triangular training: cites real numbers, reasons through them.
GROUNDED_COMPLETION = (
    "ACME closed at 87.40, above its 50-day moving average of 81.20 and well "
    "above its 200-day of 74.10. RSI of 71.0 suggests overbought conditions. "
    "Given the trend is intact but momentum is stretched, and given P/E of 22.8 "
    "is in line with peers, I recommend HOLD."
)
