# RLVR for Finance — An Interactive Primer

A small, focused educational artifact that teaches RLVR (Reinforcement Learning with Verifiable Rewards) from first principles, then demonstrates — through three runnable examples — why the **verifier**, not the model or the algorithm, is the central design problem in finance.

The full specification, narrative arc, and design system live in [`CLAUDE.md`](./CLAUDE.md).

## Quick start

```bash
pip install -e .
streamlit run app/main.py
```

The app opens with five pages, navigated from the left sidebar:

1. **What is RLVR?** — first-principles intro to verifiable rewards and GRPO.
2. **Where RLVR Just Works** — bond pricing, a clean deterministic verifier.
3. **Where RLVR Breaks** — trade signal generation, the noise-and-hacking failure.
4. **The Frontier** — 10-K reasoning with a process verifier.
5. **The Verifier *is* the IP** — recap.

---

## What's in this repo

The project is laid out so that each example is independently readable. Every verifier is a pure function — same inputs in, same reward out — so you can read it in five minutes and adapt it to your own domain.

```
rlvr-finance-explainer/
├── CLAUDE.md                     The canonical spec — read this first
├── README.md                     You are here
├── pyproject.toml
│
├── app/                          The Streamlit app
│   ├── main.py                   Entry point: sidebar nav, CSS injection
│   ├── styles.css                Design tokens (color, type, spacing)
│   ├── chart_theme.py            Minimal Plotly template (no gridlines, single accent)
│   ├── components/               Reusable UI atoms
│   │   ├── eyebrow.py            Uppercase tag above each page title
│   │   ├── takeaway.py           Bold one-sentence callout per page
│   │   ├── verifier_card.py      Green/amber/red sub-verifier indicator
│   │   ├── training_curve.py     Animated reward-over-steps chart
│   │   └── loader.py             Imports digit-prefixed example modules
│   └── pages/                    One file per page; pure composition over components
│       ├── 00_intro.py
│       ├── 01_bond_pricing.py
│       ├── 02_trade_signals.py
│       ├── 03_filing_reasoning.py
│       └── 04_recap.py
│
└── examples/                     Verifiers and cached artifacts (the substance)
    ├── 01_bond_pricing/
    ├── 02_trade_signals/
    └── 03_filing_reasoning/
```

---

## The three examples

The examples are pedagogically progressive — each one introduces a problem the previous one couldn't show. Together they make the argument.

### Example 1 — Bond pricing (`examples/01_bond_pricing/`)

**The easy case: closed-form answer, deterministic verifier, dense reward.**

A vanilla coupon bond's price is `Σ C/(1+y)^t + F/(1+y)^T`. The verifier extracts the model's numeric answer and compares it to the analytical price within a tolerance.

| File | What it contains |
|---|---|
| `verifier.py` | `BondInputs` dataclass, `analytical_price()`, and `verifier()` — ~50 lines, no I/O. Returns reward 1.0 when within tolerance, scaling smoothly to 0.0 by 10% relative error. |
| `data.py` | Synthetic training-curve and density-curve data (logistic climb, plateau ≈ 0.92), plus before/after sample completions for the same prompt. |

**What the page demonstrates:** GRPO converging cleanly. Reward climbs through a logistic curve. The "before training" completion is fluent and wrong ($1,250 — sums coupons without discounting). The "after training" completion shows the discount-and-sum structure ($957.88, the analytical answer). An interactive widget lets you change bond inputs and a candidate completion and watch the reward respond.

### Example 2 — Trade signal generation (`examples/02_trade_signals/`)

**The hard case: an honest verifier with a hackable proxy.**

The model is given market context for a stock and asked for BUY / HOLD / SELL with reasoning. The naive verifier rewards forward 21-day excess return. It looks reasonable. It produces a model that hallucinates technicals.

| File | What it contains |
|---|---|
| `naive_verifier.py` | `MarketContext` dataclass and a one-function verifier that signs the forward return by the BUY/SELL/HOLD decision. The verifier that fails. |
| `triangular_verifier.py` | Three sub-verifiers — `evidence_verifier` (do cited numbers match the input?), `reasoning_verifier` (connectives + numbers + decision present?), `outcome_verifier` (did the trade move in the predicted direction?) — combined via geometric mean. The fix. |
| `data.py` | Long-format training curves for both verifiers (the naive one is jittery and barely climbs; the triangular one is smooth and plateaus higher), plus two sample completions: a "hacked" momentum hand-wave that cites no real numbers, and a "grounded" response that engages with the data. |

**What the page demonstrates:** the noise wall (naive curve barely moves), the failure mode (hacked completion gets 0.7 reward under the naive verifier and 0.08 under the triangular one because evidence collapses), and an interactive autopsy widget where you edit a completion and watch the four sub-scores update live.

### Example 3 — 10-K filing reasoning (`examples/03_filing_reasoning/`)

**The frontier: when the answer is a chain, verify the chain.**

The model answers a multi-step question about Apple's services vs. products revenue growth. It responds in a small structured DSL — `EXTRACT`, `COMPUTE`, `CITE`, `CONCLUDE` — that exposes its reasoning to verification step by step.

| File | What it contains |
|---|---|
| `verifier.py` | The DSL parser plus four sub-verifiers: extraction (do cited values match the filing?), calculation (does the arithmetic evaluate against extracted keys?), citation (does each key point to the right source?), final answer (does the conclusion mention the expected concepts?). Composite reward is a tunable weighted sum, supporting curriculum-style training. |
| `data.py` | A pre-processed Apple 10-K filing as a flat fact dict, source pointers, the canonical question, and three sample completions: grounded (passes everything), hacked (correct format, wrong numbers — extraction kills it), and prose-only (just a `CONCLUDE` line — no chain to verify). |

**What the page demonstrates:** a step-by-step trace (each line lights up green or red as its sub-verifier evaluates it), and a re-weighting panel where you can shift mass between the four sub-verifiers and see which completion the policy gradient would prefer under each weighting.

---

## Reading the code

If you only have time for two files, read `examples/02_trade_signals/triangular_verifier.py` and `examples/03_filing_reasoning/verifier.py`. Together they are the entire argument of the talk: the verifier is the design problem, and a good verifier looks like a small data-engineering project, not RL research.

## Status

Pedagogical artifact. Not a training pipeline. Not a benchmark. Not financial advice.

---

## Homework — a Westworld-style verifier

A small self-contained exercise lives in [`homework/`](./homework/). It is inspired by Halluminate's [Westworld](https://www.halluminate.ai/blog/westworld) — a suite of web-app simulators built so that web agents can be evaluated under deterministic, reproducible rewards rather than live-site noise. The same trick transplants to finance.

You get a toy "broker simulator" (three venues, one ticker, the agent buys 100 shares at the best total price) and a starter file with three sub-verifier stubs to fill in, matching the three verification methods in the Westworld blog: a **state** check, a **component** check, and a **ground-truth** check computed against the simulator's own quotes. Three sample agents — optimal, lazy, overbought — give you something concrete to score, plus a few discussion questions that connect back to this repo's main thesis.

Start at [`homework/README.md`](./homework/README.md).
