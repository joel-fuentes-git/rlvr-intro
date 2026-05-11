# CLAUDE.md — RLVR for Finance

> **Project codename:** `rlvr-finance-explainer`
> **Audience:** Quantitative finance students, applied ML practitioners in financial services, talk attendees
> **Deliverable:** A pedagogical repository + sleek Streamlit app that walks the viewer through RLVR (Reinforcement Learning with Verifiable Rewards), why finance is the hardest domain for it, and three worked examples that progressively reveal the core design problem.
> **Author context:** Joel Fuentes (JPMorgan Chase, Applied AI/ML Lead). Material derived from his University of Chicago Financial Mathematics seminar series.

---

## 0. Purpose of This File

This `CLAUDE.md` is the canonical specification for the project. It is intended to be read by:

1. **Claude Code** — when extending, refactoring, or building new components in this repo.
2. **The author** — when authoring slide decks for the accompanying talk; section structure here mirrors the intended slide narrative.
3. **Future readers of the repo** — as a self-contained explainer that does not require running the app.

Everything Claude Code builds in this repo should be traceable to a section here. If a new feature has no corresponding section, update this file first.

---

## 1. Project Overview

### 1.1 What this project is

A small, focused educational artifact that:

1. Teaches RLVR from first principles in the language of a quant finance audience.
2. Demonstrates, with three runnable examples, how the verifier — not the model, not the algorithm — is the central design problem.
3. Provides a Streamlit app that turns each example into an interactive visual narrative suitable for a 30–45 minute talk.

### 1.2 What this project is *not*

- Not a production training pipeline. Examples may use lightweight stand-ins (e.g., synthetic policies) where full LLM fine-tuning would obscure the pedagogical point.
- Not a benchmark. We are not claiming SOTA on anything.
- Not financial advice. Trading examples use historical data for illustration only.

### 1.3 Talk narrative arc

The repo and app are structured to support a three-act talk:

| Act | Question | Resolution |
|---|---|---|
| **I. Foundations** | What is RLVR and why is everyone talking about it? | GRPO + verifiable rewards collapse the human-feedback bottleneck. |
| **II. The Finance Problem** | Why doesn't this just transfer to finance? | Verifiers in finance are stochastic, sparse, and easy to game. |
| **III. The Frontier** | What does "good" RLVR for finance look like? | Triangular / process / consistency verifiers — the verifier is the IP. |

Each example in the app maps to one act.

---

## 2. RLVR Conceptual Foundation

### 2.1 The one-line definition

> **RLVR** trains a language model to maximize a reward signal that is computed by a deterministic, programmatic *verifier* — not by a human preference model.

### 2.2 Why this matters

Pre-RLVR (RLHF era): reward came from a learned reward model trained on human preference pairs. Expensive, noisy, easy to game, capped by labeler quality.

Post-RLVR: reward comes from a function. For math, the function is `answer == expected`. For code, `tests_pass(generated_code)`. The reward signal is cheap, scalable, and — within its domain — uncheatable.

The result: DeepSeek-R1, the open-weights reasoning model that catalyzed the shift, was trained predominantly with verifiable rewards on math and code. The reasoning ability *transferred* to many other domains the model was never explicitly trained on.

### 2.3 The canonical algorithm: GRPO

**Group Relative Policy Optimization** is the workhorse RL algorithm behind most modern RLVR systems. The intuition:

1. For a given prompt, sample `G` candidate completions from the current policy.
2. Score each one with the verifier → group of rewards `r_1 ... r_G`.
3. Compute *relative* advantages: each completion's reward minus the group mean, divided by group std.
4. Update the policy to up-weight tokens in above-average completions and down-weight tokens in below-average ones.
5. Add a KL penalty against a reference policy to prevent catastrophic drift.

GRPO eliminates the value function (no critic network) — group statistics replace it. This is what makes RLVR cheap enough to run on a single 8×H100 node for small models.

### 2.4 The three things that must be true for RLVR to work

1. **Verifiability**: There must be a programmatic check for "correct."
2. **Density**: Among `G` samples, at least some must be correct, or there is no signal to learn from.
3. **Faithfulness**: The verifier must reward the *property you actually care about*, not a proxy that can be hacked.

