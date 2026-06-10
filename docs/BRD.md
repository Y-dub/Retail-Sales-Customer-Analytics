# Business Requirements Document (BRD)
## Retail Sales & Customer Analytics

| | |
|---|---|
| Author | Yash Dubey |
| Version | 1.0 |
| Date | 09/03/26 |
| Status | Final |



## 1. Purpose & background
The business sells giftware online to UK consumers and overseas wholesalers. Sales and customer reporting is currently manual and inconsistent, with no single modelled source of truth. This project delivers (a) a cleaned, modelled data source and (b) a dashboard so commercial, marketing, and data teams can track performance and prioritise customers and products from the same numbers.

## 2. Current-state problems (evidence-based)
Drawn directly from the data profiling:

| # | Problem | Evidence |
|---|---|---|
| P1 | A large share of sales cannot be attributed to a customer | **24.9%** of rows have no `CustomerID` |
| P2 | Returns/cancellations are mixed into raw transactions | Cancellation invoices = **1.7%** of rows; return value ≈ **£897k (8.4%** of gross) |
| P3 | Non-product lines inflate "product" performance | "DOTCOM POSTAGE" / "POSTAGE" appear among top revenue lines |
| P4 | Duplicate and invalid rows distort totals | ~**1%** exact duplicates; **2%** non-positive quantity; **0.5%** non-positive price |
| P5 | Revenue is highly concentrated and seasonal, but unmonitored | UK = **84.6%** of revenue; Champions (≈30% of customers) = **73%** of revenue; Nov peak ≈ **£1.5m** vs Feb trough ≈ **£0.52m** |


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
| FR2 | The pipeline shall classify any invoice beginning with "C" as a return and exclude it from gross sales | BR1, BR2 |
| FR3 | The pipeline shall derive `Revenue = Quantity x UnitPrice` for all valid sales rows | BR2 |
| FR4 | The model shall hold a product dimension that tags postage/admin StockCodes so they can be excluded from product analysis | BR4 |
| FR5 | The dashboard shall present monthly net revenue, orders, AOV, and return rate with a date filter | BR2, BR5 |
| FR6 | The dashboard shall present RFM segments with customer counts and revenue contribution | BR3 |
| FR7 | The dashboard shall present revenue by country and top products (excl. admin lines) | BR4, BR5 |
| FR8 | A data-quality summary shall report the volume of each known issue per refresh | BR6 |

## 7. Non-functional requirements
| ID | Requirement |
|---|---|
| NFR1 | The dataset shall be reproducible: re-running the pipeline on the same input yields identical outputs |
| NFR2 | Cleaning rules shall be documented and version-controlled (no manual one-off edits) |
| NFR3 | KPI definitions (revenue, order, return, active customer) shall be documented once and reused everywhere |
| NFR4 | The dashboard shall refresh from the modelled tables without manual re-keying |

## 8. Assumptions
- Cancellation invoices ("C" prefix) represent returns/refunds.
- Non-positive price rows are administrative adjustments, not sales.
- The data is historical and complete for the period 2010-12 to 2011-12.

## 9. Acceptance criteria (summary)
The solution is accepted when: the cleaned dataset reconciles to documented row counts; all FRs are demonstrable on the dashboard; KPI definitions match this BRD; and the data-quality summary reproduces the figures in `findings.md`. (Detailed criteria live in the RTM.)
