from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def _compute_drawdown(prices: pd.Series) -> Optional[float]:
    if prices is None or prices.empty:
        return None
    running_max = prices.cummax()
    drawdown = (prices - running_max) / running_max
    return float(drawdown.min())


def compute_market_metrics(
    price_history: pd.DataFrame,
    benchmark_history: Optional[pd.DataFrame] = None,
) -> dict:
    if price_history is None or price_history.empty or "Close" not in price_history:
        return {
            "total_return": None,
            "volatility": None,
            "drawdown": None,
            "beta": None,
        }

    price_history = price_history.dropna(subset=["Close"]).copy()
    price_history = price_history.sort_values("Date")
    prices = price_history["Close"]
    returns = prices.pct_change().dropna()

    total_return = None
    if len(prices) > 1:
        total_return = float(prices.iloc[-1] / prices.iloc[0] - 1)

    volatility = float(returns.std() * np.sqrt(252)) if not returns.empty else None
    drawdown = _compute_drawdown(prices)

    beta = None
    if benchmark_history is not None and not benchmark_history.empty:
        benchmark = benchmark_history.dropna(subset=["Close"]).sort_values("Date")
        benchmark_returns = benchmark["Close"].pct_change().dropna()
        aligned = pd.concat([returns, benchmark_returns], axis=1, join="inner").dropna()
        if aligned.shape[0] > 10:
            cov = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])[0, 1]
            var = np.var(aligned.iloc[:, 1])
            if var != 0:
                beta = float(cov / var)

    return {
        "total_return": total_return,
        "volatility": volatility,
        "drawdown": drawdown,
        "beta": beta,
    }