**These three constraints are the entire story.** Every advanced RLVR technique exists because one of them broke.

---

## 3. Why Finance is the Hardest Domain for RLVR

This is the core thesis of the talk and should be the most memorable section.

### 3.1 The verifiability problem

Math has `4 == 4`. Code has `assert tests_pass()`. Finance has:

- Was that trade *good*? → Depends on the holding period, the benchmark, the market regime, the cost of capital, and what else you could have done with the money.
- Was that risk assessment *correct*? → Won't know until either the tail event happens or it doesn't, and the absence of a tail event doesn't validate the model.
- Was that earnings interpretation *right*? → Often depends on subsequent quarters of data not yet available.

In short: **most things finance professionals get paid to do are not cleanly verifiable on the timescales over which a model trains**.

### 3.2 The density problem

In math RLVR, a 1.5B model can solve grade-school arithmetic ~50% of the time on first sample. Plenty of signal.

In trading: even a perfectly informed model has a Sharpe ratio bounded by the market's information content. On a single trade, the "right" decision still loses money about 45% of the time. Most reward signal *is noise*. Naive RLVR averages over noise → averages out the signal.

### 3.3 The faithfulness problem (a.k.a. reward hacking)

This is where it gets dangerous. If you reward "trades that made money over the next 30 days" on historical data, an LLM with enough capacity will learn:

- **Lookahead leakage:** Recognize tickers and remember their post-window returns from pretraining.
- **Momentum mimicry:** Become a one-line momentum strategy that hallucinates fundamental justifications.
- **Survivorship pattern matching:** Always recommend names that survived to be in the dataset.

The verifier said "high reward." The model said "thanks." The deployed system loses money.

### 3.4 The implication

> **In finance, designing the verifier is the research problem.** The choice of model, the choice of algorithm, the choice of compute budget — all secondary. If your verifier rewards reward-hackable proxies, the better your model, the worse your outcome.

This is the line the talk should drive home.

---

## 4. Three Example Projects

Each example is implemented as a Python module under `examples/` and surfaced as a Streamlit page under `app/pages/`. They are designed to be pedagogically *progressive*: each one introduces a problem the previous example couldn't show.

### 4.1 Example 1 — *Deterministic Verifier: Bond Pricing*

**Module:** `examples/01_bond_pricing/`
**Streamlit page:** "Where RLVR Just Works"
**Talk slot:** Act I closer

#### Premise

A vanilla coupon bond has a closed-form price. Given face value, coupon rate, yield-to-maturity, and time-to-maturity, the price is:

```
P = Σ (C / (1+y)^t) + F / (1+y)^T
```

The model is asked to compute it given inputs in natural language. The verifier checks the answer to within ε of the analytical solution.

#### What this demonstrates

- The "easy" case: clean inputs, single correct answer, programmatic check, dense signal.
- A baseline GRPO loop running cleanly — students see the loss go down, accuracy go up, sample completions get more structured.
- The reasoning chain becomes more disciplined as training progresses (good visual on the Streamlit page).

#### Implementation notes

- We do **not** need to actually fine-tune a model live in the app. The educational point is the *dynamics*, not the artifact.
- Cache pre-computed checkpoints (or scripted "before / after" completions) and animate them.
- The verifier is ~10 lines of code. Show it.

#### Visualization

- Live training curve (reward over steps).
- "Before training" vs "After training" sample completions, side-by-side, highlighted.
- A meter showing "what fraction of sampled completions get reward > 0.5" (the *density* metric).

---

### 4.2 Example 2 — *Stochastic Verifier: Trade Signal Generation*

**Module:** `examples/02_trade_signals/`
**Streamlit page:** "Where RLVR Breaks"
**Talk slot:** Act II centerpiece

#### Premise

The model is given a market context (recent OHLCV, simple fundamentals) for a held-out universe of stocks and asked to generate a buy / hold / sell decision with a reasoning chain. The verifier is the *forward 21-day excess return* relative to a benchmark.

