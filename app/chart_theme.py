"""Minimal Plotly theme for the RLVR explainer.

Registers a `rlvr` template with no gridlines, no legend chrome, soft axis labels,
and a single accent color for default series. Helpers below return pre-themed figures
for the chart types used in the app.
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

INK = "#1A1A1A"
INK_SOFT = "#5A5A5A"
RULE = "#E8E6E0"
ACCENT = "#1F6FEB"
GOOD = "#2D7A4F"
BAD = "#B8341F"
BG = "#FAFAF7"
SURFACE = "#FFFFFF"


def _register_template() -> None:
    template = go.layout.Template(
        layout=go.Layout(
            font=dict(family="Inter, sans-serif", size=13, color=INK),
            paper_bgcolor=BG,
            plot_bgcolor=BG,
            colorway=[ACCENT, BAD, GOOD, "#8A6818", "#5A5A5A"],
            margin=dict(l=48, r=24, t=24, b=48),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=True,
                linecolor=RULE,
                linewidth=1,
                ticks="outside",
                tickcolor=RULE,
                tickfont=dict(color=INK_SOFT, size=11, family="JetBrains Mono"),
                title=dict(font=dict(color=INK_SOFT, size=12)),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=RULE,
                gridwidth=1,
                zeroline=False,
                showline=False,
                ticks="",
                tickfont=dict(color=INK_SOFT, size=11, family="JetBrains Mono"),
                title=dict(font=dict(color=INK_SOFT, size=12)),
            ),
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,0,0,0)",
                font=dict(size=12, color=INK_SOFT),
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
            ),
            hoverlabel=dict(
                bgcolor=SURFACE,
                bordercolor=RULE,
                font=dict(family="JetBrains Mono", size=12, color=INK),
            ),
        )
    )
    pio.templates["rlvr"] = template
    pio.templates.default = "rlvr"


_register_template()


def empty_figure(height: int = 320) -> go.Figure:
    """Return a fresh figure with the rlvr template applied."""
    fig = go.Figure()
    fig.update_layout(template="rlvr", height=height)
    return fig
