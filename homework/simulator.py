"""Toy broker simulator for the Westworld-style homework.

A deterministic in-memory "broker" with three venues. The agent acts on it by
calling `Simulator.submit(venue, shares)`; the simulator records the fill and
updates its observable state. Verifiers read that state.

This is deliberately small. The point is not the simulator; the point is that
you have one at all, and that everything the agent does is inspectable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Quote:
    venue: str
    price: float
    available: int


@dataclass(frozen=True)
class Fill:
    venue: str
    shares: int
    price: float


@dataclass
class BrokerState:
    cash_spent: float = 0.0
    shares_held: int = 0
    fills: list[Fill] = field(default_factory=list)


@dataclass
class Simulator:
    quotes: tuple[Quote, ...]
    state: BrokerState = field(default_factory=BrokerState)

    def submit(self, venue: str, shares: int) -> None:
        quote = next((q for q in self.quotes if q.venue == venue), None)
        if quote is None:
            raise ValueError(f"unknown venue: {venue}")
        if shares <= 0:
            raise ValueError("shares must be positive")
        if shares > quote.available:
            raise ValueError(
                f"venue {venue} only has {quote.available} shares available"
            )
        self.state.fills.append(Fill(venue=venue, shares=shares, price=quote.price))
        self.state.cash_spent += shares * quote.price
        self.state.shares_held += shares


# --- The canonical scenario --------------------------------------------------

TASK_DESCRIPTION = "Buy 100 shares of ACME at the best total price."

TARGET_SHARES = 100

SCENARIO_QUOTES: tuple[Quote, ...] = (
    Quote(venue="A", price=10.00, available=40),
    Quote(venue="B", price=10.05, available=80),
    Quote(venue="C", price=10.20, available=200),
)

# Optimal routing: 40 @ A + 60 @ B = $1,003.00.
EXPECTED_FINAL_CASH = 1003.00
EXPECTED_FILLS: tuple[Fill, ...] = (
    Fill(venue="A", shares=40, price=10.00),
    Fill(venue="B", shares=60, price=10.05),
)


def fresh_simulator() -> Simulator:
    return Simulator(quotes=SCENARIO_QUOTES)


# --- Sample agents -----------------------------------------------------------

Agent = Callable[[Simulator], None]


def agent_optimal(sim: Simulator) -> None:
    """Hits A and B in the right amounts. 100 shares at $1003.00."""
    sim.submit("A", 40)
    sim.submit("B", 60)


def agent_lazy(sim: Simulator) -> None:
    """Buys everything at venue C. Right share count, overpays."""
    sim.submit("C", 100)


def agent_overbought(sim: Simulator) -> None:
    """Buys too much. Wrong final state entirely."""
    sim.submit("A", 40)
    sim.submit("B", 80)


SAMPLE_AGENTS: dict[str, Agent] = {
    "optimal": agent_optimal,
    "lazy": agent_lazy,
    "overbought": agent_overbought,
}