This is a deliberately naive setup. The point is to make it fail.

#### What this demonstrates

- **The signal-to-noise wall.** Show that even with thousands of training examples, reward is dominated by noise. The training curve is jittery and barely improves.
- **Reward hacking emerges visibly.** After enough training, the model converges to "always recommend high-momentum names with technical-sounding justification." Show example completions: the reasoning is fluent and wrong.
- **The verifier was honest. The proxy was the lie.** Future excess return is a noisy proxy for "good investment thesis."

#### The fix: triangular verification

Implement a Trade-R1-inspired triangular verifier:

1. **Evidence verifier:** Does the cited evidence (price levels, ratios) actually appear in the input data?
2. **Reasoning verifier:** Does the reasoning chain logically connect the evidence to the conclusion? (LLM-as-judge with a constrained rubric.)
3. **Outcome verifier:** Did the position make money? (The original noisy signal — but now weighted *less* in the composite score.)

The composite reward is the geometric mean of the three. A reward-hacking strategy fails (1) or (2) regardless of (3).

#### Visualization

- Side-by-side: naive verifier training curve (jittery, low) vs triangular training curve (cleaner, higher).
- A "reasoning autopsy" widget: paste a model completion, see all three sub-rewards lit up like a control panel.
- Walk-through animation: the same example completion under both verifiers, with sub-scores annotated.

#### Implementation notes

- For tractability, use a small open dataset (e.g., S&P 500 historical OHLCV from `yfinance`) with a fixed train/test temporal split.
- The "model" in the demo can be a scripted policy that simulates the failure modes — full LLM fine-tuning is unnecessary for the visualization.
- The triangular verifier itself is the artifact worth showing.

---

### 4.3 Example 3 — *Process Verifier: 10-K Reasoning*

**Module:** `examples/03_filing_reasoning/`
**Streamlit page:** "What RLVR for Finance Will Actually Look Like"
**Talk slot:** Act III, looking forward

#### Premise

The model is given a 10-K excerpt and asked a multi-step financial reasoning question, e.g.:

> *"Apple's services revenue grew at what rate from FY2022 to FY2024, and how does that compare to its product revenue growth over the same period? Cite the relevant figures."*

The "correct answer" is not a single number — it is a chain: (a) extract the right figures, (b) compute the right ratios, (c) make the right comparison, (d) cite correctly.

#### The process verifier

Inspired by MR-RLVR and K2V research:

1. **Extraction sub-verifier:** Are the cited figures actually in the document? (String / table-cell match.)
2. **Calculation sub-verifier:** Do the arithmetic operations on extracted figures produce the asserted intermediate values? (Sympy or eval.)
3. **Citation sub-verifier:** Does each claim have a corresponding source pointer? (Pattern match.)
4. **Final-answer sub-verifier:** Does the conclusion follow from the verified intermediates?

Each step gets a sub-reward. The final reward is a weighted sum, with optional curriculum (early training weights extraction heavily; later training shifts weight to final-answer).

#### What this demonstrates

- **Process supervision generalizes outcome supervision.** When the answer is a chain, you can — and should — verify the chain.
- **The verifier looks like a small data engineering project.** This is the realistic engineering load of doing RLVR for finance well.
- **Once you have process verifiers, the model can be small.** You don't need GPT-5 to do this — you need the right verifier architecture.

#### Visualization

- A reasoning chain UI: each step (extract → compute → cite → conclude) appears as a card, lighting up green/red as the sub-verifier evaluates it.
- A "verifier config" panel where the viewer can re-weight sub-verifiers and see how the training trajectory would change.
- Show the same model output under (a) outcome-only verifier and (b) full process verifier — different rewards, different gradient signals, different learned behavior.

#### Implementation notes

