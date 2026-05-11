"""RLVR for Finance — Streamlit app entry point.

Sidebar nav drives a five-page narrative. Pages are pure modules under app/pages/.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from chart_theme import _register_template

st.set_page_config(
    page_title="RLVR for Finance",
    page_icon="•",
    layout="wide",
    initial_sidebar_state="expanded",
)

_register_template()


def _inject_styles() -> None:
    css_path = Path(__file__).parent / "styles.css"
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


_inject_styles()


PAGES_DIR = Path(__file__).parent / "pages"

PAGES = [
    st.Page(str(PAGES_DIR / "00_intro.py"), title="What is RLVR?", default=True),
    st.Page(str(PAGES_DIR / "01_bond_pricing.py"), title="Where RLVR Just Works"),
    st.Page(str(PAGES_DIR / "02_trade_signals.py"), title="Where RLVR Breaks"),
    st.Page(str(PAGES_DIR / "03_filing_reasoning.py"), title="The Frontier"),
    st.Page(str(PAGES_DIR / "04_recap.py"), title="The Verifier is the IP"),
]


with st.sidebar:
    st.markdown(
        """
<div style="padding: 8px 0 24px 0;">
  <div style="font-family:'JetBrains Mono',monospace; font-size:11px;
              text-transform:uppercase; letter-spacing:0.12em;
              color: var(--ink-soft); margin-bottom:8px;">
    RLVR for Finance
  </div>
  <div style="font-size:14px; color: var(--ink-soft); line-height:1.5;">
    An interactive primer
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

nav = st.navigation(PAGES, position="sidebar")

with st.sidebar:
    st.markdown("---")
    st.markdown(
        """
<div style="font-size:12px; color: var(--ink-soft); line-height:1.6;">
Pedagogical artifact — not a training pipeline, not financial advice.
</div>
        """,
        unsafe_allow_html=True,
    )

nav.run()
