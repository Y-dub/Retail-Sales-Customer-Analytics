"""
Online Retail — current-state data profiling + core analysis.
Outputs real numbers (findings.md) that anchor the BRD, validation rules,
RTM, and dashboard KPIs.
"""
import pandas as pd, numpy as np, json, datetime as dt

RAW = "../data/online_retail.csv"
df = pd.read_csv(RAW, encoding="latin1", dtype={"InvoiceNo": str, "StockCode": str})
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%Y %H:%M", errors="coerce")

n_raw = len(df)
lines = []
def log(s=""): lines.append(s); print(s)

log("# Retail Sales & Customer Analytics — Current-State Findings")
log(f"\n_Dataset: UCI Online Retail (UK online giftware retailer). Rows (raw): {n_raw:,}_\n")

# ---------- 1. DATA QUALITY ASSESSMENT ----------
log("## 1. Data quality assessment\n")
miss_cust = df["CustomerID"].isna().sum()
miss_desc = df["Description"].isna().sum()
cancel = df["InvoiceNo"].str.startswith("C", na=False).sum()
neg_qty = (df["Quantity"] <= 0).sum()
zero_price = (df["UnitPrice"] <= 0).sum()
dupes = df.duplicated().sum()
bad_dates = df["InvoiceDate"].isna().sum()

dq = {
    "Missing CustomerID": (miss_cust, f"{miss_cust/n_raw:.1%}"),
    "Missing Description": (miss_desc, f"{miss_desc/n_raw:.1%}"),
    "Cancellation invoices (InvoiceNo starts 'C')": (cancel, f"{cancel/n_raw:.1%}"),
    "Non-positive Quantity (<=0)": (neg_qty, f"{neg_qty/n_raw:.1%}"),
    "Non-positive UnitPrice (<=0)": (zero_price, f"{zero_price/n_raw:.1%}"),
    "Exact duplicate rows": (dupes, f"{dupes/n_raw:.1%}"),
    "Unparseable InvoiceDate": (bad_dates, f"{bad_dates/n_raw:.1%}"),
}
log("| Issue | Rows | % of raw |")
log("|---|---|---|")
for k,(c,p) in dq.items():
    log(f"| {k} | {c:,} | {p} |")

log(f"\nDate range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}")
log(f"Distinct countries: {df['Country'].nunique()}  |  Distinct StockCodes: {df['StockCode'].nunique():,}")

# ---------- 2. CLEANING RULES ----------
log("\n## 2. Cleaning / validation rules applied\n")
rules = [
    "Drop cancellation invoices (InvoiceNo starts with 'C') -> handled separately as returns",
    "Drop rows with non-positive Quantity for the SALES view",
    "Drop rows with non-positive UnitPrice (admin/adjustment lines)",
    "Drop exact duplicate rows",
    "Flag (not drop) rows with missing CustomerID -> excluded only from customer-level analysis",
    "Derive Revenue = Quantity * UnitPrice",
]
for r in rules: log(f"- {r}")

returns = df[df["InvoiceNo"].str.startswith("C", na=False)].copy()
clean = df[~df["InvoiceNo"].str.startswith("C", na=False)].copy()
clean = clean[(clean["Quantity"] > 0) & (clean["UnitPrice"] > 0)].drop_duplicates()
clean["Revenue"] = clean["Quantity"] * clean["UnitPrice"]
clean["InvoiceMonth"] = clean["InvoiceDate"].dt.to_period("M").astype(str)
log(f"\nClean SALES rows: {len(clean):,}  |  Dropped: {n_raw-len(clean):,} ({(n_raw-len(clean))/n_raw:.1%})")

