"""Buy-and-hold benchmark (Phase 1 Task 4).

Every strategy report shows this alongside: a strategy only earns its
complexity if it beats holding on a risk-adjusted basis. HODL is modeled
gross of fees - a single 0.4% round trip is negligible over these horizons.
"""

import pandas as pd


def buy_and_hold(df: pd.DataFrame) -> dict:
    """Total return, CAGR and max drawdown of holding from the first open
    to the last close of the given window."""
    entry = float(df["Open"].iloc[0])
    closes = df["Close"].astype(float)
    final = float(closes.iloc[-1])

    total_return = final / entry - 1
    days = max((df.index[-1] - df.index[0]).days, 1)
    cagr = (final / entry) ** (365.25 / days) - 1

    # Max drawdown on the close-price path, seeded with the entry price.
    path = pd.concat([pd.Series([entry]), closes], ignore_index=True)
    drawdown = path / path.cummax() - 1
    max_dd = float(drawdown.min())

    return {
        "total_return": total_return,
        "cagr": cagr,
        "max_dd": max_dd,
        "start": df.index[0],
        "end": df.index[-1],
    }
