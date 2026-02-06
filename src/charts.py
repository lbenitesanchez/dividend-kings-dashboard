from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def price_chart(prices: pd.DataFrame, title: str) -> go.Figure:
    if prices is None or prices.empty:
        fig = go.Figure()
        fig.update_layout(title=title, height=300)
        return fig
    fig = px.line(prices, x="Date", y="Close", title=title)
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def dividend_history_chart(dividends: pd.Series, title: str) -> go.Figure:
    if dividends is None or dividends.empty:
        fig = go.Figure()
        fig.update_layout(title=title, height=300)
        return fig
    df = dividends.reset_index()
    df.columns = ["Date", "Dividend"]
    fig = px.bar(df, x="Date", y="Dividend", title=title)
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def annual_dividends_chart(annual: pd.DataFrame, title: str) -> go.Figure:
    if annual is None or annual.empty:
        fig = go.Figure()
        fig.update_layout(title=title, height=300)
        return fig
    fig = px.bar(annual, x="year", y="dividends", title=title)
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def financials_chart(statement: Optional[pd.DataFrame], row: str, title: str) -> go.Figure:
    if statement is None or statement.empty or row not in statement.index:
        fig = go.Figure()
        fig.update_layout(title=title, height=300)
        return fig
    series = statement.loc[row].dropna().sort_index()
    df = pd.DataFrame({"Date": series.index, "Value": series.values})
    fig = px.bar(df, x="Date", y="Value", title=title)
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def multi_series_chart(df: pd.DataFrame, title: str) -> go.Figure:
    if df is None or df.empty:
        fig = go.Figure()
        fig.update_layout(title=title, height=300)
        return fig
    fig = px.line(df, x="Date", y="Value", color="Metric", title=title)
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig
