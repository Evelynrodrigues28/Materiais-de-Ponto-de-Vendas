# Methodology

This document explains, step by step, how the project turns raw sell-out into a material plan
and then allocates a budget. All numbers are illustrative (synthetic data).

## Part 1 — Sizing the material need (Python pipeline)

### Step 1 — Moving window
Keep only the **most recent 6 periods** of sell-out. Older periods are dropped so the plan reflects
current performance.

### Step 2 — Top 10% stores per distributor
Within **each distributor**, rank its points of sale (POS) by total revenue and keep only the
**top 10%** (the stores that sell the most). This focuses material investment where it pays off.
Done per distributor, so a large and a small distributor each keep their own top 10%.

### Step 3 — Segment classification
Each store belongs to a **retail segment** (Hypermarket, Large/Small Supermarket, Traditional,
Wholesale, Cash & Carry, Pharmacy).

### Step 4 — Count stores per segment
For each distributor, count how many top-10% stores fall in each segment (`total_pos`).

### Step 5 — Material kit per segment
Each segment has a fixed **kit** of materials per store (e.g., a Hypermarket store gets
1 Flagship Display + 2 Regular Displays + 1 Slim Display + 1 Shelf Liner + 1 Light Kit).

### Step 6 — Consolidate
**Material quantity = kit per store × number of top-10% stores in the segment.**

Example (a distributor with 45 Hypermarket stores):

| Material | Per store | × stores | Quantity |
| --- | --- | --- | --- |
| FLAGSHIP_DISPLAY | 1 | 45 | 45 |
| REGULAR_DISPLAY | 2 | 45 | 90 |
| SLIM_DISPLAY | 1 | 45 | 45 |
| SHELF_LINER | 1 | 45 | 45 |
| LIGHT_KIT | 1 | 45 | 45 |

## Part 2 — Allocating the budget (Power BI)

### Step 7 — Total cost (the need)
`Total Cost = sum over materials of (quantity × unit price)`. This is the money each distributor
would need to fully cover its top-10% stores.

### Step 8 — Budget allocated
The budget is split **proportionally to each distributor's need**:

```
Budget Allocated = (distributor's Total Cost / total Total Cost of all distributors) × Budget
```

...and **capped at the distributor's own need** (`MIN(..., Total Cost)`), so no one gets more money
than they require. Worked example with a budget of R$ 1,000,000 and a total need of R$ 4,910,000:

* A distributor that needs R$ 500,000 represents ~10.2% of the total need → receives ~R$ 101,833.
* A distributor that needs R$ 100,000 (~2%) → receives ~R$ 20,367.

### Step 9 — Coverage
`Coverage = Budget Allocated / Total Cost` = the fraction of the need the money covers.
Because the split is proportional, **coverage is the same for everyone** and equals
`Budget / total need` (~20% in the example). Think of it as giving everyone the same "discount".

### Step 10 — Units funded per material
`Units Funded = planned quantity × Coverage` (rounded down). With ~20% coverage, the budget pays
for ~20% of every material's planned quantity.

## Design choices & trade-offs

* **Why proportional to need?** It is simple, transparent and defensible — easy for a trade-marketing
  analyst to explain. It allocates by *need/size*, not by *return*. A more ROI-oriented variant would
  weight by sell-out or by efficiency (sell-out per material cost).
* **"Client" = store (POS), not company.** Counting is done at the point-of-sale level, the atomic
  unit that actually receives materials.
* **Snapshot, not forecast.** The need is based on a 6-period window of historical sell-out and fixed
  per-segment kits; it is not a forward-looking demand model.
