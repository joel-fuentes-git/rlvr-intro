"""Page: Where RLVR Breaks — trade signal generation."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from components import eyebrow, load_example, takeaway, training_curve, verifier_card  # noqa: E402

naive = load_example("02_trade_signals", "naive_verifier")
triangular = load_example("02_trade_signals", "triangular_verifier")
data_mod = load_example("02_trade_signals", "data")


eyebrow("Example 2 of 3 · The hard case")
st.title("Where RLVR Breaks")
st.markdown(
    '<p class="subtitle">A naive verifier that rewards "did the trade make money" '
    "looks reasonable. It produces a model that hallucinates technicals, "
    "chases momentum, and can't be deployed.</p>",
    unsafe_allow_html=True,
)

st.markdown("## The naive setup")
st.markdown(
    "Show the model market context for a stock; ask for BUY / HOLD / SELL with "
    "a reasoning chain. Reward = forward 21-day excess return, signed by the decision."
)

st.code(
    """def verifier(ctx, completion):
    decision = _extract_decision(completion)   # BUY / SELL / HOLD
    ret = ctx.forward_excess_return            # the next 21 days, post hoc
    raw = ret if decision == "BUY" else -ret if decision == "SELL" else 0
    return {"reward": clip(raw * 10, -1, 1)}""",
    language="python",
)

st.markdown(
    "Honest verifier. Honest reward. **Useless gradient.** Excess return is "
    "noise-dominated on a 21-day horizon. With a large enough model and enough "
    "training, the policy converges to the cheapest signal it can find — usually "
    "*confident momentum-chasing prose that doesn't engage with the data*."
)

st.markdown("## Naive vs. triangular: training dynamics")

curves_df = data_mod.training_curves_df()
fig = training_curve(
    curves_df,
    series="verifier",
    series_colors={"naive": "#B8341F", "triangular": "#2D7A4F"},
    y_label="Mean reward (rolling)",
    height=360,
)
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
st.caption(
    "Naive (red) is jittery and barely climbs — the noise wall. "
    "Triangular (green) climbs cleanly and plateaus higher because every component "
    "of the reward carries information that isn't pure noise."
)

st.markdown("## The fix: triangular verification")
st.markdown(
    "Decompose the reward into three sub-verifiers and combine via geometric mean. "
    "A reward-hacking strategy fails one of the first two regardless of the third."
)

c1, c2, c3 = st.columns(3)
c1.markdown(
    '<div class="card"><strong>Evidence</strong>'
    '<p style="color:var(--ink-soft); font-size:14px;">Do the cited numbers '
    "actually appear in the input?</p></div>",
    unsafe_allow_html=True,
)
c2.markdown(
    '<div class="card"><strong>Reasoning</strong>'
    '<p style="color:var(--ink-soft); font-size:14px;">Does the chain '
    "logically connect evidence to conclusion?</p></div>",
    unsafe_allow_html=True,
)
c3.markdown(
    '<div class="card"><strong>Outcome</strong>'
    '<p style="color:var(--ink-soft); font-size:14px;">Did the trade make '
    "money? (The original noisy signal — now down-weighted.)</p></div>",
    unsafe_allow_html=True,
)

st.markdown("## Reasoning autopsy")
st.markdown(
    "Pick a sample completion and watch the sub-verifiers light up. The naive "
    "verifier rewards both. The triangular verifier separates them."
)

ctx = triangular.TradeContext(**data_mod.DEMO_CONTEXT)

choice = st.radio(
    "Sample completion",
    options=["Hacked (momentum hand-wave)", "Grounded (cites the data)"],
    horizontal=True,
)

completion = (
    data_mod.HACKED_COMPLETION if choice.startswith("Hacked")
    else data_mod.GROUNDED_COMPLETION
)

cls = "before" if choice.startswith("Hacked") else "after"
st.markdown(
    f'<div class="completion {cls}">'
    f'<span class="label">Model output</span>\n{completion}</div>',
    unsafe_allow_html=True,
)

# Naive verifier — same forward return for both
naive_ctx = naive.MarketContext(
    ticker=ctx.ticker, forward_excess_return=ctx.forward_excess_return,
)
naive_score = naive.verifier(naive_ctx, completion)

st.markdown("**Naive verifier (one number)**")
verifier_card(
    "Outcome only",
    "Forward 21-day excess return, signed by the BUY/SELL/HOLD decision.",
    score=max(0.0, (naive_score["reward"] + 1) / 2),  # display as 0-1
    pass_threshold=0.7, partial_threshold=0.45,
)

st.markdown("**Triangular verifier (three numbers, geometric mean)**")
tri_score = triangular.verifier(ctx, completion)
verifier_card(
    "Evidence",
    "Fraction of cited numbers that match the input data within 1%.",
    score=tri_score["evidence"],
)
verifier_card(
    "Reasoning",
    "Connectives, cited numbers, and an explicit decision are all present.",
    score=tri_score["reasoning"],
)
verifier_card(
    "Outcome",
    "Did the position move in the predicted direction over 21 days?",
    score=tri_score["outcome"],
)
verifier_card(
    "Composite (geometric mean)",
    "All three must be high for the composite to be high. Hacking one isn't enough.",
    score=tri_score["reward"],
)

st.markdown("## Try this")
st.markdown(
    "Edit a completion and watch the sub-scores update. Try citing numbers "
    "that aren't in the data, or stripping the reasoning chain entirely."
)

edited = st.text_area(
    "Completion to score",
    value=data_mod.GROUNDED_COMPLETION,
    height=120,
)

with st.expander("Allowed facts (the data the model was given)"):
    facts = ctx.cited_facts
    st.markdown(
        "<div class='mono' style='line-height:1.8'>"
        + "<br/>".join(f"{k} = {v}" for k, v in facts.items())
        + f"<br/>forward_excess_return (held out) = {ctx.forward_excess_return:+.2%}"
        + "</div>",
        unsafe_allow_html=True,
    )

live = triangular.verifier(ctx, edited)
m1, m2, m3, m4 = st.columns(4)
for col, key, label in [
    (m1, "evidence", "Evidence"),
    (m2, "reasoning", "Reasoning"),
    (m3, "outcome", "Outcome"),
    (m4, "reward", "Composite"),
]:
    col.markdown(
        f'<div class="kpi"><div class="label">{label}</div>'
        f'<div class="value">{live[key]:.2f}</div></div>',
        unsafe_allow_html=True,
    )

takeaway(
    "In finance, the verifier is the research problem. "
    "If your reward is hackable, the better your model the worse your outcome."
)

st.markdown(
    '<div class="page-nav">'
    '<span>← Where RLVR Just Works</span>'
    '<span>The Frontier →</span>'
    '</div>',
    unsafe_allow_html=True,
)
