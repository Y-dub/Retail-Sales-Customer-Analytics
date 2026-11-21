import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
from cleaning import classify, data_quality_checks  # noqa: E402


def frame(rows):
    df = pd.DataFrame(rows, columns=["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate",
                                     "UnitPrice", "CustomerID", "Country"])
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["is_cancellation"] = df["InvoiceNo"].str.startswith("C")
    return df


ROWS = [
    # invoice, code, description, qty, date, price, customer, country
    ("1001", "85123A", "T-LIGHT HOLDER", 6, "2011-01-01 09:00", 2.55, 1.0, "UK"),     # product_sale
    ("1001", "85123A", "T-LIGHT HOLDER", 6, "2011-01-01 09:00", 2.55, 1.0, "UK"),     # duplicate
    ("C1002", "85123A", "T-LIGHT HOLDER", -2, "2011-01-03 09:00", 2.55, 1.0, "UK"),   # product_return
    ("1003", "22000", "damaged", -5, "2011-01-04 09:00", 0.0, None, "UK"),            # stock_adjustment
    ("1004", "22001", "FREE ITEM", 1, "2011-01-04 09:00", 0.0, 2.0, "UK"),            # invalid_price
    ("1005", "POST", "POSTAGE", 1, "2011-01-05 09:00", 18.0, 3.0, "France"),          # non_product
    ("C1006", "AMAZONFEE", "AMAZON FEE", -1, "2011-01-05 09:00", 5000.0, None, "UK"),  # non_product
    ("1007", "gift_0001_20", "Gift Voucher", 1, "2011-01-05 09:00", 20.0, 4.0, "UK"),  # non_product
    ("1008", "23166", "CERAMIC JAR", 74215, "2011-01-18 10:01", 1.04, 5.0, "UK"),      # order_error (sale)
    ("C1009", "23166", "CERAMIC JAR", -74215, "2011-01-18 10:17", 1.04, 5.0, "UK"),    # order_error (cancel)
    ("1010", "22502", "PICNIC BASKET", 1, "2011-02-01 09:00", 10.0, 6.0, "UK"),       # product_sale
    ("1011", "22502", "PICNIC BASKET", 1, "2011-02-02 09:00", 10.0, 7.0, "UK"),       # product_sale
    ("1012", "22502", "PICNIC BASKET", 60, "2011-02-03 09:00", 649.5, 8.0, "UK"),     # price_error
    ("1013", "DCGSSBOY", "BOYS PARTY BAG", 2, "2011-02-04 09:00", 3.0, 9.0, "UK"),    # product_sale (DCGS kept)
]
EXPECTED = ["product_sale", "duplicate", "product_return", "stock_adjustment", "invalid_price", "non_product",
            "non_product", "non_product", "order_error", "order_error", "product_sale", "product_sale",
            "price_error", "product_sale"]


def test_every_row_gets_the_expected_line_type():
    out = classify(frame(ROWS))
    assert out["line_type"].tolist() == EXPECTED


def test_non_product_categories():
    out = classify(frame(ROWS))
    assert out.loc[5, "non_product_category"] == "Postage"
    assert out.loc[6, "non_product_category"] == "Fees"
    assert out.loc[7, "non_product_category"] == "Gift voucher"
    assert pd.isna(out.loc[13, "non_product_category"])


def test_order_errors_net_to_zero_and_are_not_product_lines():
    out = classify(frame(ROWS))
    errs = out[out["line_type"] == "order_error"]
    assert errs["Revenue"].sum() == 0
    assert not errs["is_product_line"].any()


def test_partial_return_is_not_an_order_error():
    rows = [
        ("2001", "23166", "CERAMIC JAR", 20000, "2011-03-01 10:00", 1.0, 5.0, "UK"),
        ("C2002", "23166", "CERAMIC JAR", -500, "2011-03-01 11:00", 1.0, 5.0, "UK"),
    ]
    out = classify(frame(rows))
    assert out["line_type"].tolist() == ["product_sale", "product_return"]


def test_data_quality_checks_count_raw_rows():
    dq = data_quality_checks(frame(ROWS)).set_index("check")
    assert dq.loc["Missing CustomerID", "rows"] == 2
    assert dq.loc["Exact duplicate row", "rows"] == 1
    assert dq.loc["Cancellation invoice ('C' prefix)", "rows"] == 3
