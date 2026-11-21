"""Reference charts for the README and dashboard build. Run after 01_profile_and_analyse.py."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from cleaning import ROOT  # noqa: E402

DATA, FIG = ROOT / "data", ROOT / "figures"
INK, MUTED, ACCENT, GRID = "#1F2937", "#9CA3AF", "#2E5C8A", "#E5E7EB"
plt.rcParams.update({
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
})

lines = pd.read_csv(DATA / "classified_lines.csv", low_memory=False)
rfm = pd.read_csv(DATA / "rfm_segments.csv")
by_month = pd.read_csv(DATA / "revenue_by_month.csv")
product = lines[lines["is_product_line"]]


def save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=150)
    plt.close(fig)


# 1. Monthly net revenue (Dec 2011 is a partial month)
fig, ax = plt.subplots(figsize=(8, 3.4))
colours = [MUTED if m == "2011-12" else ACCENT for m in by_month["InvoiceMonth"]]
ax.bar(by_month["InvoiceMonth"], by_month["NetRevenue"] / 1e6, color=colours)
ax.set_title("Net product revenue by month (£m)", loc="left", color=INK)
ax.grid(axis="y", color=GRID)
ax.set_axisbelow(True)
ax.annotate("1–9 Dec only", xy=(len(by_month) - 1, by_month["NetRevenue"].iloc[-1] / 1e6),
            xytext=(0, 6), textcoords="offset points", ha="center", fontsize=9, color=MUTED)
plt.xticks(rotation=45, ha="right")
save(fig, "monthly_revenue.png")

# 2. RFM: share of customers vs share of net revenue
seg = rfm.groupby("Segment")["Monetary"].agg(["size", "sum"])
seg = seg.assign(cust_pct=seg["size"] / seg["size"].sum() * 100, rev_pct=seg["sum"] / seg["sum"].sum() * 100)
seg = seg.sort_values("rev_pct")
fig, ax = plt.subplots(figsize=(8, 3.4))
y = range(len(seg))
ax.barh([i + 0.2 for i in y], seg["rev_pct"], height=0.4, color=ACCENT, label="% of net revenue")
ax.barh([i - 0.2 for i in y], seg["cust_pct"], height=0.4, color=MUTED, label="% of customers")
ax.set_yticks(list(y), seg.index)
for i, (c, r) in enumerate(zip(seg["cust_pct"], seg["rev_pct"], strict=True)):
    ax.text(r + 1, i + 0.2, f"{r:.0f}%", va="center", fontsize=9, color=INK)
    ax.text(c + 1, i - 0.2, f"{c:.0f}%", va="center", fontsize=9, color=MUTED)
ax.set_title("RFM segments: share of customers vs share of net revenue", loc="left", color=INK)
ax.set_xlim(0, 100)
ax.legend(frameon=False, loc="lower right")
save(fig, "rfm_segments.png")

# 3. Top products by net revenue
top = product.groupby("Description")["Revenue"].sum().sort_values().tail(8)
fig, ax = plt.subplots(figsize=(8, 3.6))
ax.barh([d.strip().title()[:34] for d in top.index], top.values / 1e3, color=ACCENT)
ax.set_title("Top products by net revenue (£k), product lines only", loc="left", color=INK)
ax.grid(axis="x", color=GRID)
ax.set_axisbelow(True)
save(fig, "top_products.png")

# 4. What the original "returns" figure was made of
canc = lines[lines["is_cancellation"]].copy()
canc["component"] = canc["line_type"].map({
    "product_return": "Product returns",
    "order_error": "Cancelled order errors (2 orders)",
    "duplicate": "Other",
}).fillna(canc["non_product_category"].map({"Fees": "Fees (Amazon, bank, CRUK)",
                                            "Manual adjustment": "Manual adjustments"}))
canc["component"] = canc["component"].fillna("Other")
parts = (-canc.groupby("component")["Revenue"].sum()).sort_values()
fig, ax = plt.subplots(figsize=(8, 3.2))
bar_colours = [ACCENT if c == "Product returns" else MUTED for c in parts.index]
ax.barh(parts.index, parts.values / 1e3, color=bar_colours)
for i, v in enumerate(parts.values):
    ax.text(v / 1e3 + 4, i, f"£{v / 1e3:,.0f}k", va="center", fontsize=9, color=INK)
ax.set_title(f"The original £{parts.sum() / 1e3:,.0f}k 'returns': only the blue bar is product returns",
             loc="left", color=INK)
ax.set_xlim(0, parts.max() / 1e3 * 1.2)
ax.set_xlabel("£k")
save(fig, "returns_breakdown.png")

print("[saved] figures/monthly_revenue.png, rfm_segments.png, top_products.png, returns_breakdown.png")
