-- Star schema for Retail Sales & Customer Analytics (Snowflake)
-- Load target for clean_sales.csv after cleaning. Dimensions + one fact.
-- You should be able to explain WHY this is a star (one fact, denormalised dims,
-- conformed DIM_DATE) if asked.

CREATE OR REPLACE TABLE DIM_CUSTOMER (
    customer_key   INT AUTOINCREMENT PRIMARY KEY,
    customer_id    NUMBER,            -- natural key from source; NULL = unattributed sale
    country        VARCHAR,
    segment        VARCHAR            -- from RFM: Champions / Loyal / At risk / Lost / Recent
);

CREATE OR REPLACE TABLE DIM_PRODUCT (
    product_key    INT AUTOINCREMENT PRIMARY KEY,
    stock_code     VARCHAR,
    description    VARCHAR,
    is_admin_line  BOOLEAN            -- TRUE for POSTAGE / DOTCOM POSTAGE / MANUAL etc (FR4)
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
    sales_key      INT AUTOINCREMENT PRIMARY KEY,
    invoice_no     VARCHAR,
    customer_key   INT REFERENCES DIM_CUSTOMER(customer_key),
    product_key    INT REFERENCES DIM_PRODUCT(product_key),
    date_key       INT REFERENCES DIM_DATE(date_key),
    quantity       INT,
    unit_price     NUMBER(10,2),
    revenue        NUMBER(12,2),      -- quantity * unit_price (FR3)
    is_return      BOOLEAN            -- TRUE if source invoice began with 'C' (FR2)
);

-- Example KPI query: monthly net revenue (should reconcile to revenue_by_month.csv)
-- SELECT d.year, d.month, SUM(CASE WHEN f.is_return THEN 0 ELSE f.revenue END) AS net_revenue
-- FROM FACT_SALES f JOIN DIM_DATE d ON f.date_key = d.date_key
-- GROUP BY 1,2 ORDER BY 1,2;

-- Example: revenue by RFM segment (should reconcile to findings.md section 6)
-- SELECT c.segment, COUNT(DISTINCT c.customer_id) AS customers, SUM(f.revenue) AS revenue
-- FROM FACT_SALES f JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key
-- WHERE NOT f.is_return AND c.customer_id IS NOT NULL
-- GROUP BY 1 ORDER BY revenue DESC;
