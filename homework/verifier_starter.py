"""Starter file. Fill in the four TODOs.

Run this file directly to see your verifier scoring the three sample agents:

    python verifier_starter.py
"""

from __future__ import annotations

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
    """Return 1.0 if the final state matches expectations exactly, else 0.0.

    Hint: compare sim.state.shares_held to TARGET_SHARES and sim.state.cash_spent
    to EXPECTED_FINAL_CASH (use a small tolerance for float compare).
    """
    # TODO: implement
    return 0.0


def component_verifier(sim: Simulator) -> dict[str, float]:
    """Return a dict mapping each EXPECTED_FILLS entry to a 0.0/1.0 score
    based on whether the agent's fills include an exact match.

    Hint: iterate over EXPECTED_FILLS, look for the same (venue, shares, price)
    in sim.state.fills, score 1.0 per match.
    """
    # TODO: implement
    return {f"fill_{i}": 0.0 for i, _ in enumerate(EXPECTED_FILLS)}


def ground_truth_verifier(sim: Simulator) -> float:
    """Compute the optimal cost from SCENARIO_QUOTES on the fly, then score
    the agent's cash_spent relative to optimal.

    Hint: sort quotes by price ascending, fill greedily up to TARGET_SHARES,
    sum the cost. Then compare to sim.state.cash_spent.

    If the agent's final shares_held != TARGET_SHARES, return 0.0.
    """
    # TODO: implement
    return 0.0


def composite_reward(sim: Simulator) -> float:
    """Combine the three sub-rewards into one number in [0, 1].

    Document your choice (min? geometric mean? weighted sum?) in a comment.
    """
    # TODO: implement
    return 0.0


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
