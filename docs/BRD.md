# Business Requirements Document (BRD)
## Retail Sales & Customer Analytics

| | |
|---|---|
| Author | Yash Dubey |
| Version | 1.1 |
| Date | 09/03/26 |
| Status | Final |



## 1. Purpose & background
The business sells giftware online to UK consumers and overseas wholesalers. Sales and customer reporting is currently manual and inconsistent, with no single modelled source of truth. This project delivers (a) a cleaned, modelled data source and (b) a dashboard so commercial, marketing, and data teams can track performance and prioritise customers and products from the same numbers.

## 2. Current-state problems (evidence-based)
Drawn directly from the data profiling:

| # | Problem | Evidence |
|---|---|---|
| P1 | A large share of sales cannot be attributed to a customer | **24.9%** of rows have no `CustomerID` |
| P2 | Cancellation invoices mix product returns with fees, manual adjustments and order errors | Cancellations total **£897k**, but only **£230k** are product returns (**2.3%** of gross product sales). The rest: fees £251k, two cancelled order errors £246k, manual adjustments £147k |
| P3 | Non-product lines and order errors distort product performance | Postage, fees and manual adjustments sit alongside products; two cancelled bulk orders appeared as the #2 and #6 "best-selling" products |
| P4 | Duplicate and invalid rows distort totals | **1.0%** exact duplicates; **0.2%** stock adjustments (quantity ≤ 0, priced £0); **0.5%** non-positive price; 2 lines priced 100× the product's normal price |
| P5 | Revenue is highly concentrated and seasonal, but unmonitored | UK = **84.7%** of net product revenue; Champions (30% of customers) = **76%**; Nov 2011 ≈ **£1.43m** vs Feb ≈ **£0.50m** |
| P6 | Data-quality issues are not visible to report users | No summary of issue volumes; e.g. **15.2%** of product sales have no `CustomerID` |


## 3. Scope
**In scope:** historical online transaction data; sales, returns, product, and customer-value analysis; a cleaned modelled dataset; a tableau dashboard.
**Out of scope:** real-time/streaming data; in-store EPOS; demand forecasting (phase 2); marketing-automation integration.

## 4. Stakeholders
| Stakeholder | Interest |
|---|---|
| Commercial / Merchandising | Sales, AOV, product performance, seasonality |
| Marketing / CRM | Customer segments, retention, concentration risk |
| Data / Reporting team | Data quality, maintainability, single source of truth |
| Finance | Net revenue after returns |

## 5. Business requirements
| ID | Requirement | Addresses |
|---|---|---|
| BR1 | Provide a single cleaned, documented dataset of sales with consistent definitions of revenue, orders, and returns | P2, P4 |
| BR2 | Report net revenue (gross less returns), orders, AOV, and active customers over time | P5 |
| BR3 | Segment customers by value (RFM) so marketing can target retention spend | P1, P5 |
| BR4 | Separate genuine product performance from postage/admin lines | P3 |
| BR5 | Surface geographic and seasonal concentration so the business can manage the risk | P5 |
| BR6 | Quantify and monitor data-quality issues so they can be reduced over time | P1, P4 |

## 6. Functional requirements
| ID | Requirement | Trace |
|---|---|---|
| FR1 | The pipeline shall flag (not silently drop) rows missing `CustomerID` and exclude them only from customer-level metrics | BR1, BR6 |
| FR2 | The pipeline shall classify cancellation lines ("C" invoices) as product returns, non-product reversals or order errors, and net only product returns off product revenue | BR1, BR2 |
| FR3 | The pipeline shall derive `Revenue = Quantity x UnitPrice` for all valid sales rows | BR2 |
| FR4 | The model shall tag non-product StockCodes (postage, carriage, fees, manual adjustments, discounts, samples, gift vouchers) so they can be excluded from product analysis | BR4 |
| FR5 | The dashboard shall present monthly net revenue, orders, AOV, and return rate with a date filter | BR2, BR5 |
| FR6 | The dashboard shall present RFM segments with customer counts and revenue contribution | BR3 |
| FR7 | The dashboard shall present revenue by country and top products (excl. admin lines) | BR4, BR5 |
| FR8 | A data-quality summary shall report the volume of each known issue per refresh | BR6 |
| FR9 | The pipeline shall exclude order errors (sales ≥ £10,000 fully reversed by the same customer within 24 hours) and price errors (over 50× the product's median price) from product metrics, and report them | BR1, BR4 |

## 7. Non-functional requirements
| ID | Requirement |
|---|---|
| NFR1 | The dataset shall be reproducible: re-running the pipeline on the same input yields identical outputs |
| NFR2 | Cleaning rules shall be documented and version-controlled (no manual one-off edits) |
| NFR3 | KPI definitions (revenue, order, return, active customer) shall be documented once and reused everywhere |
| NFR4 | The dashboard shall refresh from the modelled tables without manual re-keying |

## 8. Assumptions
- Cancellation invoices ("C" prefix) are reversals; only those on product StockCodes are product returns.
- Exact duplicate rows are double-loads, not repeat purchases.
- Non-positive price rows are administrative adjustments, not sales.
- The data is historical and complete for the period 2010-12 to 2011-12.

## 9. Acceptance criteria (summary)
The solution is accepted when: the cleaned dataset reconciles to documented row counts; all FRs are demonstrable on the dashboard; KPI definitions match this BRD; and the data-quality summary reproduces the figures in `findings.md`. (Detailed criteria live in the RTM.)

## 10. Change log
| Version | Change |
|---|---|
| 1.0 | Initial BRD |
| 1.1 | Re-analysis showed cancellation invoices mix product returns with fees, adjustments and order errors. P2–P5 evidence corrected, P6 added, FR2/FR4 revised, FR9 added |
