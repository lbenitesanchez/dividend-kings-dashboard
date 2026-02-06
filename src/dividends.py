from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd


def compute_ttm_dividend(dividends: pd.Series) -> Optional[float]:
    if dividends is None or dividends.empty:
        return None
    last_year = dividends[dividends.index >= (dividends.index.max() - pd.DateOffset(years=1))]
    if last_year.empty:
        return None
    return float(last_year.sum())


def compute_forward_dividend(info: Dict[str, Any]) -> Optional[float]:
    value = info.get("dividendRate") if isinstance(info, dict) else None
    return float(value) if value not in (None, 0) else None


def compute_dividend_yield(info: Dict[str, Any]) -> Optional[float]:
    value = info.get("dividendYield") if isinstance(info, dict) else None
    return float(value) if value not in (None, 0) else None


def compute_payout_ratio(info: Dict[str, Any]) -> Optional[float]:
    value = info.get("payoutRatio") if isinstance(info, dict) else None
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def compute_annual_dividends(dividends: pd.Series) -> pd.DataFrame:
    if dividends is None or dividends.empty:
        return pd.DataFrame(columns=["year", "dividends"])
    annual = dividends.resample("Y").sum()
    return pd.DataFrame({"year": annual.index.year, "dividends": annual.values})


def compute_dividend_cagr(annual: pd.DataFrame, years: int) -> Optional[float]:
    if annual is None or annual.empty or len(annual) < years + 1:
        return None
    annual_sorted = annual.sort_values("year")
    end_value = annual_sorted["dividends"].iloc[-1]
    start_value = annual_sorted["dividends"].iloc[-(years + 1)]
    if start_value <= 0:
        return None
    return float((end_value / start_value) ** (1 / years) - 1)


def compute_dividend_metrics(
    info: Dict[str, Any],
    dividends: pd.Series,
) -> Dict[str, Optional[float]]:
    ttm = compute_ttm_dividend(dividends)
    forward = compute_forward_dividend(info)
    return {
        "ttm_dividend": ttm,
        "forward_dividend": forward,
        "dividend_yield": compute_dividend_yield(info),
        "payout_ratio": compute_payout_ratio(info),
    }


def compute_dividend_safety(
    net_income: Optional[float],
    dividends_paid: Optional[float],
    free_cash_flow: Optional[float],
) -> Dict[str, Optional[float]]:
    earnings_payout = None
    fcf_payout = None
    if net_income and dividends_paid:
        try:
            earnings_payout = abs(dividends_paid) / net_income
        except Exception:
            earnings_payout = None
    if free_cash_flow and dividends_paid:
        try:
            fcf_payout = abs(dividends_paid) / free_cash_flow
        except Exception:
            fcf_payout = None
    return {
        "earnings_payout_ratio": earnings_payout,
        "fcf_payout_ratio": fcf_payout,
    }


def last_dividend_event(dividends: pd.Series) -> Optional[pd.Timestamp]:
    if dividends is None or dividends.empty:
        return None
    return dividends.index.max()


def next_ex_dividend_date(calendar: pd.DataFrame, info: Dict[str, Any]) -> Optional[pd.Timestamp]:
    if isinstance(calendar, pd.DataFrame) and not calendar.empty:
        for key in ["Ex-Dividend Date", "Ex-Dividend"]:
            if key in calendar.index:
                value = calendar.loc[key].dropna()
                if not value.empty:
                    return pd.to_datetime(value.iloc[0])
    if isinstance(info, dict):
        ex_date = info.get("exDividendDate")
        if ex_date:
            try:
                return pd.to_datetime(ex_date, unit="s")
            except Exception:
                return pd.to_datetime(ex_date, errors="coerce")
    return None


def annual_dividend_growth(annual: pd.DataFrame) -> pd.DataFrame:
    if annual is None or annual.empty:
        return pd.DataFrame(columns=["year", "dividends", "growth"])
    annual = annual.sort_values("year")
    annual["growth"] = annual["dividends"].pct_change()
    return annual
