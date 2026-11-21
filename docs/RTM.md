# Requirements Traceability Matrix (RTM)
## Retail Sales & Customer Analytics

> Each row traces a business need → functional requirement → where it's built (data field / model object) → how it's verified.

| Req ID | Business req | Functional req | Design / data object | Acceptance test | Status |
|---|---|---|---|---|---|
| BR1 | Single clean dataset | FR1, FR2, FR3, FR9 | `clean_sales.csv`; `FACT_SALES` | Every raw row has one line type; counts reconcile to `findings.md` §2 (522,533 product sales, 8,666 product returns) | Done |
| BR2 | Net revenue / orders / AOV over time | FR3, FR5 | `FACT_SALES.revenue`, `DIM_DATE` | Dashboard monthly net revenue matches `revenue_by_month.csv` (Nov 2011 ≈ £1.43m); return rate 2.3% | Done |
| BR3 | Customer value segmentation | FR6 | `rfm_segments.csv`; `DIM_CUSTOMER.segment` | 5 segments present; Champions = 1,309 customers, 76% of net revenue | Done (analysis) |
| BR4 | Separate product vs admin lines | FR4, FR9 | `DIM_PRODUCT.is_admin_line` flag | Top-product chart shows no postage, fee, manual or order-error lines | Done |
| BR5 | Geographic / seasonal concentration | FR5, FR7 | `DIM_DATE`, `DIM_CUSTOMER.country` | Country chart shows UK ≈ 84.7%; month chart shows Q4 peak | Done |
| BR6 | Monitor data quality | FR1, FR8 | data-quality summary table | Refresh reproduces issue counts in `findings.md` §1 (e.g. 24.9% of rows missing CustomerID); `pytest` passes | Done (analysis) |

**Legend:** *Done* = built and verified in the analysis; *Open* = to be completed in the dashboard build.
