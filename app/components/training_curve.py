"""Animated reward-over-steps chart."""

from __future__ import annotations

from typing import Iterable

import pandas as pd
import plotly.graph_objects as go

from chart_theme import ACCENT, BAD, GOOD, INK_SOFT, RULE, empty_figure

_PALETTE = {
    "accent": ACCENT,
    "bad": BAD,
    "good": GOOD,
    "soft": INK_SOFT,
}


def training_curve(
    df: pd.DataFrame,
    *,
    x: str = "step",
    y: str = "reward",
    series: str | None = None,
    series_colors: dict[str, str] | None = None,
    y_label: str = "Mean reward",
    x_label: str = "Training step",
    height: int = 320,
    y_range: tuple[float, float] | None = None,
    show_smoothed: bool = True,
    smoothing_window: int = 10,
) -> go.Figure:
    """Render a training curve.

    If ``series`` is provided, plot one line per unique value of that column.
    Otherwise plot a single series.
    """
    fig = empty_figure(height=height)

    if series is None:
        _add_line(fig, df[x], df[y], color=ACCENT, name=y_label,
                  show_smoothed=show_smoothed, window=smoothing_window)
    else:
        names: Iterable[str] = df[series].unique()
        for name in names:
            sub = df[df[series] == name]
            color = (series_colors or {}).get(name)
            if color is None:
                color = _PALETTE.get(name.lower(), ACCENT)
            _add_line(fig, sub[x], sub[y], color=color, name=name,
                      show_smoothed=show_smoothed, window=smoothing_window)

    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        showlegend=series is not None,
    )
    if y_range is not None:
        fig.update_yaxes(range=list(y_range))

    return fig


def _add_line(
    fig: go.Figure,
    xs,
    ys,
    *,
    color: str,
    name: str,
    show_smoothed: bool,
    window: int,
) -> None:
    if show_smoothed and len(ys) > window:
        smoothed = pd.Series(ys.values).rolling(window, min_periods=1).mean()
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys,
                mode="lines",
                line=dict(color=color, width=1),
                opacity=0.25,
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=xs, y=smoothed,
                mode="lines",
                line=dict(color=color, width=2.5),
                name=name,
            )
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys,
                mode="lines",
                line=dict(color=color, width=2.5),
                name=name,
            )
        )
