"""Page: Where RLVR Just Works — bond pricing."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Make ``app/`` importable when Streamlit runs this page.
APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from components import eyebrow, load_example, takeaway, training_curve  # noqa: E402

verifier_mod = load_example("01_bond_pricing", "verifier")
data_mod = load_example("01_bond_pricing", "data")


eyebrow("Example 1 of 3 · The easy case")
st.title("Where RLVR Just Works")
st.markdown(
    '<p class="subtitle">A vanilla coupon bond has a closed-form price. '
    "The verifier is ten lines of Python. RLVR converges cleanly.</p>",
    unsafe_allow_html=True,
)

st.markdown("## The verifier")
st.markdown(
    "The reward signal is just the analytical bond price plus a tolerance check. "
    "There is no judgment call, no learned reward model, no human in the loop."
)

st.code(
    '''def analytical_price(b: BondInputs) -> float:
    periods = b.years * b.freq
    period_rate = b.ytm / b.freq
    coupon = b.face * b.coupon_rate / b.freq
    pv_coupons = sum(coupon / (1 + period_rate) ** t
                     for t in range(1, periods + 1))
    pv_face = b.face / (1 + period_rate) ** periods
    return pv_coupons + pv_face


def verifier(inputs, completion, *, tolerance=0.01):
    truth = analytical_price(inputs)
    guess = _extract_final_number(completion)
    rel_err = abs(guess - truth) / abs(truth)
    return {"reward": 1.0 if rel_err <= tolerance else max(0, 1 - rel_err / 0.10)}''',
    language="python",
)

st.markdown("## Training dynamics")
st.markdown(
    "Reward climbs through a logistic curve as the policy discovers the "
    "discount-and-sum structure. The density metric — the fraction of sampled "
    "completions earning > 0.5 reward — is the diagnostic that tells you "
    "RLVR has signal to learn from."
)

col1, col2 = st.columns(2)
with col1:
    fig = training_curve(data_mod.training_curve_df(), y_label="Mean reward")
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
with col2:
    fig2 = training_curve(
        data_mod.density_curve_df(),
        y="density",
        y_label="Fraction of completions with reward > 0.5",
    )
    st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

st.markdown("## A sample, before and after training")
st.markdown(f'<div class="card mono">{data_mod.SAMPLE_PROMPT}</div>',
            unsafe_allow_html=True)

inputs = verifier_mod.BondInputs(**data_mod.SAMPLE_INPUTS)
truth = verifier_mod.analytical_price(inputs)
before_score = verifier_mod.verifier(inputs, data_mod.COMPLETION_BEFORE)
after_score = verifier_mod.verifier(inputs, data_mod.COMPLETION_AFTER)

c1, c2 = st.columns(2)
with c1:
    st.markdown(
        f'<div class="completion before">'
        f'<span class="label">Before training · reward = {before_score["reward"]:.2f}</span>\n'
        f'{data_mod.COMPLETION_BEFORE}</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        f"Extracted ${before_score['extracted']:.2f} · "
        f"truth ${truth:.2f} · "
        f"relative error {before_score['relative_error']:.1%}"
    )

with c2:
    st.markdown(
        f'<div class="completion after">'
        f'<span class="label">After training · reward = {after_score["reward"]:.2f}</span>\n'
        f'{data_mod.COMPLETION_AFTER}</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        f"Extracted ${after_score['extracted']:.2f} · "
        f"truth ${truth:.2f} · "
        f"relative error {after_score['relative_error']:.2%}"
    )

st.markdown("## Try this")
st.markdown("Adjust the bond inputs and a candidate answer; watch the reward respond.")

c1, c2, c3, c4, c5 = st.columns(5)
face = c1.number_input("Face", value=1000.0, step=100.0, format="%.2f")
coupon_rate = c2.number_input("Coupon", value=0.05, step=0.005, format="%.3f")
ytm = c3.number_input("YTM", value=0.06, step=0.005, format="%.3f")
years = c4.number_input("Years", value=5, step=1, min_value=1, max_value=30)
freq = c5.selectbox("Coupons / yr", [1, 2], index=0)

candidate = st.text_input(
    "Candidate completion (we extract the last number as the answer)",
    value="My answer is 957.88",
)

inputs = verifier_mod.BondInputs(
    face=float(face),
    coupon_rate=float(coupon_rate),
    ytm=float(ytm),
    years=int(years),
    freq=int(freq),
)
result = verifier_mod.verifier(inputs, candidate)
truth = verifier_mod.analytical_price(inputs)

m1, m2, m3 = st.columns(3)
m1.markdown(
    f'<div class="kpi"><div class="label">Analytical price</div>'
    f'<div class="value">${truth:,.2f}</div></div>',
    unsafe_allow_html=True,
)
extracted = result["extracted"]
extracted_str = f"{extracted:,.2f}" if extracted == extracted else "—"  # NaN check
m2.markdown(
    f'<div class="kpi"><div class="label">Extracted answer</div>'
    f'<div class="value">{extracted_str}</div></div>',
    unsafe_allow_html=True,
)
m3.markdown(
    f'<div class="kpi"><div class="label">Reward</div>'
    f'<div class="value">{result["reward"]:.2f}</div></div>',
    unsafe_allow_html=True,
)

takeaway(
    "When the verifier is a function and the answer is a number, "
    "RLVR is a solved problem."
)

st.markdown(
    '<div class="page-nav">'
    '<span>← What is RLVR?</span>'
    '<span>Where RLVR Breaks →</span>'
    '</div>',
    unsafe_allow_html=True,
)
