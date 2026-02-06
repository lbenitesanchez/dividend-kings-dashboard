from __future__ import annotations

import pandas as pd


def load_universe(path: str) -> pd.DataFrame:
    return pd.read_csv(path).dropna(subset=["ticker"]).reset_index(drop=True)
