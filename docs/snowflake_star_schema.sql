-- Star schema for Retail Sales & Customer Analytics (Snowflake)
-- One fact table at transaction-line grain, three dimensions and a date dimension.
-- Files: snowflake-bundle/ (built by analysis/04_build_snowflake_bundle.py).
--
-- Why a star: one fact at a single grain (one row per invoice line), denormalised dimensions,
-- and a conformed date dimension, so every KPI is a simple aggregate of FACT_SALES.

CREATE OR REPLACE TABLE DIM_CUSTOMER (
    customer_key   INT PRIMARY KEY,   -- 0 = unattributed sale (no CustomerID in source)
    customer_id    NUMBER,            -- natural key from source
    segment        VARCHAR            -- RFM: Champions / Loyal / Recent / At risk / Lost
);

CREATE OR REPLACE TABLE DIM_PRODUCT (
    product_key           INT PRIMARY KEY,
    stock_code            VARCHAR,
    description           VARCHAR,
    non_product_category  VARCHAR,    -- Postage, Fees, Manual adjustment, ... (NULL for products)
    is_non_product        BOOLEAN     -- FR4
);

CREATE OR REPLACE TABLE DIM_GEOGRAPHY (
    geo_key        INT PRIMARY KEY,
    country        VARCHAR
);

CREATE OR REPLACE TABLE DIM_DATE (
    date_key       INT PRIMARY KEY,   -- yyyymmdd
    full_date      DATE,
    year           INT,
    month          INT,
    month_name     VARCHAR,
    day_of_week    INT
);

CREATE OR REPLACE TABLE FACT_SALES (
    invoice_no     VARCHAR,
    customer_key   INT REFERENCES DIM_CUSTOMER(customer_key),
    product_key    INT REFERENCES DIM_PRODUCT(product_key),
    geo_key        INT REFERENCES DIM_GEOGRAPHY(geo_key),
    date_key       INT REFERENCES DIM_DATE(date_key),
    quantity       INT,
    unit_price     NUMBER(10,2),
    revenue        NUMBER(12,2),      -- quantity * unit_price (FR3)
    line_type      VARCHAR            -- product_sale, product_return, non_product, order_error, ... (FR2, FR9)
);

-- Monthly net product revenue (reconciles to data/revenue_by_month.csv; Nov 2011 ~ £1.43m)
-- SELECT d.year, d.month, SUM(f.revenue) AS net_revenue
-- FROM FACT_SALES f JOIN DIM_DATE d ON f.date_key = d.date_key
-- WHERE f.line_type IN ('product_sale', 'product_return')
-- GROUP BY 1, 2 ORDER BY 1, 2;

-- Product return rate (reconciles to docs/findings.md; 2.3%)
-- SELECT -SUM(CASE WHEN line_type = 'product_return' THEN revenue END)
--        / SUM(CASE WHEN line_type = 'product_sale' THEN revenue END) AS return_rate
-- FROM FACT_SALES;

-- Net revenue by RFM segment (reconciles to findings.md section 6; Champions 76%)
-- SELECT c.segment, COUNT(DISTINCT c.customer_id) AS customers, SUM(f.revenue) AS net_revenue
-- FROM FACT_SALES f JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key
-- WHERE f.line_type IN ('product_sale', 'product_return') AND c.customer_key <> 0
-- GROUP BY 1 ORDER BY net_revenue DESC;
