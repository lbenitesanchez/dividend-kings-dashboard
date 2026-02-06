from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, Optional

import pandas as pd
import streamlit as st


@st.cache_data(ttl=3600)
def cached_call(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    return func(*args, **kwargs)


def safe_get(mapping: Optional[Dict[str, Any]], key: str, default: Any = None) -> Any:
    if not isinstance(mapping, dict):
        return default
    return mapping.get(key, default)


def format_currency(value: Any, decimals: int = 2) -> str:
    try:
        if value is None or pd.isna(value):
            return "—"
        return f"${value:,.{decimals}f}"
    except Exception:
        return "—"


def format_percent(value: Any, decimals: int = 2) -> str:
    try:
        if value is None or pd.isna(value):
            return "—"
        return f"{value * 100:,.{decimals}f}%"
    except Exception:
        return "—"


def format_number(value: Any, decimals: int = 2) -> str:
    try:
        if value is None or pd.isna(value):
            return "—"
        return f"{value:,.{decimals}f}"
    except Exception:
        return "—"


def format_large_number(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "—"
        value = float(value)
        for unit, divisor in [("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)]:
            if abs(value) >= divisor:
                return f"${value / divisor:,.2f}{unit}"
        return f"${value:,.2f}"
    except Exception:
        return "—"


def as_of_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


@st.cache_data(ttl=3600)
def empty_frame(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)
