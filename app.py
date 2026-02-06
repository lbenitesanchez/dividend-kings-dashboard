from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src import charts, data, dividends, universe
from src.health import compute_health_metrics
from src.metrics import compute_market_metrics
from src.utils import (
    as_of_timestamp,
    format_currency,
    format_large_number,
    format_number,
    format_percent,
)

st.set_page_config(page_title="Dividend Kings Dashboard", layout="wide")

st.title("Dividend Kings Dashboard")
last_refresh = st.empty()

universe_df = universe.load_universe("data/dividend_kings.csv")

st.sidebar.header("Universe")
universe_name = st.sidebar.selectbox(
    "Ticker universe", ["Dividend Kings"], help="Edit data/dividend_kings.csv to change the universe."
)

all_tickers = universe_df["ticker"].tolist()
default_tickers = all_tickers[: min(len(all_tickers), 8)]
selected_tickers = st.sidebar.multiselect(
    "Select tickers", all_tickers, default=default_tickers, help="Select up to 10 tickers for performance."
)

start_date = st.sidebar.date_input("Start date", value=date(2020, 1, 1))
end_date = st.sidebar.date_input("End date", value=date.today())
interval = st.sidebar.selectbox("Interval", ["1d", "1wk"], index=0)
compare_benchmark = st.sidebar.toggle("Compare to SPY", value=True)
if st.sidebar.button("Refresh data"):
    st.cache_data.clear()

last_refresh.markdown(f"Last refresh: **{as_of_timestamp()}**")

if not selected_tickers:
    st.warning("Select at least one ticker to begin.")
    st.stop()

benchmark_history = None
if compare_benchmark:
    benchmark_history = data.fetch_price_history("SPY", str(start_date), str(end_date), interval)

kpi_rows = []
metrics_rows = []
news_data: dict[str, list[dict]] = {}

for ticker in selected_tickers:
    info = data.fetch_info(ticker)
    price_history = data.fetch_price_history(ticker, str(start_date), str(end_date), interval)
    dividends_series = data.fetch_dividends(ticker)
    financials = data.fetch_financials(ticker)
    market = compute_market_metrics(price_history, benchmark_history)
    health_metrics = compute_health_metrics(financials)
    dividend_metrics = dividends.compute_dividend_metrics(info, dividends_series)

    price = None
    if price_history is not None and not price_history.empty:
        price = float(price_history.sort_values("Date")["Close"].iloc[-1])

    kpi_rows.append(
        {
            "Ticker": ticker,
            "Price": price,
            "Market Cap": info.get("marketCap"),
            "Dividend Yield": dividend_metrics.get("dividend_yield"),
            "TTM Dividend": dividend_metrics.get("ttm_dividend"),
            "Forward Dividend": dividend_metrics.get("forward_dividend"),
            "Payout Ratio": dividend_metrics.get("payout_ratio"),
            "Drawdown": market.get("drawdown"),
        }
    )

    metrics_rows.append(
        {
            "Ticker": ticker,
            "Price": price,
            "Market Cap": info.get("marketCap"),
            "Dividend Yield": dividend_metrics.get("dividend_yield"),
            "TTM Dividend": dividend_metrics.get("ttm_dividend"),
            "Forward Dividend": dividend_metrics.get("forward_dividend"),
            "Payout Ratio": dividend_metrics.get("payout_ratio"),
            "Total Return": market.get("total_return"),
            "Volatility": market.get("volatility"),
            "Drawdown": market.get("drawdown"),
            "Beta": market.get("beta"),
            "Revenue Growth": health_metrics.get("revenue_growth"),
            "Net Margin": health_metrics.get("net_margin"),
            "Debt/Equity": health_metrics.get("debt_to_equity"),
            "FCF": health_metrics.get("free_cash_flow"),
        }
    )

    news_data[ticker] = data.fetch_news(ticker)

metrics_df = pd.DataFrame(metrics_rows)

overview_tab, dividends_tab, health_tab, portfolio_tab, news_tab = st.tabs(
    ["Overview", "Dividends", "Financials & Health", "Portfolio Calculator", "News"]
)

