# Retail Sales & Customer Analytics — Business Analysis + Data Project

## Live Dashboard
https://public.tableau.com/app/profile/yash.dubey7502/viz/Retail-BA/SalesPerformance

End-to-end project on the UCI **Online Retail** dataset (UK online giftware retailer, 541,909 transactions, Dec 2010 – Dec 2011). It covers the full business-analysis cycle — current-state assessment, requirements, process mapping, gap analysis — alongside the data work: cleaning, modelling (star schema), customer segmentation, and a dashboard.

## What's here
| Path | What it is |
|---|---|
| `analysis/01_profile_and_analyse.py` | Data-quality profiling, cleaning, KPIs, RFM segmentation |
| `analysis/02_figures.py` | Dashboard reference charts |
| `analysis/03_build_dashboard_dataset.py` | Dashboard data source |
| `docs/findings.md` | Current-state findings (the evidence base) |
| `docs/BRD.md` | Business Requirements Document |
| `docs/RTM.md` | Requirements Traceability Matrix |
| `docs/process_maps.md` | As-is / to-be process maps + gap analysis |
| `docs/snowflake_star_schema.sql` | Dimensional model (Snowflake) |
| `docs/dashboard_spec.md` | Tableau build spec |
| `figures/` | Rendered charts |

## Key findings
- **Data quality:** 24.9% of rows have no CustomerID; ~1.7% are cancellations; ~3% are otherwise invalid/duplicate.
- **Revenue concentration:** UK = 84.6% of revenue; Champions (≈30% of customers) drive 73% of revenue.
- **Seasonality:** strong Q4 peak (Nov ≈ £1.5m vs Feb ≈ £0.52m).
- **Returns:** ≈£897k, an 8.4% return rate.

## How to reproduce
```
pip install pandas numpy matplotlib
cd analysis && python 01_profile_and_analyse.py && python 02_figures.py && python 03_build_dashboard_dataset.py
```

## Skills demonstrated
Business analysis (BRD, RTM, process mapping, gap analysis) · requirements definition · SQL/dimensional modelling · Python data cleaning & profiling · RFM segmentation · data-quality assessment · Tableau dashboard design.
