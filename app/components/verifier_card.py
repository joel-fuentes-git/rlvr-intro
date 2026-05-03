"""Verifier sub-score card.

Renders a row showing one sub-verifier's name, description, and score.
The card lights up green / red / amber based on the score crossing thresholds.
"""

from __future__ import annotations

import streamlit as st


def _state(score: float, pass_threshold: float, partial_threshold: float) -> str:
    if score >= pass_threshold:
        return "pass"
    if score >= partial_threshold:
        return "partial"
    return "fail"


def verifier_card(
    label: str,
    description: str,
    score: float,
    *,
    pass_threshold: float = 0.8,
    partial_threshold: float = 0.4,
) -> None:
    state = _state(score, pass_threshold, partial_threshold)
    st.markdown(
        f"""
<div class="verifier-card {state}">
  <div>
    <div class="label">{label}</div>
    <div class="desc">{description}</div>
  </div>
  <div class="score">{score:.2f}</div>
</div>
""",
        unsafe_allow_html=True,
    )