# ---------- 3. HEADLINE KPIs ----------
log("\n## 3. Headline KPIs (clean sales)\n")
total_rev = clean["Revenue"].sum()
n_orders = clean["InvoiceNo"].nunique()
n_cust = clean["CustomerID"].nunique()
n_prod = clean["StockCode"].nunique()
avg_order = total_rev / n_orders
return_rev = (returns["Quantity"] * returns["UnitPrice"]).sum()
kpis = {
    "Total revenue (GBP)": f"{total_rev:,.0f}",
    "Orders (distinct invoices)": f"{n_orders:,}",
    "Customers with ID": f"{n_cust:,}",
    "Distinct products": f"{n_prod:,}",
    "Average order value (GBP)": f"{avg_order:,.2f}",
    "Return value (GBP, from cancellations)": f"{return_rev:,.0f}",
    "Return rate (return val / gross sales)": f"{abs(return_rev)/total_rev:.1%}",
}
for k,v in kpis.items(): log(f"- **{k}:** {v}")

# ---------- 4. REVENUE BY MONTH ----------
log("\n## 4. Revenue by month\n")
by_month = clean.groupby("InvoiceMonth")["Revenue"].sum().round(0)
log("| Month | Revenue (GBP) |")
log("|---|---|")
for m,v in by_month.items(): log(f"| {m} | {v:,.0f} |")

# ---------- 5. TOP COUNTRIES & PRODUCTS ----------
log("\n## 5. Top markets and products\n")
top_country = clean.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(6).round(0)
log("Top countries by revenue:")
for c,v in top_country.items(): log(f"- {c}: GBP {v:,.0f} ({v/total_rev:.1%})")
top_prod = clean.groupby("Description")["Revenue"].sum().sort_values(ascending=False).head(8).round(0)
log("\nTop products by revenue:")
for p,v in top_prod.items(): log(f"- {p.strip()}: GBP {v:,.0f}")

# ---------- 6. RFM SEGMENTATION ----------
log("\n## 6. RFM customer segmentation\n")
cust = clean.dropna(subset=["CustomerID"]).copy()
snapshot = cust["InvoiceDate"].max() + pd.Timedelta(days=1)
rfm = cust.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x: (snapshot - x.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("Revenue", "sum"),
)
# scores 1-4 (quartiles); recency reversed (lower recency = better)
rfm["R"] = pd.qcut(rfm["Recency"], 4, labels=[4,3,2,1]).astype(int)
rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1,2,3,4]).astype(int)
rfm["M"] = pd.qcut(rfm["Monetary"], 4, labels=[1,2,3,4]).astype(int)
rfm["RFM"] = rfm["R"] + rfm["F"] + rfm["M"]
def seg(row):
    if row["R"] >= 3 and row["F"] >= 3 and row["M"] >= 3: return "Champions"
    if row["R"] >= 3 and row["F"] >= 2: return "Loyal"
    if row["R"] >= 3: return "Recent / promising"
    if row["R"] == 2: return "At risk"
    return "Lost / dormant"
rfm["Segment"] = rfm.apply(seg, axis=1)
seg_summary = rfm.groupby("Segment").agg(
    Customers=("Monetary","size"),
    Avg_Monetary=("Monetary","mean"),
    Total_Monetary=("Monetary","sum"),
).round(0).sort_values("Total_Monetary", ascending=False)
log("| Segment | Customers | Avg spend (GBP) | Total spend (GBP) | % of revenue |")
log("|---|---|---|---|---|")
tot_m = rfm["Monetary"].sum()
for s,r in seg_summary.iterrows():
    log(f"| {s} | {int(r.Customers):,} | {r.Avg_Monetary:,.0f} | {r.Total_Monetary:,.0f} | {r.Total_Monetary/tot_m:.1%} |")

# ---------- save artefacts ----------
clean.to_csv("../data/clean_sales.csv", index=False)
rfm.reset_index().to_csv("../data/rfm_segments.csv", index=False)
by_month.to_csv("../data/revenue_by_month.csv")
with open("../docs/findings.md","w") as f: f.write("\n".join(lines))
print("\n[saved] clean_sales.csv, rfm_segments.csv, revenue_by_month.csv, docs/findings.md")
