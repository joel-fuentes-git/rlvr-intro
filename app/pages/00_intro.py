"""Page: What is RLVR?"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from components import eyebrow, takeaway  # noqa: E402

eyebrow("Introduction")
st.title("What is RLVR?")
st.markdown(
    '<p class="subtitle">RLVR — Reinforcement Learning with Verifiable Rewards — '
    "is the technique that powers DeepSeek-R1 and the modern reasoning-model wave. "
    "The single change is the reward function.</p>",
    unsafe_allow_html=True,
)

st.markdown("## The one-line definition")
st.markdown(
    "RLVR trains a language model to maximize a reward signal computed by a "
    "**deterministic, programmatic verifier** — not by a learned reward model "
    "trained on human preferences."
)

st.markdown("## Why this matters")
c1, c2 = st.columns(2)
with c1:
    st.markdown(
        '<div class="card">'
        '<div class="eyebrow" style="margin-bottom:8px;">Pre-RLVR · the RLHF era</div>'
        "Reward came from a learned model trained on human preference pairs. "
        "Expensive, noisy, easy to game, capped by labeler quality."
        "</div>",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        '<div class="card">'
        '<div class="eyebrow" style="margin-bottom:8px;">Post-RLVR</div>'
        "Reward comes from a function. For math, <code>answer == expected</code>. "
        "For code, <code>tests_pass(generated_code)</code>. The signal is cheap, "
        "scalable, and — within its domain — uncheatable."
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    "DeepSeek-R1, the open-weights reasoning model that catalyzed the shift, "
    "was trained predominantly with verifiable rewards on math and code. "
    "The reasoning ability *transferred* to many other domains the model "
    "was never explicitly trained on."
)

st.markdown("## The canonical algorithm: GRPO")
st.markdown(
    "**Group Relative Policy Optimization** is the workhorse RL algorithm "
    "behind most modern RLVR systems. The intuition:"
)
st.markdown(
    """
1. For a given prompt, sample **G** candidate completions from the current policy.
2. Score each one with the verifier → group of rewards `r_1 ... r_G`.
3. Compute *relative* advantages: each completion's reward minus the group mean,
   divided by the group standard deviation.
4. Update the policy to up-weight tokens in above-average completions and
   down-weight tokens in below-average ones.
5. Add a KL penalty against a reference policy to prevent catastrophic drift.
"""
)
st.markdown(
    "GRPO eliminates the value function — group statistics replace it. "
    "This is what makes RLVR cheap enough to run on a single 8×H100 node "
    "for small models."
)

st.markdown("## The three preconditions")
st.markdown(
    "Every advanced RLVR technique exists because one of these three broke."
)

p1, p2, p3 = st.columns(3)
p1.markdown(
    '<div class="card"><strong>1. Verifiability</strong>'
    '<p style="color:var(--ink-soft); font-size:14px; margin-top:8px;">'
    "There must be a programmatic check for &quot;correct.&quot;</p></div>",
    unsafe_allow_html=True,
)
p2.markdown(
    '<div class="card"><strong>2. Density</strong>'
    '<p style="color:var(--ink-soft); font-size:14px; margin-top:8px;">'
    "Among G samples, at least some must be correct, "
    "or there is no signal to learn from.</p></div>",
    unsafe_allow_html=True,
)
p3.markdown(
    '<div class="card"><strong>3. Faithfulness</strong>'
    '<p style="color:var(--ink-soft); font-size:14px; margin-top:8px;">'
    "The verifier must reward the property you actually care about, "
    "not a proxy that can be hacked.</p></div>",
    unsafe_allow_html=True,
)

st.markdown("## Why finance is the hardest domain")
st.markdown(
    "Math has `4 == 4`. Code has `assert tests_pass()`. Finance has:"
)
st.markdown(
    """
- *Was that trade good?* — depends on holding period, benchmark, regime,
  cost of capital, and what else you could have done with the money.
- *Was that risk assessment correct?* — won't know until either the tail
  event happens or it doesn't, and the absence of a tail event doesn't
  validate the model.
- *Was that earnings interpretation right?* — often depends on subsequent
  quarters of data not yet available.
"""
)
st.markdown(
    "Most things finance professionals get paid to do are not cleanly "
    "verifiable on the timescales over which a model trains. "
    "The next three pages walk through what happens when you try anyway."
)

takeaway(
    "RLVR is GRPO plus a verifier. In finance, designing the verifier "
    "is the research problem."
)

st.markdown(
    '<div class="page-nav">'
    '<span></span>'
    '<span>Where RLVR Just Works →</span>'
    '</div>',
    unsafe_allow_html=True,
)
