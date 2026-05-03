"""Takeaway block — the bold one-sentence callout per page."""

from __future__ import annotations

import streamlit as st


def takeaway(sentence: str) -> None:
    st.markdown(f'<div class="takeaway">{sentence}</div>', unsafe_allow_html=True)