- Pre-process 2–3 well-known 10-Ks (Apple, Costco, NVIDIA) and have a small set of canonical questions.
- The extraction layer can re-use the architecture from `graphify-unstructured` (Joel's existing repo) for table-aware parsing.
- The process verifier is the centerpiece — give it its own clean module (`examples/03_filing_reasoning/verifier.py`) that other authors can read and crib from.

---

## 5. Streamlit App Architecture

### 5.1 Design philosophy

> **Pedagogical clarity over decoration.** Every pixel earns its place. The viewer should never wonder where to look next.

Style touchstones: Stripe documentation, Linear changelogs, OpenAI's interpretability gallery. Quiet, confident, lots of whitespace.

### 5.2 Information architecture

```
┌─────────────────────────────────────────────────────┐
│  RLVR FOR FINANCE                                   │
│  An interactive primer                              │
├─────────┬───────────────────────────────────────────┤
│         │                                           │
│ ▸ Intro │   [main canvas: large, focused]          │
│   Ex 1  │                                           │
│   Ex 2  │                                           │
│   Ex 3  │                                           │
│   Recap │                                           │
│         │                                           │
│ About   │                                           │
└─────────┴───────────────────────────────────────────┘
```

Five pages, accessed via a left sidebar with vertical text-only nav (no icons, no badges). Pages:

| Slug | Title | Maps to |
|---|---|---|
| `00_intro` | What is RLVR? | §2 of this doc |
| `01_bond_pricing` | Where RLVR Just Works | §4.1 / Example 1 |
| `02_trade_signals` | Where RLVR Breaks | §4.2 / Example 2 |
| `03_filing_reasoning` | The Frontier | §4.3 / Example 3 |
| `04_recap` | The Verifier *is* the IP | §3.4 closing argument |

### 5.3 Page anatomy (consistent across all five)

```
[ Eyebrow label — e.g., "Example 2 of 3" ]

# Page Title
A one-sentence subtitle that frames the takeaway.

[ Main interactive widget — chart, animation, or split view ]

## What's happening here
Two short paragraphs of plain-language explanation.

## Try this
A small interactive control (slider, button, dropdown) that lets the
viewer perturb the example and see what changes.

## The takeaway
A single bold sentence — the line you want them to remember.

[ Footer: ← Previous page · Next page → ]
```

### 5.4 Visual language

**Color palette** (use as CSS variables — no hardcoded hex anywhere in component code):

| Variable | Hex | Use |
|---|---|---|
| `--bg` | `#FAFAF7` | Page background (warm off-white, not pure white) |
| `--surface` | `#FFFFFF` | Card / widget surfaces |
| `--ink` | `#1A1A1A` | Primary text |
| `--ink-soft` | `#5A5A5A` | Secondary text |
| `--rule` | `#E8E6E0` | Hairline dividers |
| `--accent` | `#1F6FEB` | Single accent — interactive elements, key data series |
| `--good` | `#2D7A4F` | Verifier-pass states |
| `--bad` | `#B8341F` | Verifier-fail states |

**No more than three colors on any single screen** beyond ink and background.

**Typography:**
- Headings: `Inter` 600, tight tracking
- Body: `Inter` 400, generous line height (1.6)
- Numerals & code: `JetBrains Mono` (tabular numerals on for all data displays)

**Spacing scale:** 4 / 8 / 16 / 24 / 48 / 96 px. Use large vertical rhythm — it makes the app feel slow and confident, which is the right register for a teaching tool.

**Charts:** Plotly with a custom minimal theme (no gridlines, no legend boxes, axis labels in `--ink-soft`, single-series default to `--accent`). Chart titles are page-level headings, not chart-level chrome.

**Animation:** Sparingly. Training curves animate in left-to-right on first view. Verifier sub-scores "tick" green/red with a 200ms ease. No bouncing. No spinners — use skeleton loaders.

### 5.5 Tech stack

- **App framework:** Streamlit (latest)
- **Charts:** Plotly + a small `chart_theme.py` that registers a minimal template
- **Layout:** Native Streamlit `st.columns` and `st.container` — avoid third-party layout libraries
- **State:** `st.session_state` only; no external store
- **Styling:** A single `app/styles.css` injected via `st.markdown(unsafe_allow_html=True)` at app start — defines the CSS variables and a handful of utility classes
- **Data:** Pre-computed artifacts under `data/` (training curves as CSV, sample completions as JSON). The app does *not* run training live.

---

## 6. Repo Structure

```
rlvr-finance-explainer/
├── CLAUDE.md                  # this file
├── README.md                  # short, public-facing
├── pyproject.toml
├── app/
│   ├── main.py                # entry point, sidebar nav, CSS injection
│   ├── styles.css
│   ├── chart_theme.py
│   ├── components/
│   │   ├── eyebrow.py         # the "Example 2 of 3" label
│   │   ├── takeaway.py        # the bold one-sentence takeaway block
│   │   ├── verifier_card.py   # the green/red sub-verifier indicator
│   │   └── training_curve.py  # the animated reward chart
│   └── pages/
│       ├── 00_intro.py
│       ├── 01_bond_pricing.py
│       ├── 02_trade_signals.py
│       ├── 03_filing_reasoning.py
│       └── 04_recap.py
├── examples/
│   ├── 01_bond_pricing/
│   │   ├── verifier.py
│   │   ├── completions.json   # cached "before/after" examples
│   │   └── training_curve.csv
│   ├── 02_trade_signals/
│   │   ├── naive_verifier.py
│   │   ├── triangular_verifier.py
│   │   ├── completions.json
│   │   └── training_curves.csv  # both verifiers, long-format
│   └── 03_filing_reasoning/
│       ├── verifier.py
│       ├── filings/           # pre-processed 10-K excerpts
│       ├── questions.json
│       └── completions.json
├── homework/                  # Westworld-style verifier exercise (see §11)
│   ├── README.md
│   ├── simulator.py           # Toy broker simulator + sample agents
│   ├── verifier_starter.py    # Four TODO stubs for the student
│   └── solution.py            # Reference implementation
├── data/                      # raw inputs (yfinance pulls, etc.)
└── notebooks/                 # exploratory work, not shipped
```

### Conventions

- **Verifiers are pure functions.** `verifier(prompt, completion) -> dict[str, float]`. No I/O, no side effects, no hidden state. This makes them testable and inspectable in the UI.
- **All visual data is pre-computed.** Every chart and example is backed by a static file under `examples/*/`. The app loads these synchronously on page entry.
- **Page modules are dumb.** A page module composes components and reads data files. Logic lives in `examples/*/` or `app/components/`.
- **No live model calls in the app.** If a future iteration adds them, gate behind a `--live` CLI flag and an API-key check.

---

## 7. Build Order

For Claude Code working through this from scratch:

1. **Skeleton first.** `app/main.py` with the sidebar and five empty pages. CSS variables wired in. Confirm visual baseline (off-white background, Inter loading, accent color rendering).
2. **Chart theme + components.** Build the four reusable components (`eyebrow`, `takeaway`, `verifier_card`, `training_curve`) against dummy data. These ship before any example logic.
3. **Example 1 end-to-end.** Verifier + cached data + page. This validates the whole vertical slice on the easiest case.
4. **Example 2.** This is the hardest one — the triangular verifier, the side-by-side training curves, the reasoning autopsy widget.
5. **Example 3.** Builds on the verifier patterns from Example 2; the new work is the chain-of-thought UI.
6. **Intro and recap pages.** Written *last*, once the examples have shaped the narrative.
7. **Polish pass.** Microcopy review, animation timing, mobile breakpoints (the app should at least not break on a phone — it won't be used there for the talk, but the repo is public).

---

## 8. Slide Mapping

For deck authoring, each slide section pulls directly from a section of this file:

| Slide section | Source |
|---|---|
| Title slide | §1.1 + §1.3 narrative arc |
| "What is RLVR" (3 slides) | §2.1, §2.2, §2.3 |
| "The three preconditions" | §2.4 |
| "Why finance is different" (4 slides) | §3.1, §3.2, §3.3, §3.4 |
| Example 1 walkthrough (3 slides) | §4.1 — premise, verifier, training dynamics |
| Example 2 walkthrough (5 slides) | §4.2 — premise, the failure, the fix, before/after, lesson |
| Example 3 walkthrough (4 slides) | §4.3 — premise, process verifier, generalization claim |
| Closing (1 slide) | §3.4 — "the verifier is the IP" |

Per-slide visuals should be screenshots of the corresponding Streamlit page where possible — this keeps the deck and the demo in lockstep.

---

## 9. Open Questions / Future Work

To revisit after the first version of the talk lands:

- Should Example 2's triangular verifier include a *learned* sub-verifier (e.g., a small classifier for reasoning quality), or stay fully rule-based for transparency? The pedagogical case argues rule-based.
- Is there an Example 4 worth adding on **long-context RLVR** (LongRLVR-style) for whole-filing reasoning? Probably yes for v2, but adds significant complexity.
- Should the app expose a "Roll your own verifier" sandbox where a viewer pastes a function and sees its training implications? High effort, high payoff for the right audience.

---

## 10. Tone & Voice (for any prose Claude writes in the app)

- Direct. Short sentences. Active voice.
- Quantitative when relevant; never quantitative for its own sake.
- No marketing register. No "powerful" or "cutting-edge" or "revolutionary."
- Assume the reader is technically literate but not necessarily an RL specialist. Define jargon the first time it appears.
- One bold takeaway sentence per page. Earn it.

---

## 11. Homework

A small, self-contained exercise that lives outside the talk narrative but reinforces its central thesis. Inspired by Halluminate's [Westworld](https://www.halluminate.ai/blog/westworld) — a suite of web-app simulators built to give web agents deterministic, reproducible rewards instead of live-site noise. The same idea transplants to a finance toy problem.

### 11.1 Premise

The student is given a deterministic in-memory broker simulator with three venues quoting one ticker, and is asked to buy 100 shares of ACME at the best total price. The student does *not* write the agent. The student writes the *verifier*.

```
Venue A:  40 shares @ $10.00
Venue B:  80 shares @ $10.05
Venue C: 200 shares @ $10.20

Optimal: 40 @ A + 60 @ B = $1,003.00
```

### 11.2 The task

Implement three sub-verifiers and one composite, mapped one-to-one to the three verification methods in the Westworld blog:

| Sub-verifier | Westworld analogue | What it checks |
|---|---|---|
| `state_verifier` | State-based unit test | Final shares held and cash spent match expectations exactly |
| `component_verifier` | Component-level verification | Each expected fill (venue, shares, price) appears in the fill log |
| `ground_truth_verifier` | Real-time calculated ground truth | Optimal cost is computed on the fly from the simulator's quotes, then compared to the agent's spend |
| `composite_reward` | — | Combine the three; the choice of combinator is itself the lesson |

Three sample agents — `agent_optimal`, `agent_lazy`, `agent_overbought` — drive scoring. A correct solution produces three meaningfully different composite rewards, with `optimal` clearly winning.

### 11.3 Pedagogical point

The reference solution uses geometric mean for the composite. The interesting case is `agent_lazy`, which scores ~0.98 on `ground_truth_verifier` in isolation (bought the right quantity, overpaid only ~1.7%) but collapses to 0.0 in the composite because the state and component checks both fail. This is the same lesson Example 2 makes about reward hacking: a single permissive sub-verifier is not enough. The *composition* of verifiers is where hacking gets closed off.

The discussion questions in `homework/README.md` push further:

1. Which sub-verifier *almost* misses `agent_lazy`, and what does that say about choosing a combinator?
2. If an adversarial agent forges `BrokerState` directly without calling `Simulator.submit()`, which sub-verifier still catches it? (The answer: `component_verifier`, since the fills list will be empty — illustrating that *where you put the source of truth* matters more than the verifier code itself.)
3. What is the analogous "simulator" in Example 2 (trade signals), and why is it harder to build there?

### 11.4 Layout

```
homework/
├── README.md              Problem statement + discussion questions
├── simulator.py           Quote, Fill, BrokerState, Simulator, sample agents
├── verifier_starter.py    Four TODO stubs; runnable as-is (prints zeros)
└── solution.py            Reference implementation
```

The homework is independent of the Streamlit app and the examples — no shared imports, no installation step beyond a standard Python 3.10+ runtime.

---

*End of CLAUDE.md. If you are extending this project, update the relevant section here before writing code.*
