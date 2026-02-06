from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=3600)
def get_ticker(ticker: str) -> yf.Ticker:
    return yf.Ticker(ticker)


@st.cache_data(ttl=3600)
def fetch_info(ticker: str) -> Dict[str, Any]:
    try:
        return get_ticker(ticker).info or {}
    except Exception:
        return {}


@st.cache_data(ttl=3600)
def fetch_calendar(ticker: str) -> pd.DataFrame:
    try:
        calendar = get_ticker(ticker).calendar
        if isinstance(calendar, pd.DataFrame):
            return calendar
        if isinstance(calendar, dict):
            return pd.DataFrame(calendar)
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_price_history(
    ticker: str,
    start: str,
    end: str,
    interval: str = "1d",
) -> pd.DataFrame:
    try:
        history = get_ticker(ticker).history(start=start, end=end, interval=interval)
        if history is None:
            return pd.DataFrame()
        return history.reset_index()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_dividends(ticker: str) -> pd.Series:
    try:
        dividends = get_ticker(ticker).dividends
        if dividends is None:
            return pd.Series(dtype=float)
        return dividends
    except Exception:
        return pd.Series(dtype=float)


@st.cache_data(ttl=3600)
def fetch_financials(ticker: str) -> Dict[str, Optional[pd.DataFrame]]:
    try:
        yf_ticker = get_ticker(ticker)
        return {
            "income": yf_ticker.financials,
            "balance": yf_ticker.balance_sheet,
            "cashflow": yf_ticker.cashflow,
            "quarterly_income": yf_ticker.quarterly_financials,
            "quarterly_balance": yf_ticker.quarterly_balance_sheet,
            "quarterly_cashflow": yf_ticker.quarterly_cashflow,
        }
    except Exception:
        return {
            "income": None,
            "balance": None,
            "cashflow": None,
            "quarterly_income": None,
            "quarterly_balance": None,
            "quarterly_cashflow": None,
        }


@st.cache_data(ttl=3600)
def fetch_news(ticker: str) -> list[Dict[str, Any]]:
    try:
        return get_ticker(ticker).news or []
    except Exception:
        return []
