# Data Dictionary — Olist Brazilian E-Commerce Capstone

## Dataset Summary

| Item | Details |
|---|---|
| Dataset name | Olist Brazilian E-Commerce Public Dataset |
| Source | Olist (via Kaggle public release — raw CSV files, not a competition dataset) |
| Sector | Retail / E-Commerce |
| Raw files | 9 CSVs in `data/raw/` |
| Last updated | Dataset covers Sep 2016 – Oct 2018 |
| Primary analysis file | `data/processed/olist_delivered_orders_master.csv` |
| Tableau file | `data/processed/olist_orders_master.csv` |
| Granularity | One row per order in both master files |

---

## Raw Tables

| Table | Rows | Columns | Description |
|---|---|---|---|
| `olist_orders_dataset.csv` | 99,441 | 8 | Core order lifecycle timestamps and status |
| `olist_customers_dataset.csv` | 99,441 | 5 | Customer identifiers and zip code |
| `olist_geolocation_dataset.csv` | 738,332 | 5 | Lat/lng/city/state per zip code prefix |
| `olist_order_items_dataset.csv` | 112,650 | 7 | One row per item in an order |
| `olist_order_payments_dataset.csv` | 103,886 | 5 | Payment method, value, instalments per order |
| `olist_order_reviews_dataset.csv` | 99,224 | 7 | Customer review score and text |
| `olist_products_dataset.csv` | 32,951 | 9 | Product metadata and dimensions |
| `olist_sellers_dataset.csv` | 3,095 | 4 | Seller identifiers and zip code |
| `product_category_name_translation.csv` | 71 | 2 | Portuguese → English category name mapping |

---

## Column Definitions — Order Master Files

Both `olist_orders_master.csv` (99,441 rows) and `olist_delivered_orders_master.csv` (96,478 rows) share the same 50-column schema.

### Source: Orders Table

| Column Name | Data Type | Description | Example Value | Used In | Cleaning Notes |
|---|---|---|---|---|---|
| `order_id` | string | Unique identifier for each order | `e481f51cbdc...` | EDA / KPI / Tableau | Primary key — no nulls |
| `customer_id` | string | Links to the customers table | `d2b7e...` | Join key | No nulls |
| `order_status` | string | Current fulfilment status of the order | `delivered` | Tableau / EDA | Values: delivered, shipped, canceled, unavailable, invoiced, processing, created, approved |
| `order_purchase_timestamp` | datetime | When the customer placed the order | `2017-10-02 10:56:33` | EDA / KPI | Parsed from string; no nulls |
| `order_approved_at` | datetime | When the payment was approved | `2017-10-02 11:07:15` | Delivery lag KPI | 160 rows null — orders that were never approved |
| `order_delivered_carrier_date` | datetime | When the seller handed off to the carrier | `2017-10-04 19:55:00` | Carrier lag KPI | 1,783 nulls — undelivered orders |
| `order_delivered_customer_date` | datetime | When the customer physically received the order | `2017-10-10 21:25:13` | Delivery days KPI | 2,965 nulls — undelivered orders |
| `order_estimated_delivery_date` | datetime | Estimated delivery date shown to the customer at purchase | `2017-10-18 00:00:00` | Late delivery flag | No nulls |

### Source: Customers Table (enriched with geolocation)

| Column Name | Data Type | Description | Example Value | Used In | Cleaning Notes |
|---|---|---|---|---|---|
| `customer_unique_id` | string | Anonymised customer identity — one person can have multiple `customer_id` values | `861eff47...` | Customer analysis | No nulls |
| `zip_code_prefix` | int | First 5 digits of the customer's zip code | `14409` | Geolocation join | No nulls |
| `geolocation_lat` | float | Average latitude of the customer's zip prefix | `-20.499` | Tableau map | Derived from geo lookup; a few nulls where zip not in geo table |
| `geolocation_lng` | float | Average longitude of the customer's zip prefix | `-47.396` | Tableau map | Same as above |
| `geolocation_city` | string | Most common city name for the zip prefix | `franca` | Tableau filter | Lower-cased; filled from geo lookup |
| `geolocation_state` | string | State code from geolocation | `SP` | Tableau filter | Two-letter Brazilian state code |
| `customer_city` | string | City from the customer record (may differ slightly from geolocation) | `franca` | EDA / Tableau | Filled with geolocation city where null |
| `customer_state` | string | State from the customer record | `SP` | EDA / KPI / Tableau | Two-letter state code; used as primary geographic dimension |

