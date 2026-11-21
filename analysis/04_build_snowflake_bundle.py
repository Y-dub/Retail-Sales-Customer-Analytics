"""Build dimension files for the Snowflake star schema (docs/snowflake_star_schema.sql).

Writes snowflake-bundle/dim_customer.csv, dim_product.csv and dim_geography.csv.
The fact table (~540k rows) is generated as fact_sales.csv but kept out of git.
Run after 01_profile_and_analyse.py.
"""

from __future__ import annotations

import pandas as pd
from cleaning import ROOT

DATA, OUT = ROOT / "data", ROOT / "snowflake-bundle"
OUT.mkdir(exist_ok=True)

lines = pd.read_csv(DATA / "classified_lines.csv", low_memory=False, dtype={"InvoiceNo": str, "StockCode": str})
rfm = pd.read_csv(DATA / "rfm_segments.csv")[["CustomerID", "Segment"]]

# Customers: key 0 = unattributed sales (no CustomerID)
cust = pd.DataFrame({"customer_id": sorted(lines["CustomerID"].dropna().unique())})
cust = cust.merge(rfm, left_on="customer_id", right_on="CustomerID", how="left").drop(columns="CustomerID")
cust["segment"] = cust.pop("Segment").fillna("Not segmented")
cust.insert(0, "customer_key", range(1, len(cust) + 1))
cust = pd.concat([pd.DataFrame([{"customer_key": 0, "customer_id": None, "segment": "Unattributed (no CustomerID)"}]),
                  cust], ignore_index=True)
cust["customer_id"] = cust["customer_id"].astype("float64")

# Products: one row per StockCode, most common description, non-product flag from the shared rules
def most_common(s: pd.Series) -> str:
    s = s.dropna()
    return s.mode().iloc[0].strip() if len(s) else "(no description)"


prod = (lines.groupby("StockCode")
        .agg(description=("Description", most_common),
             non_product_category=("non_product_category", "first"))
        .reset_index().rename(columns={"StockCode": "stock_code"}))
prod["is_non_product"] = prod["non_product_category"].notna()
prod.insert(0, "product_key", range(1, len(prod) + 1))

geo = pd.DataFrame({"country": sorted(lines["Country"].unique())})
geo.insert(0, "geo_key", range(1, len(geo) + 1))

known = cust.loc[cust["customer_key"] > 0, ["customer_key", "customer_id"]]
fact = (lines.merge(known, left_on="CustomerID", right_on="customer_id", how="left")
        .merge(prod[["product_key", "stock_code"]], left_on="StockCode", right_on="stock_code", how="left")
        .merge(geo, left_on="Country", right_on="country", how="left"))
fact["customer_key"] = fact["customer_key"].fillna(0).astype(int)
fact["date_key"] = pd.to_datetime(fact["InvoiceDate"]).dt.strftime("%Y%m%d").astype(int)
fact = fact.rename(columns={"InvoiceNo": "invoice_no", "Quantity": "quantity", "UnitPrice": "unit_price",
                            "Revenue": "revenue"})
fact = fact[["invoice_no", "customer_key", "product_key", "geo_key", "date_key", "quantity", "unit_price",
             "revenue", "line_type"]]

cust.to_csv(OUT / "dim_customer.csv", index=False)
prod.to_csv(OUT / "dim_product.csv", index=False)
geo.to_csv(OUT / "dim_geography.csv", index=False)
fact.to_csv(OUT / "fact_sales.csv", index=False)
print(f"dim_customer {len(cust):,} | dim_product {len(prod):,} | dim_geography {len(geo)} | fact_sales {len(fact):,}")
