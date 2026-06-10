import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 10, "axes.spgrid": True} if False else {"font.size": 10})

clean = pd.read_csv("../data/clean_sales.csv")
rfm = pd.read_csv("../data/rfm_segments.csv")
bym = pd.read_csv("../data/revenue_by_month.csv")

# 1. Monthly revenue
fig, ax = plt.subplots(figsize=(8,3.2))
ax.bar(bym["InvoiceMonth"], bym["Revenue"]/1e6, color="#2E5C8A")
ax.set_title("Monthly revenue (GBP m)"); ax.set_ylabel("GBP m")
plt.xticks(rotation=45, ha="right"); plt.tight_layout()
plt.savefig("../figures/monthly_revenue.png", dpi=120); plt.close()

# 2. RFM segments by revenue
seg = rfm.groupby("Segment")["Monetary"].agg(["size","sum"]).sort_values("sum", ascending=True)
fig, ax = plt.subplots(figsize=(8,3.2))
ax.barh(seg.index, seg["sum"]/1e6, color="#3C7A3C")
ax.set_title("Revenue by RFM segment (GBP m)"); ax.set_xlabel("GBP m")
plt.tight_layout(); plt.savefig("../figures/rfm_segments.png", dpi=120); plt.close()

# 3. Top products (exclude obvious postage/admin lines for the 'real product' view)
admin = ["DOTCOM POSTAGE","POSTAGE","MANUAL","Adjust bad debt","AMAZON FEE"]
prod = clean[~clean["Description"].isin(admin)]
top = prod.groupby("Description")["Revenue"].sum().sort_values(ascending=False).head(8)
fig, ax = plt.subplots(figsize=(8,3.6))
ax.barh([d.title()[:28] for d in top.index[::-1]], top.values[::-1]/1e3, color="#8A5C2E")
ax.set_title("Top products by revenue, excl. postage/admin (GBP k)"); ax.set_xlabel("GBP k")
plt.tight_layout(); plt.savefig("../figures/top_products.png", dpi=120); plt.close()

print("figures saved")
