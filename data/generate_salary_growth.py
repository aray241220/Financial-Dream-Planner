"""One-time generator for the salary-growth training set.

The provided salary_data.csv has no future-salary column, so this script derives
a SYNTHETIC, illustrative "Future Salary" over a fixed 5-year horizon. The growth
rate (CAGR) varies by city tier and age with small seeded random noise, so the
target is a genuine (if synthetic) regression target rather than a constant
multiple of current salary. Metrics reported by train.py are honest for THIS
dataset; the dataset itself is illustrative, not real.

Run:    python data/generate_salary_growth.py
Output: data/salary_growth.csv  (Age, City, Current Salary, Future Salary)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HORIZON_YEARS = 5
SEED = 42
DATA_DIR = Path(__file__).resolve().parent
SOURCE = DATA_DIR / "salary_data.csv"
OUTPUT = DATA_DIR / "salary_growth.csv"

# Illustrative base 5-year CAGR by city tier (tech hubs grow a bit faster).
CITY_BASE_CAGR = {
    "Bangalore": 0.115, "Hyderabad": 0.110, "Pune": 0.108,
    "Mumbai": 0.100, "Delhi": 0.100, "Chennai": 0.098,
    "Ahmedabad": 0.088, "Jaipur": 0.085, "Kolkata": 0.084, "Lucknow": 0.082,
}
DEFAULT_CAGR = 0.09


def build() -> pd.DataFrame:
    df = pd.read_csv(SOURCE)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df.columns = df.columns.str.strip()

    rng = np.random.default_rng(SEED)
    current = df["Monthly_Salary"].astype(float)
    base = df["City"].map(CITY_BASE_CAGR).fillna(DEFAULT_CAGR)
    age_adj = (30 - df["Age"].astype(float)) * 0.002  # younger grows slightly faster
    noise = rng.normal(0.0, 0.012, size=len(df))
    cagr = (base + age_adj + noise).clip(0.04, 0.16)

    future = current * (1 + cagr) ** HORIZON_YEARS
    future = (future / 500).round() * 500  # round to a tidy figure

    return pd.DataFrame({
        "Age": df["Age"].astype(int),
        "City": df["City"],
        "Current Salary": current.astype(int),
        "Future Salary": future.astype(int),
    })


if __name__ == "__main__":
    out = build()
    out.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(out)} rows -> {OUTPUT}")
    print(out.head().to_string(index=False))
