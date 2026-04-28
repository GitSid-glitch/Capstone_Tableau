# Gate 1 Proposal — Go/No-Go Checkpoint

## Problem Statement

Brazilian e-commerce has expanded aggressively over the past decade, with platforms like Olist enabling thousands of small and medium sellers to reach customers across the country. While the growth in order volumes is visible, the operational reality is more complicated — delivery timelines vary widely across regions, customer satisfaction is inconsistent across product categories, and it is unclear which factors most directly drive revenue and fulfilment quality.

This project analyses approximately 100,000 orders placed on the Olist marketplace between September 2016 and October 2018. The central questions we are trying to answer are:

1. Which product categories generate the most revenue, and how does customer satisfaction vary across them?
2. What drives late deliveries, and which states and seller regions are most affected?
3. How do payment method choices correlate with order value and fulfilment outcomes?
4. What operational KPIs should Olist's logistics and category teams track on a monthly basis?

The intended audience for the final dashboard is Olist's operations management team, who need a reliable, filterable view of order fulfilment health across regions, categories, and time periods.

---

## Primary Dataset

**Name:** Olist Brazilian E-Commerce Public Dataset

**Source:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

**Why this dataset qualifies:**
- 9 raw relational CSV files — not a pre-cleaned competition file
- `olist_orders_dataset.csv` alone has 99,441 rows and 8 columns, comfortably exceeding the 5,000-row / 8-column minimums
- Real missing values exist in orders, reviews, and products tables, making the cleaning requirement meaningful
- Covers a two-year period (2016–2018) with temporal, geographic, and category-level variation suitable for KPI analysis and hypothesis testing

**Raw file sizes:**

| Table | Rows | Columns |
|---|---|---|
| olist_orders_dataset.csv | 99,441 | 8 |
| olist_customers_dataset.csv | 99,441 | 5 |
| olist_order_items_dataset.csv | 112,650 | 7 |
| olist_order_payments_dataset.csv | 103,886 | 5 |
| olist_order_reviews_dataset.csv | 99,224 | 7 |
| olist_products_dataset.csv | 32,951 | 9 |
| olist_sellers_dataset.csv | 3,095 | 4 |
| olist_geolocation_dataset.csv | 738,332 | 5 |
| product_category_name_translation.csv | 71 | 2 |

---

## Initial Data Dictionary

Full column-level documentation is in `docs/data_dictionary.md`. Key fields for the proposal:

| Field | Table | Type | Description |
|---|---|---|---|
| order_id | orders | string | Unique order identifier |
| order_status | orders | string | Fulfilment status (delivered, canceled, etc.) |
| order_purchase_timestamp | orders | datetime | When the customer placed the order |
| order_delivered_customer_date | orders | datetime | When the customer received the order |
| order_estimated_delivery_date | orders | datetime | Promised delivery date shown to customer |
| customer_state | customers | string | Brazilian state of the customer |
| product_category_name | products | string | Product category in Portuguese |
| payment_type | payments | string | Payment method used |
| payment_value | payments | float | Total payment amount |
| review_score | reviews | int | Customer rating on a 1–5 scale |
| price | order_items | float | Item price (before freight) |
| freight_value | order_items | float | Freight charge per item |

---

## Backup Datasets

In case the primary dataset is rejected, we have identified two backup datasets from the same sector (Retail / E-Commerce) that also meet the raw data requirements.

### Backup 1 — UCI Online Retail II

**Source:** https://archive.ics.uci.edu/dataset/502/online+retail+ii

**Description:** Transactional sales data from a UK-based online gift retailer covering 2009–2011. Each row is one line item in an invoice.

| Attribute | Value |
|---|---|
| Rows | ~1,067,371 |
| Columns | 8 (InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country) |
| Missing values | Yes — CustomerID is missing for ~25% of rows |
| Format | Raw XLSX, not a competition file |

**Why it qualifies:** Large raw transactional dataset with real nulls, temporal coverage, and geographic variation (countries). Supports revenue, customer segmentation, and time-series KPI analysis.

### Backup 2 — Global Superstore Sales Dataset

**Source:** https://www.kaggle.com/datasets/apoorvaappz/global-super-store-dataset

**Description:** Order-level retail sales data from a global superstore chain covering 2011–2014 across North America, Europe, and Asia-Pacific.

| Attribute | Value |
|---|---|
| Rows | 51,290 |
| Columns | 24 (Order ID, Order Date, Ship Date, Ship Mode, Customer, Segment, Country, Category, Sub-Category, Sales, Quantity, Discount, Profit, etc.) |
| Missing values | Yes — Postal Code is missing for several international rows |
| Format | Raw CSV, not a competition file |

**Why it qualifies:** Multi-region, multi-category retail data with temporal and geographic dimensions. Supports KPI analysis on revenue, profitability, shipping performance, and customer segmentation.
