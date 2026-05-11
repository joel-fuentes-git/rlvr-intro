"""Reference solution.

Composite reward chosen as the geometric mean of the three sub-rewards
(with component_verifier collapsed to its mean). Geometric mean penalises
a single zero-scoring sub-verifier sharply — which is what we want, since
each sub-verifier checks a property the others cannot.
"""

from __future__ import annotations

from math import isclose

from simulator import (
    EXPECTED_FILLS,
    EXPECTED_FINAL_CASH,
    SAMPLE_AGENTS,
    SCENARIO_QUOTES,
    TARGET_SHARES,
    Simulator,
    fresh_simulator,
)


def state_verifier(sim: Simulator) -> float:
    correct_shares = sim.state.shares_held == TARGET_SHARES
    correct_cash = isclose(sim.state.cash_spent, EXPECTED_FINAL_CASH, abs_tol=0.005)
    return 1.0 if (correct_shares and correct_cash) else 0.0


def component_verifier(sim: Simulator) -> dict[str, float]:
    scores: dict[str, float] = {}
    for i, expected in enumerate(EXPECTED_FILLS):
        match = any(
            f.venue == expected.venue
            and f.shares == expected.shares
            and isclose(f.price, expected.price, abs_tol=0.001)
            for f in sim.state.fills
        )
        scores[f"fill_{i}"] = 1.0 if match else 0.0
    return scores


def _optimal_cost(quotes, target_shares: int) -> float:
    remaining = target_shares
    cost = 0.0
    for q in sorted(quotes, key=lambda q: q.price):
        take = min(remaining, q.available)
        cost += take * q.price
        remaining -= take
        if remaining == 0:
            break
    if remaining > 0:
        return float("inf")
    return cost


def ground_truth_verifier(sim: Simulator) -> float:
    if sim.state.shares_held != TARGET_SHARES:
        return 0.0
    optimal = _optimal_cost(SCENARIO_QUOTES, TARGET_SHARES)
    overpay = max(0.0, sim.state.cash_spent - optimal)
    return max(0.0, 1.0 - overpay / optimal)


def composite_reward(sim: Simulator) -> float:
    s = state_verifier(sim)
    c_scores = component_verifier(sim)
    c = sum(c_scores.values()) / max(1, len(c_scores))
    g = ground_truth_verifier(sim)
    return (max(s, 1e-6) * max(c, 1e-6) * max(g, 1e-6)) ** (1 / 3)


if __name__ == "__main__":
    print(f"{'agent':<12} {'state':>6} {'components':>14} {'ground':>8} {'final':>7}")
    print("-" * 52)
    for name, agent in SAMPLE_AGENTS.items():
        sim = fresh_simulator()
        agent(sim)
        s = state_verifier(sim)
        c = component_verifier(sim)
        c_str = "/".join(f"{v:.2f}" for v in c.values())
        g = ground_truth_verifier(sim)
        r = composite_reward(sim)
        print(f"{name:<12} {s:>6.2f} {c_str:>14} {g:>8.2f} {r:>7.2f}")