### Source: Order Items (aggregated to order level)

| Column Name | Data Type | Description | Example Value | Used In | Cleaning Notes |
|---|---|---|---|---|---|
| `item_count` | int | Total number of items in the order | `2` | EDA / Regression | Aggregated from `order_item_id` count |
| `unique_products` | int | Number of distinct product SKUs in the order | `2` | EDA | nunique of `product_id` per order |
| `unique_sellers` | int | Number of distinct sellers fulfilling the order | `1` | EDA | nunique of `seller_id` per order |
| `total_price` | float | Sum of item prices (before freight) | `141.46` | KPI / Tableau | Sum of `price` across items |
| `total_freight` | float | Sum of freight charges across all items | `19.93` | KPI / Tableau | Sum of `freight_value` across items |
| `avg_item_price` | float | Mean item price within the order | `70.73` | EDA | Mean of `price` per order |
| `max_item_price` | float | Highest-priced item in the order | `141.46` | EDA | Max of `price` per order |
| `primary_product_category` | string | Most common product category in the order (modal) | `health_beauty` | EDA / KPI / Tableau | English category name; `unknown` where category was missing |
| `primary_seller_state` | string | State of the seller responsible for most items in the order | `SP` | EDA / Tableau | Two-letter state code |
| `contains_missing_product_metadata` | int (0/1) | Flag: at least one item in the order had missing product attributes | `0` | Data quality | 1 = at least one item affected |

### Source: Payments (aggregated to order level)

| Column Name | Data Type | Description | Example Value | Used In | Cleaning Notes |
|---|---|---|---|---|---|
| `payment_records` | int | Number of payment transactions recorded for the order | `1` | EDA | Count of payment rows per order |
| `payment_value_total` | float | Total value of all payment transactions | `161.39` | KPI / Tableau | Sum of `payment_value`; should match `order_value` closely |
| `payment_installments_max` | int | Maximum number of instalment splits across payment records | `3` | EDA / Statistical analysis | Proxy for purchase financing behaviour |
| `payment_type_primary` | string | Most common payment method used | `credit_card` | EDA / KPI / Tableau | Modal `payment_type`; values: credit_card, boleto, voucher, debit_card |
| `payment_types_count` | int | Number of distinct payment methods used in the same order | `1` | EDA | Orders using two methods simultaneously are rare but exist |

### Source: Reviews (aggregated to order level)

| Column Name | Data Type | Description | Example Value | Used In | Cleaning Notes |
|---|---|---|---|---|---|
| `review_score` | float | Average review score left by the customer (1–5 scale) | `4.0` | EDA / Statistical analysis / KPI | Mean of all review scores for the order; 0.0 where no review exists |
| `review_has_comment` | int (0/1) | Flag: the customer wrote a written review comment | `1` | EDA | 1 if `review_comment_message` was not the placeholder `no_comment` |
| `review_created_at` | date | Date the review form was sent to the customer | `2017-05-13` | EDA | Earliest review creation date per order |
| `review_answered_at` | datetime | When the customer submitted the review | `2017-05-15 11:34:13` | EDA | Latest answer timestamp per order |

### Derived Columns (added in `derive_order_features`)

