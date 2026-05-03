"""Page: The Frontier — process verifiers for 10-K reasoning."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from components import eyebrow, load_example, takeaway, verifier_card  # noqa: E402

verifier_mod = load_example("03_filing_reasoning", "verifier")
data_mod = load_example("03_filing_reasoning", "data")


eyebrow("Example 3 of 3 · The frontier")
st.title("The Frontier")
st.markdown(
    '<p class="subtitle">When the answer is a chain of reasoning, the verifier '
    "should verify the chain. Each step gets its own sub-reward.</p>",
    unsafe_allow_html=True,
)

st.markdown("## The setup")
st.markdown(
    "The model is given a 10-K excerpt and a multi-step question. It responds in "
    "a small structured DSL that exposes its reasoning to verification:"
)

st.code(
    """EXTRACT  <key> = <value>            # pull a number from the filing
COMPUTE  <key> = <expr>             # arithmetic over already-extracted keys
CITE     <key> -> <source_id>       # attach a source pointer
CONCLUDE: <natural language>        # final answer""",
    language="text",
)

st.markdown(
    "Four sub-verifiers — extraction, calculation, citation, final answer — "
    "evaluate the chain. The composite reward is a weighted sum, so a "
    "curriculum can shift weight from extraction (early) to final answer (late)."
)

st.markdown("## The question")
st.markdown(f'<div class="card">{data_mod.QUESTION_TEXT}</div>',
            unsafe_allow_html=True)

with st.expander("The filing the model can extract from"):
    rows = "<br/>".join(
        f"{k} = {v}  &nbsp; <span style='color:var(--ink-soft)'>"
        f"({data_mod.APPLE_SOURCES.get(k, '—')})</span>"
        for k, v in data_mod.APPLE_FILING.items()
    )
    st.markdown(f"<div class='mono' style='line-height:1.8'>{rows}</div>",
                unsafe_allow_html=True)

st.markdown("## Try this")
st.markdown(
    "Choose a sample completion and re-weight the sub-verifiers. "
    "Watch which completion the policy gradient would prefer."
)

choice = st.radio(
    "Sample completion",
    options=[
        "Grounded (follows the protocol, real numbers)",
        "Hacked (follows the protocol, fake numbers)",
        "Prose only (just a CONCLUDE line)",
    ],
    index=0,
)

if choice.startswith("Grounded"):
    completion = data_mod.COMPLETION_GROUNDED
elif choice.startswith("Hacked"):
    completion = data_mod.COMPLETION_HACKED
else:
    completion = data_mod.COMPLETION_PROSE

st.markdown("**Verifier weights**")
c1, c2, c3, c4 = st.columns(4)
w_e = c1.slider("Extraction", 0.0, 1.0, 0.25, 0.05)
w_c = c2.slider("Calculation", 0.0, 1.0, 0.25, 0.05)
w_ci = c3.slider("Citation", 0.0, 1.0, 0.20, 0.05)
w_f = c4.slider("Final answer", 0.0, 1.0, 0.30, 0.05)

editable = st.text_area("Completion", value=completion, height=240)

question = verifier_mod.Question(
    text=data_mod.QUESTION_TEXT,
    filing=data_mod.APPLE_FILING,
    sources=data_mod.APPLE_SOURCES,
    expected_answer_keywords=data_mod.EXPECTED_KEYWORDS,
)

result = verifier_mod.verifier(
    question, editable, weights=(w_e, w_c, w_ci, w_f),
)

st.markdown("### Sub-verifier breakdown")
verifier_card(
    "Extraction", "Cited values match the filing within tolerance.",
    score=result.extraction,
)
verifier_card(
    "Calculation", "Arithmetic on extracted keys evaluates without error.",
    score=result.calculation,
)
verifier_card(
    "Citation", "Each cited key points to the correct source identifier.",
    score=result.citation,
)
verifier_card(
    "Final answer", "Conclusion mentions the expected concepts.",
    score=result.final,
)
verifier_card(
    "Composite (weighted)", "The single number that becomes the policy gradient.",
    score=result.reward,
)

st.markdown("### Step-by-step trace")
trace_html = ['<div class="card mono" style="font-size:13px; line-height:1.8;">']
for s in result.steps:
    color = "var(--good)" if s.ok else "var(--bad)"
    glyph = "✓" if s.ok else "✗"
    note = (f" <span style='color:var(--ink-soft); font-family:Inter;"
            f" font-size:12px;'>— {s.note}</span>") if s.note else ""
    trace_html.append(
        f'<div><span style="color:{color}; font-weight:600;">{glyph}</span> '
        f'<span style="color:var(--ink-soft); font-size:11px; '
        f'text-transform:uppercase; letter-spacing:0.08em;">{s.kind}</span> '
        f"{s.raw}{note}</div>"
    )
trace_html.append("</div>")
st.markdown("\n".join(trace_html), unsafe_allow_html=True)

takeaway(
    "Once you have process verifiers, the model can be small. "
    "The intelligence moves into the verifier — and that's where the IP lives."
)

st.markdown(
    '<div class="page-nav">'
    '<span>← Where RLVR Breaks</span>'
    '<span>The Verifier is the IP →</span>'
    '</div>',
    unsafe_allow_html=True,
)
