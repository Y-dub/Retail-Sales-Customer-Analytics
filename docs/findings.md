# Retail Sales & Customer Analytics — Current-State Findings

_Dataset: UCI Online Retail (UK online giftware retailer). Rows (raw): 541,909_

## 1. Data quality assessment

| Issue | Rows | % of raw |
|---|---|---|
| Missing CustomerID | 135,080 | 24.9% |
| Missing Description | 1,454 | 0.3% |
| Cancellation invoices (InvoiceNo starts 'C') | 9,288 | 1.7% |
| Non-positive Quantity (<=0) | 10,624 | 2.0% |
| Non-positive UnitPrice (<=0) | 2,517 | 0.5% |
| Exact duplicate rows | 5,268 | 1.0% |
| Unparseable InvoiceDate | 0 | 0.0% |

Date range: 2010-12-01 08:26:00 to 2011-12-09 12:50:00
Distinct countries: 38  |  Distinct StockCodes: 4,070

## 2. Cleaning / validation rules applied

- Drop cancellation invoices (InvoiceNo starts with 'C') -> handled separately as returns
- Drop rows with non-positive Quantity for the SALES view
- Drop rows with non-positive UnitPrice (admin/adjustment lines)
- Drop exact duplicate rows
- Flag (not drop) rows with missing CustomerID -> excluded only from customer-level analysis
- Derive Revenue = Quantity * UnitPrice

Clean SALES rows: 524,878  |  Dropped: 17,031 (3.1%)

## 3. Headline KPIs (clean sales)

- **Total revenue (GBP):** 10,642,111
- **Orders (distinct invoices):** 19,960
- **Customers with ID:** 4,338
- **Distinct products:** 3,922
- **Average order value (GBP):** 533.17
- **Return value (GBP, from cancellations):** -896,812
- **Return rate (return val / gross sales):** 8.4%

## 4. Revenue by month

| Month | Revenue (GBP) |
|---|---|
| 2010-12 | 821,453 |
| 2011-01 | 689,812 |
| 2011-02 | 522,546 |
| 2011-03 | 716,215 |
| 2011-04 | 536,968 |
| 2011-05 | 769,297 |
| 2011-06 | 760,547 |
| 2011-07 | 718,076 |
| 2011-08 | 757,841 |
| 2011-09 | 1,056,435 |
| 2011-10 | 1,151,264 |
| 2011-11 | 1,503,867 |
| 2011-12 | 637,790 |

## 5. Top markets and products

Top countries by revenue:
- United Kingdom: GBP 9,001,744 (84.6%)
- Netherlands: GBP 285,446 (2.7%)
- EIRE: GBP 283,141 (2.7%)
- Germany: GBP 228,678 (2.1%)
- France: GBP 209,625 (2.0%)
- Australia: GBP 138,454 (1.3%)

Top products by revenue:
- DOTCOM POSTAGE: GBP 206,249
- REGENCY CAKESTAND 3 TIER: GBP 174,157
- PAPER CRAFT , LITTLE BIRDIE: GBP 168,470
- WHITE HANGING HEART T-LIGHT HOLDER: GBP 106,237
- PARTY BUNTING: GBP 99,445
- JUMBO BAG RED RETROSPOT: GBP 94,160
- MEDIUM CERAMIC TOP STORAGE JAR: GBP 81,701
- POSTAGE: GBP 78,102

## 6. RFM customer segmentation

| Segment | Customers | Avg spend (GBP) | Total spend (GBP) | % of revenue |
|---|---|---|---|---|
| Champions | 1,317 | 4,927 | 6,488,695 | 73.0% |
| At risk | 1,066 | 1,030 | 1,098,190 | 12.4% |
| Lost / dormant | 1,084 | 651 | 705,285 | 7.9% |
| Loyal | 612 | 823 | 503,476 | 5.7% |
| Recent / promising | 259 | 354 | 91,564 | 1.0% |