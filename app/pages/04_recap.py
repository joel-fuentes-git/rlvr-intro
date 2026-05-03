"""Page: The Verifier is the IP — recap."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from components import eyebrow, takeaway  # noqa: E402

eyebrow("Recap")
st.title("The Verifier is the IP")
st.markdown(
    '<p class="subtitle">Three examples, one argument: the choice of model, '
    "algorithm, and compute budget are secondary. The verifier is the "
    "design problem.</p>",
    unsafe_allow_html=True,
)

st.markdown("## What we saw")

c1, c2, c3 = st.columns(3)
c1.markdown(
    '<div class="card">'
    '<div class="eyebrow" style="margin-bottom:8px;">Example 1 · Bond pricing</div>'
    "<strong>Where RLVR just works.</strong>"
    '<p style="font-size:14px; color:var(--ink-soft); margin-top:8px;">'
    "Closed-form answer, ten-line verifier, dense reward signal. "
    "GRPO converges cleanly."
    "</p></div>",
    unsafe_allow_html=True,
)
c2.markdown(
    '<div class="card">'
    '<div class="eyebrow" style="margin-bottom:8px;">Example 2 · Trade signals</div>'
    "<strong>Where RLVR breaks.</strong>"
    '<p style="font-size:14px; color:var(--ink-soft); margin-top:8px;">'
    "Forward return is a noisy, hackable proxy. The model converges to "
    "fluent momentum-chasing prose. Triangular verification fixes it."
    "</p></div>",
    unsafe_allow_html=True,
)
c3.markdown(
    '<div class="card">'
    '<div class="eyebrow" style="margin-bottom:8px;">Example 3 · Filing reasoning</div>'
    "<strong>The frontier.</strong>"
    '<p style="font-size:14px; color:var(--ink-soft); margin-top:8px;">'
    "When the answer is a chain, verify the chain. Process verifiers "
    "let small models do hard work."
    "</p></div>",
    unsafe_allow_html=True,
)

st.markdown("## The pattern")
st.markdown(
    "Each example introduced a problem the previous one couldn't show:"
)
st.markdown(
    """
| | Verifiability | Density | Faithfulness |
|---|---|---|---|
| **Bond pricing** | clean | high | clean |
| **Trade signals (naive)** | clean | low | **broken** |
| **Trade signals (triangular)** | clean | medium | recovered |
| **Filing reasoning (process)** | clean per-step | high per-step | recovered |
"""
)

st.markdown("## The implication for practitioners")

st.markdown(
    """
- **Don't pick a model and then go look for a verifier.** Pick the verifier
  first; the model choice falls out of it.
- **Outcome-only verifiers are a trap in any domain where the outcome is noisy.**
  Decompose them.
- **Process verifiers look like data engineering, not RL research.** That's
  the work. A small model with a great verifier beats a great model with
  a noisy one.
- **The verifier is your IP.** It encodes the judgment a human analyst
  would apply. It is the asset that compounds.
"""
)

takeaway(
    "In finance, the model is a commodity. The verifier is the moat."
)

st.markdown("## Want to go deeper")
st.markdown(
    "- The Trade-R1 paper for the triangular-verifier idea.\n"
    "- MR-RLVR and K2V for process supervision.\n"
    "- DeepSeek-R1 for the reference RLVR pipeline at scale.\n"
    "- This repo's `examples/` directory — every verifier here is a pure "
    "function you can read in five minutes."
)

st.markdown(
    '<div class="page-nav">'
    '<span>← The Frontier</span>'
    '<span></span>'
    '</div>',
    unsafe_allow_html=True,
)