with overview_tab:
    st.subheader("Key Metrics")
    cols = st.columns(3)
    for idx, row in enumerate(kpi_rows):
        col = cols[idx % 3]
        with col:
            st.markdown(f"### {row['Ticker']}")
            st.metric("Price", format_currency(row["Price"], 2))
            st.metric("Market Cap", format_large_number(row["Market Cap"]))
            st.metric("Dividend Yield", format_percent(row["Dividend Yield"], 2))
            st.metric("TTM Dividend", format_currency(row["TTM Dividend"], 2))
            st.metric("Forward Dividend", format_currency(row["Forward Dividend"], 2))
            st.metric("Payout Ratio", format_percent(row["Payout Ratio"], 2))
            st.metric("Drawdown", format_percent(row["Drawdown"], 2))

    st.subheader("Comparison Table")
    st.dataframe(metrics_df, use_container_width=True)
    st.download_button(
        "Download metrics as CSV",
        metrics_df.to_csv(index=False),
        file_name="dividend_kings_metrics.csv",
        mime="text/csv",
    )

with dividends_tab:
    st.subheader("Dividend History")
    for ticker in selected_tickers:
        dividends_series = data.fetch_dividends(ticker)
        info = data.fetch_info(ticker)
        calendar = data.fetch_calendar(ticker)

        st.markdown(f"### {ticker}")
        st.plotly_chart(charts.dividend_history_chart(dividends_series, f"{ticker} Dividend History"), use_container_width=True)

        ex_date = dividends.next_ex_dividend_date(calendar, info)
        last_event = dividends.last_dividend_event(dividends_series)
        col1, col2 = st.columns(2)
        with col1:
            st.write("Next Ex-Dividend Date:", ex_date.date() if ex_date else "—")
        with col2:
            st.write("Last Dividend Event:", last_event.date() if last_event else "—")

        annual = dividends.compute_annual_dividends(dividends_series)
        st.plotly_chart(charts.annual_dividends_chart(annual, f"{ticker} Annual Dividends"), use_container_width=True)
        cagr_3y = dividends.compute_dividend_cagr(annual, 3)
        cagr_5y = dividends.compute_dividend_cagr(annual, 5)
        st.write("3Y CAGR:", format_percent(cagr_3y, 2))
        st.write("5Y CAGR:", format_percent(cagr_5y, 2))

        financials = data.fetch_financials(ticker)
        net_income = None
        dividends_paid = None
        free_cash_flow = None
        if financials.get("income") is not None and not financials["income"].empty:
            if "Net Income" in financials["income"].index:
                net_income = float(financials["income"].loc["Net Income"].iloc[0])
        if financials.get("cashflow") is not None and not financials["cashflow"].empty:
            if "Dividends Paid" in financials["cashflow"].index:
                dividends_paid = float(financials["cashflow"].loc["Dividends Paid"].iloc[0])
            if "Total Cash From Operating Activities" in financials["cashflow"].index and "Capital Expenditures" in financials["cashflow"].index:
                op_cash = float(financials["cashflow"].loc["Total Cash From Operating Activities"].iloc[0])
                capex = float(financials["cashflow"].loc["Capital Expenditures"].iloc[0])
                free_cash_flow = op_cash + capex

        safety = dividends.compute_dividend_safety(net_income, dividends_paid, free_cash_flow)
        st.write("Earnings payout ratio:", format_percent(safety.get("earnings_payout_ratio"), 2))
        st.write("FCF payout ratio:", format_percent(safety.get("fcf_payout_ratio"), 2))

