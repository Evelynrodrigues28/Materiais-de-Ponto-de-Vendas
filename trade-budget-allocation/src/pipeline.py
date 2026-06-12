"""Trade-marketing point-of-sale (POS) material plan.

Reads synthetic sell-out and POS data, selects the top 10% revenue stores per
distributor over a moving window, applies a per-segment material kit, and writes a
consolidated material plan consumed by the Power BI budget-allocation report.

Run ``python data/generate_sample_data.py`` first to create the input CSVs.

Usage:
    python src/pipeline.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "output"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WINDOW_PERIODS = 6   # moving window: keep the most recent 6 periods
TOP_PCT = 0.90       # keep stores at/above the 90th revenue percentile (top 10%)

MATERIAL_COLS = [
    "FLAGSHIP_DISPLAY", "REGULAR_DISPLAY", "SLIM_DISPLAY",
    "PALLET_COVER", "SHELF_LINER", "COUNTER_DISPLAY", "LIGHT_KIT",
]

# Material kit PER STORE by segment (how many units each store of that segment receives)
SEGMENT_KIT = pd.DataFrame([
    {"segment": "WHOLESALE",         "FLAGSHIP_DISPLAY": 0, "REGULAR_DISPLAY": 2, "SLIM_DISPLAY": 1, "PALLET_COVER": 0, "SHELF_LINER": 0, "COUNTER_DISPLAY": 0, "LIGHT_KIT": 1},
    {"segment": "CASH_AND_CARRY",    "FLAGSHIP_DISPLAY": 0, "REGULAR_DISPLAY": 1, "SLIM_DISPLAY": 0, "PALLET_COVER": 1, "SHELF_LINER": 1, "COUNTER_DISPLAY": 0, "LIGHT_KIT": 1},
    {"segment": "PHARMACY",          "FLAGSHIP_DISPLAY": 0, "REGULAR_DISPLAY": 0, "SLIM_DISPLAY": 0, "PALLET_COVER": 0, "SHELF_LINER": 0, "COUNTER_DISPLAY": 0, "LIGHT_KIT": 1},
    {"segment": "HYPERMARKET",       "FLAGSHIP_DISPLAY": 1, "REGULAR_DISPLAY": 2, "SLIM_DISPLAY": 1, "PALLET_COVER": 0, "SHELF_LINER": 1, "COUNTER_DISPLAY": 0, "LIGHT_KIT": 1},
    {"segment": "LARGE_SUPERMARKET", "FLAGSHIP_DISPLAY": 0, "REGULAR_DISPLAY": 2, "SLIM_DISPLAY": 0, "PALLET_COVER": 0, "SHELF_LINER": 0, "COUNTER_DISPLAY": 0, "LIGHT_KIT": 1},
    {"segment": "SMALL_SUPERMARKET", "FLAGSHIP_DISPLAY": 0, "REGULAR_DISPLAY": 0, "SLIM_DISPLAY": 2, "PALLET_COVER": 0, "SHELF_LINER": 0, "COUNTER_DISPLAY": 0, "LIGHT_KIT": 1},
    {"segment": "TRADITIONAL",       "FLAGSHIP_DISPLAY": 0, "REGULAR_DISPLAY": 0, "SLIM_DISPLAY": 0, "PALLET_COVER": 0, "SHELF_LINER": 0, "COUNTER_DISPLAY": 1, "LIGHT_KIT": 1},
])

# Unit price per material (illustrative, fictional values)
UNIT_PRICE = {
    "FLAGSHIP_DISPLAY": 750.00, "REGULAR_DISPLAY": 105.00, "SLIM_DISPLAY": 45.00,
    "PALLET_COVER": 160.00, "SHELF_LINER": 100.00, "COUNTER_DISPLAY": 0.00, "LIGHT_KIT": 40.00,
}


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    sellout = pd.read_csv(RAW_DIR / "sellout.csv", parse_dates=["date"])
    pos_dim = pd.read_csv(RAW_DIR / "pos_dimension.csv")
    return sellout, pos_dim


def apply_moving_window(sellout: pd.DataFrame) -> pd.DataFrame:
    """Keep only the most recent WINDOW_PERIODS monthly periods."""
    sellout = sellout.copy()
    sellout["period"] = sellout["date"].dt.to_period("M").astype(str)
    recent = sorted(sellout["period"].unique())[-WINDOW_PERIODS:]
    return sellout[sellout["period"].isin(recent)]


def select_top_stores(sellout: pd.DataFrame) -> pd.DataFrame:
    """Within each distributor, keep the top 10% stores by total revenue."""
    revenue = (
        sellout.groupby(["distributor_id", "pos_code"], as_index=False)
        .agg(revenue=("amount", "sum"))
    )
    revenue["pct_rank"] = (
        revenue.groupby("distributor_id")["revenue"].rank(pct=True, method="first")
    )
    return revenue.loc[revenue["pct_rank"] >= TOP_PCT, ["distributor_id", "pos_code"]]


def build_material_plan(
    sellout: pd.DataFrame, pos_dim: pd.DataFrame, top_stores: pd.DataFrame
) -> pd.DataFrame:
    """Consolidate material need per distributor x segment."""
    enriched = (
        sellout.merge(top_stores, on=["distributor_id", "pos_code"], how="inner")
        .merge(pos_dim[["pos_code", "segment"]], on="pos_code", how="left")
    )

    by_segment = (
        enriched.groupby(["distributor_id", "segment"], as_index=False)
        .agg(
            total_pos=("pos_code", "nunique"),
            sellout_amount=("amount", "sum"),
            sellout_units=("units", "sum"),
        )
    )

    # material quantity = kit per store x number of top-10% stores in the segment
    plan = by_segment.merge(SEGMENT_KIT, on="segment", how="inner")
    for col in MATERIAL_COLS:
        plan[col] = plan[col] * plan["total_pos"]

    # physical rank of distributors by total sell-out (sort key for Power BI)
    dist_rank = (
        plan.groupby("distributor_id")["sellout_amount"].sum()
        .rank(ascending=False, method="first").astype(int)
    )
    plan["distributor_rank"] = plan["distributor_id"].map(dist_rank)

    return plan.sort_values(["distributor_rank", "segment"]).reset_index(drop=True)


def material_cost(plan: pd.DataFrame) -> float:
    """Total monetary need of the whole plan (sum of qty x unit price)."""
    return float(sum((plan[c] * UNIT_PRICE[c]).sum() for c in MATERIAL_COLS))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sellout, pos_dim = load_data()
    sellout = apply_moving_window(sellout)
    top_stores = select_top_stores(sellout)
    plan = build_material_plan(sellout, pos_dim, top_stores)

    out_path = OUT_DIR / "pos_materials_plan.csv"
    plan.to_csv(out_path, index=False)

    total_units = int(plan[MATERIAL_COLS].to_numpy().sum())
    print(f"Distributors        : {plan['distributor_id'].nunique()}")
    print(f"Top-10% stores      : {int(plan['total_pos'].sum()):,}")
    print(f"Total material units: {total_units:,}")
    print(f"Total material need : R$ {material_cost(plan):,.2f}")
    print(f"Output -> {out_path}")


if __name__ == "__main__":
    main()