| Column Name | Data Type | Description | Formula / Logic | Used In |
|---|---|---|---|---|
| `order_purchase_date` | date | Date portion of the purchase timestamp | `order_purchase_timestamp.dt.date` | Tableau filter |
| `order_purchase_month` | string | Year-month period of the purchase | `order_purchase_timestamp.dt.to_period('M')` | EDA / KPI trend |
| `order_purchase_quarter` | string | Year-quarter period of the purchase | `order_purchase_timestamp.dt.to_period('Q')` | Tableau / EDA |
| `order_purchase_year` | int | Calendar year of the purchase | `order_purchase_timestamp.dt.year` | Tableau filter |
| `purchase_weekday` | string | Day of the week the order was placed | `order_purchase_timestamp.dt.day_name()` | EDA |
| `delivery_days` | float | Total days from purchase to customer receipt | `(order_delivered_customer_date − order_purchase_timestamp) / 86400` | KPI / Statistical analysis |
| `approval_lag_days` | float | Days from purchase to payment approval | `(order_approved_at − order_purchase_timestamp) / 86400` | Regression |
| `carrier_lag_days` | float | Days from payment approval to carrier pickup | `(order_delivered_carrier_date − order_approved_at) / 86400` | Regression / KPI |
| `estimated_delivery_gap_days` | float | Actual delivery date minus estimated date (negative = early) | `(order_delivered_customer_date − order_estimated_delivery_date) / 86400` | Late delivery flag |
| `is_delivered` | int (0/1) | Flag: order status is `delivered` | `order_status == 'delivered'` | Filter |
| `is_canceled` | int (0/1) | Flag: order status is `canceled` | `order_status == 'canceled'` | EDA |
| `is_late_delivery` | int (0/1) | Flag: delivered order arrived after the estimated date | `is_delivered == 1 AND estimated_delivery_gap_days > 0` | KPI / Statistical analysis / Tableau |
| `order_value` | float | Total amount charged to the customer (items + freight) | `total_price + total_freight` | KPI / EDA / Tableau |
| `payment_gap_value` | float | Difference between payment total and order value | `payment_value_total − order_value` | Data validation |
| `review_label` | string | Categorical bucket of review score | Bins: no\_review (0), poor (1–2), neutral (3), good (4), excellent (5) | Tableau colour encoding |

---

## KPI Output Files (`data/processed/`)

| File | Granularity | Key Columns |
|---|---|---|
| `kpi_monthly.csv` | One row per month | `month`, `total_revenue`, `order_count`, `avg_order_value`, `late_delivery_rate`, `avg_review_score`, `avg_delivery_days` |
| `kpi_by_category.csv` | One row per product category | `product_category`, `total_revenue`, `order_count`, `avg_review_score`, `late_delivery_rate` |
| `kpi_by_state.csv` | One row per customer state | `state`, `order_count`, `total_revenue`, `avg_review_score`, `late_delivery_rate`, `avg_delivery_days` |
| `kpi_by_payment_type.csv` | One row per payment method | `payment_type`, `order_count`, `order_share_pct`, `revenue_share_pct`, `avg_order_value` |
| `kpi_by_seller_state.csv` | One row per seller state (≥100 orders) | `seller_state`, `avg_delivery_days`, `avg_carrier_lag`, `late_delivery_rate` |
| `tableau_ready_dataset.csv` | One row per order (all statuses) | Full master + monthly benchmark columns |

---

## Data Quality Notes

- **2,965 orders** are missing `order_delivered_customer_date` — these are non-delivered orders and are excluded from `olist_delivered_orders_master.csv`. Do not use `delivery_days` or `is_late_delivery` for these rows.
- **58,247 reviews** had no written comment. These were filled with the placeholder `no_comment` and the `review_has_comment` flag was set to 0. Do not use review text for quantitative analysis.
- **610 products** were missing `product_category_name`. Numeric metadata was filled with column medians; category was set to `unknown`.
- **`review_score` is set to 0.0** for orders with no review record at all. Filter to `review_score > 0` before computing satisfaction averages if you want to exclude non-reviewers.
- **`payment_gap_value`** should be near zero for most orders. Large values indicate split payments or data entry inconsistencies — useful as a data validation check, not a business metric.
- The dataset ends in **late 2018**; the last 1–2 months have noticeably lower volume because orders placed near the cutoff were still in transit when the snapshot was taken.