with health_tab:
    st.subheader("Financials & Health")
    for ticker in selected_tickers:
        st.markdown(f"### {ticker}")
        financials = data.fetch_financials(ticker)
        health_metrics = compute_health_metrics(financials)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Revenue", format_large_number(health_metrics.get("revenue")))
        col2.metric("Net Income", format_large_number(health_metrics.get("net_income")))
        col3.metric("Revenue Growth", format_percent(health_metrics.get("revenue_growth"), 2))
        col4.metric("Net Margin", format_percent(health_metrics.get("net_margin"), 2))

        col5, col6, col7 = st.columns(3)
        col5.metric("Debt/Equity", format_number(health_metrics.get("debt_to_equity"), 2))
        col6.metric("Interest Coverage", format_number(health_metrics.get("interest_coverage"), 2))
        col7.metric("Free Cash Flow", format_large_number(health_metrics.get("free_cash_flow")))

        st.plotly_chart(
            charts.financials_chart(financials.get("income"), "Total Revenue", f"{ticker} Revenue"),
            use_container_width=True,
        )
        st.plotly_chart(
            charts.financials_chart(financials.get("income"), "Net Income", f"{ticker} Net Income"),
            use_container_width=True,
        )
        st.plotly_chart(
            charts.financials_chart(financials.get("cashflow"), "Total Cash From Operating Activities", f"{ticker} Operating Cash Flow"),
            use_container_width=True,
        )
        st.plotly_chart(
            charts.financials_chart(financials.get("cashflow"), "Capital Expenditures", f"{ticker} Capex"),
            use_container_width=True,
        )
        cashflow = financials.get("cashflow")
        if cashflow is not None and not cashflow.empty:
            if "Total Cash From Operating Activities" in cashflow.index and "Capital Expenditures" in cashflow.index:
                fcf_series = cashflow.loc["Total Cash From Operating Activities"].add(
                    cashflow.loc["Capital Expenditures"], fill_value=0
                )
                fcf_df = pd.DataFrame({"Date": fcf_series.index, "Value": fcf_series.values})
                fcf_chart = charts.multi_series_chart(
                    fcf_df.assign(Metric="Free Cash Flow"), f"{ticker} Free Cash Flow"
                )
                st.plotly_chart(fcf_chart, use_container_width=True)
            else:
                st.warning("Free cash flow data not available.")
        else:
            st.warning("Free cash flow data not available.")

        if health_metrics.get("debt_to_equity") is None:
            st.warning("Debt/Equity not available for this ticker.")
        if health_metrics.get("interest_coverage") is None:
            st.warning("Interest coverage could not be computed.")

with portfolio_tab:
    st.subheader("Portfolio Calculator")
    holdings_df = pd.DataFrame(
        {
            "ticker": selected_tickers,
            "shares": [10] * len(selected_tickers),
            "cost_basis": [None] * len(selected_tickers),
        }
    )
    holdings = st.data_editor(holdings_df, num_rows="dynamic", use_container_width=True)

    income_rows = []
    for _, row in holdings.iterrows():
        ticker = row.get("ticker")
        if not isinstance(ticker, str) or ticker == "":
            continue
        shares = row.get("shares") or 0
        info = data.fetch_info(ticker)
        dividends_series = data.fetch_dividends(ticker)
        forward = dividends.compute_forward_dividend(info)
        ttm = dividends.compute_ttm_dividend(dividends_series)
        annual_dividend = forward or ttm or 0
        income_rows.append(
            {
                "Ticker": ticker,
                "Shares": shares,
                "Annual Dividend": annual_dividend,
                "Estimated Income": shares * annual_dividend,
            }
        )

    income_df = pd.DataFrame(income_rows)
    st.dataframe(income_df, use_container_width=True)
    total_income = income_df["Estimated Income"].sum() if not income_df.empty else 0
    st.metric("Total Annual Dividend Income", format_currency(total_income, 2))

    upcoming_rows = []
    for _, row in holdings.iterrows():
        ticker = row.get("ticker")
        if not isinstance(ticker, str) or ticker == "":
            continue
        info = data.fetch_info(ticker)
        calendar = data.fetch_calendar(ticker)
        ex_date = dividends.next_ex_dividend_date(calendar, info)
        upcoming_rows.append(
            {
                "Ticker": ticker,
                "Next Ex-Dividend Date": ex_date.date() if ex_date else "—",
            }
        )
    upcoming_df = pd.DataFrame(upcoming_rows)
    st.dataframe(upcoming_df, use_container_width=True)

    combined = income_df.merge(upcoming_df, on="Ticker", how="left")
    st.download_button(
        "Download holdings as CSV",
        combined.to_csv(index=False),
        file_name="portfolio_dividends.csv",
        mime="text/csv",
    )

with news_tab:
    st.subheader("Latest News")
    for ticker in selected_tickers:
        st.markdown(f"### {ticker}")
        items = news_data.get(ticker) or []
        if not items:
            st.info("No news available from yfinance.")
            continue
        for item in items[:5]:
            title = item.get("title")
            link = item.get("link")
            publisher = item.get("publisher")
            if title and link:
                st.markdown(f"- [{title}]({link}) ({publisher})")
