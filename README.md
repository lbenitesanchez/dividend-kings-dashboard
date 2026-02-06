# Dividend Kings Dashboard

A modern Streamlit dashboard for monitoring “Dividend Kings” style companies using **yfinance** data only. The app focuses on business health, dividend health, and portfolio income planning.

## Features
- Editable ticker universe (`data/dividend_kings.csv`) with a default seed list.
- KPI cards and sortable comparison table across selected tickers.
- Dividend history, growth, and safety analytics.
- Financials & health indicators with charts.
- Portfolio calculator with expected income and ex-dividend dates.
- Optional news tab (when yfinance provides headlines).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Data Notes & Limitations
- All data comes from **yfinance** and is subject to availability, latency, and occasional missing fields.
- Metrics are computed defensively; when a field is unavailable, the dashboard shows warnings instead of failing.
- Dividend and financial metrics may differ from official filings due to data lags.

## Customizing the Universe
Edit `data/dividend_kings.csv` to change the ticker universe. The sidebar automatically loads available tickers.

## Project Structure
```
app.py
src/
  universe.py
  data.py
  dividends.py
  health.py
  metrics.py
  charts.py
  utils.py
.streamlit/config.toml
data/dividend_kings.csv
```
