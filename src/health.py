from __future__ import annotations

from typing import Dict, Optional

import pandas as pd


def _latest_value(statement: Optional[pd.DataFrame], row: str) -> Optional[float]:
    if statement is None or statement.empty:
        return None
    if row not in statement.index:
        return None
    series = statement.loc[row].dropna()
    if series.empty:
        return None
    return float(series.iloc[0])


def _two_period_growth(statement: Optional[pd.DataFrame], row: str) -> Optional[float]:
    if statement is None or statement.empty:
        return None
    if row not in statement.index:
        return None
    series = statement.loc[row].dropna()
    if len(series) < 2:
        return None
    latest = series.iloc[0]
    prior = series.iloc[1]
    if prior == 0:
        return None
    return float((latest - prior) / abs(prior))


def compute_free_cash_flow(cashflow: Optional[pd.DataFrame]) -> Optional[float]:
    if cashflow is None or cashflow.empty:
        return None
    op_cash = _latest_value(cashflow, "Total Cash From Operating Activities")
    capex = _latest_value(cashflow, "Capital Expenditures")
    if op_cash is None or capex is None:
        return None
    return float(op_cash + capex)


def compute_health_metrics(financials: Dict[str, Optional[pd.DataFrame]]) -> Dict[str, Optional[float]]:
    income = financials.get("income")
    balance = financials.get("balance")
    cashflow = financials.get("cashflow")

    revenue = _latest_value(income, "Total Revenue")
    net_income = _latest_value(income, "Net Income")
    revenue_growth = _two_period_growth(income, "Total Revenue")
    net_income_growth = _two_period_growth(income, "Net Income")

    net_margin = None
    if revenue and net_income is not None:
        try:
            net_margin = net_income / revenue
        except Exception:
            net_margin = None

    total_debt = _latest_value(balance, "Total Debt") or _latest_value(balance, "Long Term Debt")
    total_equity = _latest_value(balance, "Total Stockholder Equity")
    debt_to_equity = None
    if total_debt is not None and total_equity:
        try:
            debt_to_equity = total_debt / total_equity
        except Exception:
            debt_to_equity = None

    ebit = _latest_value(income, "EBIT")
    interest_expense = _latest_value(income, "Interest Expense")
    interest_coverage = None
    if ebit is not None and interest_expense:
        try:
            interest_coverage = ebit / abs(interest_expense)
        except Exception:
            interest_coverage = None

    free_cash_flow = compute_free_cash_flow(cashflow)

    return {
        "revenue": revenue,
        "net_income": net_income,
        "revenue_growth": revenue_growth,
        "net_income_growth": net_income_growth,
        "net_margin": net_margin,
        "debt_to_equity": debt_to_equity,
        "interest_coverage": interest_coverage,
        "free_cash_flow": free_cash_flow,
    }
