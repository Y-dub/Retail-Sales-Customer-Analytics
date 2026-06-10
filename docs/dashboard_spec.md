# Tableau Dashboard — Build Spec


## Page 1 — Sales performance
- **KPI cards:** Net revenue (£10.6m gross), Orders (19,960), AOV (£533), Return rate (8.4%).
- **Monthly net revenue** (column) — should peak Nov 2011 ≈ £1.5m. *(see figures/monthly_revenue.png)*
- **Revenue by country** (bar) — UK ≈ 84.6%. Add a note/visual calling out concentration risk.
- **Top products** — exclude admin lines (`is_admin_line`/the postage StockCodes), or your top list will be wrong. *(see figures/top_products.png)*
- **Date slicer.**

## Page 2 — Customer value
- **RFM segment table/bar:** Champions 1,317 customers / 73% of revenue; show all 5 segments. *(see figures/rfm_segments.png)*
- **Avg spend per segment.**
- One sentence of insight per visual (e.g. "73% of revenue sits with 30% of customers → retention risk concentrated").

## Suggested Calculated Fields
```
Net Revenue = SUMX(FACT_SALES, IF(FACT_SALES[is_return], 0, FACT_SALES[revenue]))
Orders = DISTINCTCOUNT(FACT_SALES[invoice_no])
AOV = DIVIDE([Net Revenue], [Orders])
```
