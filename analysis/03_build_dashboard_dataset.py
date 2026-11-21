"""Build one analysis-ready file for the dashboard (Tableau or Power BI).

Every raw row is kept with its line_type, so the dashboard can show product KPIs and still
account for every pound in the raw data. Run after 01_profile_and_analyse.py.
"""

from __future__ import annotations

import pandas as pd
from cleaning import ROOT

DATA = ROOT / "data"

lines = pd.read_csv(DATA / "classified_lines.csv", low_memory=False, dtype={"InvoiceNo": str, "StockCode": str})
rfm = pd.read_csv(DATA / "rfm_segments.csv")[["CustomerID", "Segment"]]

df = lines.merge(rfm, on="CustomerID", how="left")
df["Segment"] = df["Segment"].fillna(
    df["CustomerID"].isna().map({True: "Unattributed (no CustomerID)", False: "Not segmented"}))
df["is_return"] = df["line_type"] == "product_return"
df["MonthLabel"] = df["InvoiceMonth"]

cols = ["InvoiceNo", "StockCode", "Description", "Quantity", "UnitPrice", "Revenue", "InvoiceDate",
        "MonthLabel", "CustomerID", "Country", "Segment", "line_type", "non_product_category",
        "is_product_line", "is_return"]
df[cols].to_csv(DATA / "dashboard_data.csv", index=False)

# Reconciliation against docs/findings.md
p = df[df["is_product_line"]]
sales = p[~p["is_return"]]
print(f"rows: {len(df):,} (all raw rows kept)")
print(f"gross product sales: £{sales['Revenue'].sum():,.0f}")
print(f"product returns:     £{p.loc[p['is_return'], 'Revenue'].sum():,.0f}")
print(f"net product revenue: £{p['Revenue'].sum():,.0f}")
print(f"orders:              {sales['InvoiceNo'].nunique():,}")
print("[saved] data/dashboard_data.csv")
