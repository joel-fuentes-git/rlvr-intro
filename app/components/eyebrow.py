"""Eyebrow label — the small uppercase tag above each page title."""

from __future__ import annotations

import streamlit as st


def eyebrow(text: str) -> None:
    st.markdown(f'<div class="eyebrow">{text}</div>', unsafe_allow_html=True)
