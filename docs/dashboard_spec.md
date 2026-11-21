# Dashboard build spec

Data source: `data/dashboard_data.csv` from `analysis/03_build_dashboard_dataset.py`. Every raw row is
kept and tagged with `line_type`, so totals reconcile to `docs/findings.md`.

## Page 1: Sales performance

- **KPI cards:** Net product revenue (£9.73m), Orders (19,769), AOV (£504), Return rate (2.3%).
- **Monthly net revenue** (column): peaks in Nov 2011 at about £1.43m. Label December 2011 as partial
  (1–9 December only).
- **Net revenue by country** (bar): UK ≈ 84.7%. Note the concentration risk.
- **Top products by net revenue** (bar): product lines only. Paper Craft and the ceramic storage jar must
  **not** appear; if they do, the filter is wrong.
- **Month filter.**

## Page 2: Customer value

- **RFM segments:** % of customers next to % of net revenue (Champions: 30% of customers, 76% of revenue).
  Exclude "Unattributed (no CustomerID)" and "Not segmented".
- **Average net spend per segment.**
- One sentence of insight per visual, e.g. "76% of revenue comes from 30% of customers, so losing a few
  Champions would hurt".

## Page 3: Data quality

- **Rows by `line_type`** (bar) and **value by `line_type`** (bar), so users see what was excluded.
- **Returns breakdown:** the £897k on cancellation invoices split into product returns, fees, manual
  adjustments and order errors (as in `figures/returns_breakdown.png`).
- **% of product sales without CustomerID** (card): 15.2%.

## Calculations

| Measure | Tableau calculated field | Power BI (DAX) measure |
| --- | --- | --- |
| Gross sales | `SUM(IF [line_type] = "product_sale" THEN [Revenue] END)` | `CALCULATE ( SUM ( dashboard_data[Revenue] ), dashboard_data[line_type] = "product_sale" )` |
| Returns | `SUM(IF [line_type] = "product_return" THEN [Revenue] END)` | `CALCULATE ( SUM ( dashboard_data[Revenue] ), dashboard_data[line_type] = "product_return" )` |
| Net revenue | `[Gross sales] + [Returns]` | `[Gross sales] + [Returns]` |
| Return rate | `-[Returns] / [Gross sales]` | `DIVIDE ( -[Returns], [Gross sales] )` |
| Orders | `COUNTD(IF [line_type] = "product_sale" THEN [InvoiceNo] END)` | `CALCULATE ( DISTINCTCOUNT ( dashboard_data[InvoiceNo] ), dashboard_data[line_type] = "product_sale" )` |
| AOV | `[Gross sales] / [Orders]` | `DIVIDE ( [Gross sales], [Orders] )` |
| % of net revenue (segment, country) | `[Net revenue] / TOTAL([Net revenue])` (table calculation) or `{FIXED [Segment] : ...}` LOD | `DIVIDE ( [Net revenue], CALCULATE ( [Net revenue], ALL ( dashboard_data[Segment] ) ) )` |

The Power BI column shows how the same logic is built in DAX: Tableau's row-level `IF` inside an
aggregate becomes a `CALCULATE` filter, and a share of the total uses `ALL` to remove the segment filter.

## Changes to make in the current Tableau workbook (v1 → v2)

1. Replace the data source with the new `dashboard_data.csv`.
2. **Net Revenue card:** it currently shows £10,642,111, which is gross sales including fees and
   postage. Use the `Net revenue` field above (£9,731,699).
3. **Return Rate card:** use the new `Return rate` (2.3%, previously 8.4%).
4. **Orders:** use the new `Orders` (19,769).
5. **Top Products:** filter to `is_product_line = True` and use `Net revenue`.
6. **Customer Segments:** remove the "Distinct count" axis clutter; show % of customers vs % of revenue,
   as in `figures/rfm_segments.png`.
7. **Layout:** fix the wrapped "Net Rev-enue" title (widen the card or shorten to "Net revenue"), reduce
   the empty space under the KPI row, and add the Data quality page.
8. Republish to Tableau Public and save a new screenshot as `figures/sales_performance.png`.
