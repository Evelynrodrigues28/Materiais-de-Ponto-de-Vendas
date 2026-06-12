# Trade Marketing POS Material & Budget Allocation

End-to-end analytics project that decides **how to allocate point-of-sale (POS) marketing materials and a limited trade-marketing budget across a network of retail distributors** — from raw sell-out data to an interactive Power BI report.

> **Note:** This is a portfolio project. The company ("ACME Snacks Co."), distributors, stores, prices and all data are **100% synthetic**. No real or proprietary data is included.

---

## Business problem

A CPG company (ACME Snacks Co.) sells through dozens of independent distributors, each serving hundreds of points of sale (POS). The trade-marketing team must decide:

1. **Which stores** should receive POS materials (displays, shelf liners, pallet covers, etc.)?
2. **How many** units of each material does each distributor need?
3. Given a **fixed budget** that is smaller than the total need, **how should the money be split** across distributors — fairly and automatically?

## Approach

The pipeline focuses investment on the highest-performing stores and sizes the material need per distributor:

1. **Moving window** – keep only the most recent 6 periods of sell-out.
2. **Top 10% stores** – within each distributor, keep only the POS in the top 10% by revenue (where material investment pays off most).
3. **Segment classification** – each store belongs to a retail segment (Hypermarket, Wholesale, Pharmacy, ...).
4. **Material kit per segment** – each segment has a fixed "kit" of materials per store.
5. **Consolidation** – material quantity = kit per store × number of top-10% stores in that segment.
6. **Budget allocation (Power BI)** – the budget is split across distributors **proportionally to their material need**, capped at each distributor's need, and translated back into how many units of each material it can fund.

## Repository structure

```
trade-budget-allocation/
├── README.md
├── requirements.txt
├── data/
│   └── generate_sample_data.py   # creates synthetic sellout.csv + pos_dimension.csv
├── src/
│   └── pipeline.py               # builds the consolidated material plan (pandas)
├── powerbi/
│   └── dax_measures.md           # budget-allocation measures for the report
└── docs/
    └── methodology.md            # step-by-step methodology
```

## How to run

```bash
pip install -r requirements.txt

# 1) generate synthetic input data
python data/generate_sample_data.py

# 2) build the consolidated material plan
python src/pipeline.py
```

The pipeline writes `data/output/pos_materials_plan.csv`, which is the dataset consumed by the Power BI report (see `powerbi/dax_measures.md`).

## Power BI layer

The report lets a trade-marketing analyst type a budget and instantly see, per distributor:

* **Budget Allocated** – the distributor's share of the budget (proportional to need, capped at need).
* **Coverage** – the fraction of the need the budget covers.
* **Units funded per material** – how many units of each material the budget pays for.

All DAX is documented in [`powerbi/dax_measures.md`](powerbi/dax_measures.md).

## Tech stack

* **Python** (pandas, numpy) – data generation and the allocation pipeline
* **Power BI** (DAX, What-If parameters) – interactive budget allocation
* Original production version ran on **Databricks / PySpark** over a data warehouse; this portfolio version is refactored to pure pandas + synthetic data so it runs anywhere.

## Key concepts demonstrated

* Window-based filtering and percentile ranking per group
* Rule-based "kit" expansion (need sizing)
* Proportional budget allocation with a cap (and why it's mathematically a uniform coverage %)
* Translating a monetary allocation back into purchasable units
* Designing measures that react to an interactive parameter in BI
