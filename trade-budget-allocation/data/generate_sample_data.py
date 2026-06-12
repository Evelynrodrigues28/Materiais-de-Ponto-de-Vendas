"""Generate synthetic trade-marketing sample data for the POS material allocation project.

Outputs two CSVs under ``data/raw/``:
    - ``pos_dimension.csv`` : point-of-sale master (pos_code, distributor_id, segment)
    - ``sellout.csv``       : transactional sell-out (distributor_id, date, pos_code, units, amount)

All data is fully synthetic (ACME Snacks Co.) and generated with a fixed seed for reproducibility.

Usage:
    python data/generate_sample_data.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

RAW_DIR = Path(__file__).resolve().parent / "raw"

N_DISTRIBUTORS = 15
N_PERIODS = 8  # monthly periods generated; the pipeline keeps the most recent 6

# Retail segments and the probability that a store belongs to each one
SEGMENT_WEIGHTS = {
    "HYPERMARKET": 0.08,
    "LARGE_SUPERMARKET": 0.15,
    "SMALL_SUPERMARKET": 0.25,
    "TRADITIONAL": 0.30,
    "WHOLESALE": 0.07,
    "CASH_AND_CARRY": 0.05,
    "PHARMACY": 0.10,
}

# Average monthly revenue scale per segment (bigger formats sell more)
SEGMENT_REVENUE_SCALE = {
    "HYPERMARKET": 40_000,
    "LARGE_SUPERMARKET": 22_000,
    "SMALL_SUPERMARKET": 9_000,
    "TRADITIONAL": 4_000,
    "WHOLESALE": 60_000,
    "CASH_AND_CARRY": 35_000,
    "PHARMACY": 6_000,
}


def make_pos_dimension() -> pd.DataFrame:
    """One row per point of sale, assigned to a distributor and a retail segment."""
    seg_names = list(SEGMENT_WEIGHTS)
    seg_probs = np.array(list(SEGMENT_WEIGHTS.values()), dtype=float)
    seg_probs /= seg_probs.sum()

    rows = []
    pos_counter = 1
    for d in range(1, N_DISTRIBUTORS + 1):
        distributor_id = f"D{d:03d}"
        n_pos = int(rng.integers(40, 400))  # distributors have different sizes
        for _ in range(n_pos):
            rows.append(
                {
                    "pos_code": f"P{pos_counter:06d}",
                    "distributor_id": distributor_id,
                    "segment": rng.choice(seg_names, p=seg_probs),
                }
            )
            pos_counter += 1
    return pd.DataFrame(rows)


def make_sellout(pos_dim: pd.DataFrame) -> pd.DataFrame:
    """Monthly sell-out transactions for each store across the generated periods."""
    periods = pd.period_range(end=pd.Timestamp.today().to_period("M"), periods=N_PERIODS, freq="M")

    rows = []
    for r in pos_dim.itertuples(index=False):
        base = SEGMENT_REVENUE_SCALE[r.segment] * rng.uniform(0.4, 1.6)
        for per in periods:
            if rng.random() < 0.85:  # not every store sells in every period
                amount = max(0.0, rng.normal(base, base * 0.3))
                units = max(0.0, amount / rng.uniform(8, 25))
                day = int(rng.integers(1, 28))
                rows.append(
                    {
                        "distributor_id": r.distributor_id,
                        "date": per.to_timestamp() + pd.Timedelta(days=day - 1),
                        "pos_code": r.pos_code,
                        "units": round(units, 2),
                        "amount": round(amount, 2),
                    }
                )
    return pd.DataFrame(rows)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    pos_dim = make_pos_dimension()
    sellout = make_sellout(pos_dim)

    pos_dim.to_csv(RAW_DIR / "pos_dimension.csv", index=False)
    sellout.to_csv(RAW_DIR / "sellout.csv", index=False)

    print(f"pos_dimension.csv : {len(pos_dim):,} points of sale")
    print(f"sellout.csv       : {len(sellout):,} transactions")
    print(f"Output -> {RAW_DIR}")


if __name__ == "__main__":
    main()
