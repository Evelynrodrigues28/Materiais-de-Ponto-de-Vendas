# Power BI — Budget Allocation Measures (DAX)

The report consumes `pos_materials_plan.csv` (output of `src/pipeline.py`) as the table
**`MaterialPlan`** and a small price table **`MaterialPrices`**. A What-If parameter table
**`Budget`** lets the analyst type the available budget.

## Tables and key columns

* **`MaterialPlan`**: `distributor_id`, `segment`, `total_pos`, `sellout_amount`,
  and the 7 material quantity columns (`FLAGSHIP_DISPLAY`, `REGULAR_DISPLAY`, `SLIM_DISPLAY`,
  `PALLET_COVER`, `SHELF_LINER`, `COUNTER_DISPLAY`, `LIGHT_KIT`).
* **`MaterialPrices`**: `material_type`, `unit_price`.
* **`Budget`**: What-If parameter (numeric range). See note on granularity at the end.

---

## 1. Budget parameter value

```dax
Budget Value = COALESCE(SELECTEDVALUE('Budget'[Budget]), 0)
```

## 2. Total material cost (the "need")

Sum of `quantity * unit_price` across the 7 materials. This is the monetary need of
whatever is in the current filter context (one distributor, one segment, or the grand total).

```dax
Total Cost =
    SUM('MaterialPlan'[FLAGSHIP_DISPLAY]) * LOOKUPVALUE('MaterialPrices'[unit_price], 'MaterialPrices'[material_type], "FLAGSHIP_DISPLAY") +
    SUM('MaterialPlan'[REGULAR_DISPLAY])  * LOOKUPVALUE('MaterialPrices'[unit_price], 'MaterialPrices'[material_type], "REGULAR_DISPLAY")  +
    SUM('MaterialPlan'[SLIM_DISPLAY])     * LOOKUPVALUE('MaterialPrices'[unit_price], 'MaterialPrices'[material_type], "SLIM_DISPLAY")     +
    SUM('MaterialPlan'[PALLET_COVER])     * LOOKUPVALUE('MaterialPrices'[unit_price], 'MaterialPrices'[material_type], "PALLET_COVER")     +
    SUM('MaterialPlan'[SHELF_LINER])      * LOOKUPVALUE('MaterialPrices'[unit_price], 'MaterialPrices'[material_type], "SHELF_LINER")      +
    SUM('MaterialPlan'[COUNTER_DISPLAY])  * LOOKUPVALUE('MaterialPrices'[unit_price], 'MaterialPrices'[material_type], "COUNTER_DISPLAY")  +
    SUM('MaterialPlan'[LIGHT_KIT])        * LOOKUPVALUE('MaterialPrices'[unit_price], 'MaterialPrices'[material_type], "LIGHT_KIT")
```

## 3. Budget allocated to each distributor

The budget is split **proportionally to each distributor's need**, and **capped at that need**
(no one receives more money than they require). `REMOVEFILTERS()` makes the denominator the
total need of all distributors, which keeps the proportion correct regardless of which table
the `distributor_id` on the visual comes from.

```dax
Budget Allocated =
VAR _Proportional =
    DIVIDE([Total Cost], CALCULATE([Total Cost], REMOVEFILTERS())) * [Budget Value]
RETURN
    MIN(_Proportional, [Total Cost])
```

## 4. Coverage, gap and remaining

```dax
Coverage = DIVIDE([Budget Allocated], [Total Cost])      -- fraction of the need funded (<= 1)
```
```dax
Gap = [Total Cost] - [Budget Allocated]                  -- how much is still missing
```

> Because the allocation is proportional to need, **Coverage is uniform across all distributors**
> and equals `Budget Value / total need`. With a budget of 1,000,000 over a total need of ~4,900,000,
> coverage is ~20% for everyone.

## 5. Units funded per material

Apply the (uniform) coverage to each material's planned quantity. `ROUNDDOWN` is used because
you cannot buy a fraction of a unit (and it keeps the spend within budget).

```dax
Flagship Display Funded = ROUNDDOWN(SUM('MaterialPlan'[FLAGSHIP_DISPLAY]) * [Coverage], 0)
Regular Display Funded  = ROUNDDOWN(SUM('MaterialPlan'[REGULAR_DISPLAY])  * [Coverage], 0)
Slim Display Funded     = ROUNDDOWN(SUM('MaterialPlan'[SLIM_DISPLAY])     * [Coverage], 0)
Pallet Cover Funded     = ROUNDDOWN(SUM('MaterialPlan'[PALLET_COVER])     * [Coverage], 0)
Shelf Liner Funded      = ROUNDDOWN(SUM('MaterialPlan'[SHELF_LINER])      * [Coverage], 0)
Counter Display Funded  = ROUNDDOWN(SUM('MaterialPlan'[COUNTER_DISPLAY])  * [Coverage], 0)
Light Kit Funded        = ROUNDDOWN(SUM('MaterialPlan'[LIGHT_KIT])        * [Coverage], 0)
```

## 6. Cost based on funded quantity (optional)

If you want the cost of what the budget actually buys (instead of the planned cost):

```dax
Flagship Display Cost (Funded) =
    [Flagship Display Funded] *
    LOOKUPVALUE('MaterialPrices'[unit_price], 'MaterialPrices'[material_type], "FLAGSHIP_DISPLAY")
```

---

## Notes on the Budget What-If parameter

* A What-If parameter built with `GENERATESERIES(start, end, step)` is **discrete** — it only accepts
  values present in the series. Number of rows = `end / step`; keep it under ~1,000,000.
* A slider over a very large range cannot stop on small values — use the **Dropdown/List** slicer
  style to pick exact values, or keep the range close to realistic budgets.
* `SELECTEDVALUE` returns blank when the slicer is in **range ("Between")** mode; use **Single value**
  mode, or wrap with `MAX(...)`, so the measures always compute.

## Sorting distributors by sell-out

The pipeline already writes a physical `distributor_rank` column (distributors ranked by total
sell-out). In Power BI, set `distributor_id` → **Sort by column** → `distributor_rank`. This avoids a
DAX calculated column with `RANKX` + `CALCULATE`, which can trigger a circular-dependency error.
