# Homework — a Westworld-style verifier

> **Inspired by:** Halluminate's [Westworld](https://www.halluminate.ai/blog/westworld), a suite of web-app simulators built so that web agents can be evaluated under deterministic, reproducible rewards instead of live-site noise.

## The premise

Westworld's insight is that you cannot reliably verify a web agent against a live website — pages change, login walls appear, scraping fails. The fix is to build a simulator and verify against its observable state. The same trick transplants to finance: you cannot verify a trading agent against live markets cheaply or repeatably. So we will do it on a tiny scale.

You will work with a deterministic toy "broker simulator." It has three venues with different quotes for one ticker. An agent's job is to buy 100 shares at the best total price. Your job is to write the verifier.

```
Venue A:  40 shares @ $10.00
Venue B:  80 shares @ $10.05
Venue C: 200 shares @ $10.20
```

Optimal routing: 40 @ A + 60 @ B = **$1,003.00**.

## The task

In `verifier_starter.py`, implement three sub-verifiers and one composite. Each maps directly to a verification method from the Westworld blog:

1. **`state_verifier(sim)`** — *State-based unit test.* Did the agent leave the simulator in exactly the expected state? (Right share count, right total cash spent.) Returns one number.
2. **`component_verifier(sim)`** — *Component-level check.* For each expected fill, was the venue, share count, and price as expected? Returns a dict of per-component scores.
3. **`ground_truth_verifier(sim)`** — *Real-time computed ground truth.* Query the simulator's own quotes to compute the optimal routing, then score the agent's cost relative to optimal. Returns one number.
4. **`composite_reward(sim)`** — combine the three into one final reward in [0, 1]. (Min? Geometric mean? Weighted sum? Your call — the choice is itself a design decision. Explain it in a comment.)

`simulator.py` provides three sample agents — `agent_optimal`, `agent_lazy`, `agent_overbought`. Run

```bash
python verifier_starter.py
```

to score each one against your verifier.

## What "done" looks like

When all three sample agents produce *meaningfully different* composite rewards under your verifier — and `agent_optimal` clearly wins — you're done. A reference implementation lives in `solution.py`. Try not to peek.

## Discussion (3–5 sentences each)

1. Which sub-verifier catches `agent_lazy`? Which one *almost* doesn't, and why is that informative about choosing a composite function?
2. Suppose an adversarial agent forges its own `BrokerState` directly without calling `Simulator.submit()` — e.g., sets `shares_held = 100` and `cash_spent = 1003.00` with no fills. Which sub-verifier still catches it? Which now passes incorrectly? What does that tell you about where to put the source of truth?
3. Westworld can use ground-truth verification because the simulator *is* the source of truth. What is the analogous "simulator" in this repo's Example 2 (trade signals), and why is it harder to build there?

## The takeaway

> **The verifier is not what scores the agent. The simulator is.** The verifier just reads the simulator's state. Once you accept that, the engineering load shifts to building simulators whose state cleanly exposes the property you actually care about.
