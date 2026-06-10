"""
Build one analysis-ready file for the dashboard (Tableau or Power BI).
Includes sales AND returns with flags, so return-rate works, and the RFM
segment is already joined onto every row. Connect to this single CSV and drag.
Run: python 03_build_dashboard_dataset.py
"""
import pandas as pd, numpy as np

df = pd.read_csv("../data/online_retail.csv", encoding="latin1",
                 dtype={"InvoiceNo": str, "StockCode": str})
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%Y %H:%M", errors="coerce")
df = df.drop_duplicates()

df["is_return"] = df["InvoiceNo"].str.startswith("C", na=False)
# keep valid rows: sales need qty>0; returns have qty<0; all need a real price
df = df[df["UnitPrice"] > 0]
df = df[(df["is_return"]) | (df["Quantity"] > 0)]

df["Revenue"] = df["Quantity"] * df["UnitPrice"]
df["Year"] = df["InvoiceDate"].dt.year
df["Month"] = df["InvoiceDate"].dt.month
df["MonthLabel"] = df["InvoiceDate"].dt.to_period("M").astype(str)

# admin / non-product lines (so 'top products' isn't polluted by postage etc.)
admin_desc = {"DOTCOM POSTAGE","POSTAGE","MANUAL","Manual","Adjust bad debt",
              "AMAZON FEE","BANK CHARGES","Discount","CRUK Commission","SAMPLES"}
admin_codes = {"POST","DOT","M","C2","BANK CHARGES","AMAZONFEE","CRUK","D","S","PADS"}
df["is_admin_line"] = df["Description"].isin(admin_desc) | df["StockCode"].isin(admin_codes)

# join RFM segment onto each row by CustomerID
rfm = pd.read_csv("../data/rfm_segments.csv")[["CustomerID","Segment","Recency","Frequency","Monetary"]]
df = df.merge(rfm, on="CustomerID", how="left")
df["Segment"] = df["Segment"].fillna("Unattributed (no CustomerID)")

cols = ["InvoiceNo","StockCode","Description","Quantity","UnitPrice","Revenue",
        "InvoiceDate","Year","Month","MonthLabel","CustomerID","Country",
        "Segment","is_return","is_admin_line"]
df[cols].to_csv("../data/dashboard_data.csv", index=False)

# quick reconciliation so you can trust it matches findings.md
sales = df[~df["is_return"]]
print(f"rows: {len(df):,}")
print(f"gross sales revenue: {sales['Revenue'].sum():,.0f}  (target ~10,642,111)")
print(f"return value: {df[df['is_return']]['Revenue'].sum():,.0f}  (target ~-896,812)")
print(f"orders: {sales['InvoiceNo'].nunique():,}  (target 19,960)")
print("[saved] data/dashboard_data.csv")
