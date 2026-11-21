"""Shared loading, data-quality checks and line classification for the Online Retail dataset.

Every script imports from here, so the cleaning rules are defined once.

Each raw row gets exactly one ``line_type``, assigned in this order (first match wins):

    duplicate          exact copy of an earlier row
    stock_adjustment   quantity <= 0 on a non-cancellation invoice (price 0: "damaged", "check", ...)
    invalid_price      unit price <= 0
    non_product        postage, carriage, fees, manual adjustments, discounts, samples, gift vouchers
    price_error        product sale priced > 50x that product's median unit price
    order_error        large sale line (>= £10,000) fully reversed by the same customer within 24 hours,
                       and the cancellation line that reverses it
    product_return     other cancellation lines ('C' invoices) for real products
    product_sale       everything else: real product sales

Revenue metrics use product lines only. Net product revenue = product sales + product returns
(returns are negative). Order errors are excluded from both sides and reported separately.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "online_retail.csv"
DATA_URL = (
    "https://raw.githubusercontent.com/databricks/Spark-The-Definitive-Guide/master/"
    "data/retail-data/all/online-retail-dataset.csv"
)

# Non-product stock codes, identified by inspecting every non-numeric StockCode in the data.
# DCGS* codes look similar but are real products (party bags, dog collars), so they are kept.
NON_PRODUCT_CODES = {
    "POST": "Postage",
    "DOT": "Postage",
    "C2": "Carriage",
    "M": "Manual adjustment",
    "m": "Manual adjustment",
    "D": "Discount",
    "S": "Samples",
    "BANK CHARGES": "Fees",
    "AMAZONFEE": "Fees",
    "CRUK": "Fees",
    "B": "Bad debt adjustment",
    "PADS": "Manual adjustment",
}
GIFT_VOUCHER_PREFIX = "gift_"

PRICE_OUTLIER_MULTIPLE = 50
ORDER_ERROR_MIN_VALUE = 10_000
ORDER_ERROR_WINDOW = pd.Timedelta(hours=24)


def load_raw(path: Path = RAW_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run: python analysis/00_download_data.py")
    df = pd.read_csv(path, encoding="latin1", dtype={"InvoiceNo": str, "StockCode": str})
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%Y %H:%M", errors="coerce")
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["is_cancellation"] = df["InvoiceNo"].str.startswith("C", na=False)
    return df


def non_product_category(stock_code: pd.Series) -> pd.Series:
    cat = stock_code.map(NON_PRODUCT_CODES)
    return cat.mask(stock_code.str.startswith(GIFT_VOUCHER_PREFIX, na=False), "Gift voucher")


def _order_error_index(df: pd.DataFrame, candidates: pd.Series) -> pd.Index:
    """Sale lines >= £10k reversed in full (same customer, stock code, quantity) within 24 hours,
    plus the cancellation lines that reverse them."""
    sales = df[candidates & ~df["is_cancellation"] & (df["Revenue"] >= ORDER_ERROR_MIN_VALUE)]
    cancels = df[candidates & df["is_cancellation"]]
    hits = []
    for idx, s in sales.iterrows():
        match = cancels[
            (cancels["CustomerID"] == s["CustomerID"])
            & (cancels["StockCode"] == s["StockCode"])
            & (cancels["Quantity"] == -s["Quantity"])
            & (cancels["InvoiceDate"] >= s["InvoiceDate"])
            & (cancels["InvoiceDate"] <= s["InvoiceDate"] + ORDER_ERROR_WINDOW)
        ]
        if not match.empty:
            hits += [idx, match.index[0]]
    return pd.Index(hits)


def classify(df: pd.DataFrame) -> pd.DataFrame:
    """Add ``line_type`` and ``non_product_category`` (see module docstring for the rules)."""
    df = df.copy()
    line = pd.Series("product_sale", index=df.index, dtype="object")
    unassigned = pd.Series(True, index=df.index)

    def assign(mask: pd.Series, label: str) -> None:
        nonlocal unassigned
        hit = mask & unassigned
        line[hit] = label
        unassigned = unassigned & ~hit

    df["non_product_category"] = non_product_category(df["StockCode"])
    assign(df.duplicated(keep="first"), "duplicate")
    assign(~df["is_cancellation"] & (df["Quantity"] <= 0), "stock_adjustment")
    assign(df["UnitPrice"] <= 0, "invalid_price")
    assign(df["non_product_category"].notna(), "non_product")

    product_sale = unassigned & ~df["is_cancellation"]
    median_price = df.loc[product_sale].groupby("StockCode")["UnitPrice"].median()
    ratio = df["UnitPrice"] / df["StockCode"].map(median_price)
    assign(product_sale & (ratio > PRICE_OUTLIER_MULTIPLE), "price_error")

    err = pd.Series(False, index=df.index)
    err[_order_error_index(df, unassigned)] = True
    assign(err, "order_error")
    assign(df["is_cancellation"], "product_return")

    df["line_type"] = line
    df["is_product_line"] = df["line_type"].isin(["product_sale", "product_return"])
    df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    return df


def data_quality_checks(df: pd.DataFrame) -> pd.DataFrame:
    """Independent checks on the raw rows (a row can fail several) plus what the pipeline does."""
    n = len(df)
    checks = [
        ("Missing CustomerID", df["CustomerID"].isna(),
         "Kept for sales totals; excluded from customer analysis (RFM)"),
        ("Missing Description", df["Description"].isna(), "Kept; description is not used in any metric"),
        ("Cancellation invoice ('C' prefix)", df["is_cancellation"],
         "Treated as returns: netted off product revenue"),
        ("Quantity <= 0 on a non-cancellation invoice", ~df["is_cancellation"] & (df["Quantity"] <= 0),
         "Excluded: stock adjustments ('damaged', 'check'), all priced at £0"),
        ("Unit price <= 0", df["UnitPrice"] <= 0, "Excluded"),
        ("Exact duplicate row", df.duplicated(keep="first"), "Excluded (assumed double-load, not a repeat purchase)"),
        ("Non-product line (postage, fees, adjustments, vouchers)", non_product_category(df["StockCode"]).notna(),
         "Excluded from product metrics; reported separately"),
        ("Unparseable InvoiceDate", df["InvoiceDate"].isna(), "None found"),
    ]
    return pd.DataFrame(
        [{"check": name, "rows": int(mask.sum()), "pct_of_raw": mask.mean() * 100, "action": action}
         for name, mask, action in checks]
    ).assign(raw_rows=n)
