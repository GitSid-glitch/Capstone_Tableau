# Person A Handoff

This document explains the cleaned outputs produced from the Olist raw files so the analysis, documentation, and Tableau teammates can continue without reworking joins.

## Raw Inputs

The original files are stored in `data/raw/`:

- `olist_customers_dataset.csv`
- `olist_geolocation_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `product_category_name_translation.csv`

## Cleaning Decisions

- Kept raw files unchanged and copied them directly into `data/raw/`.
- Standardized column names to `snake_case`.
- Parsed all timestamp columns into datetime before deriving delivery metrics.
- Filled missing review titles and messages with placeholders so review presence can still be tracked.
- Filled missing product metadata with medians for numeric attributes and `unknown` for category names.
- Added English category names through `product_category_name_translation.csv`.
- Aggregated geolocation rows into one zip-prefix lookup using average latitude/longitude plus modal city/state.
- Enriched customer and seller tables with geolocation information.
- Aggregated order items, payments, and reviews to the order level to avoid one-to-many duplication in Tableau.

## Main Outputs

The processed files are stored in `data/processed/`:

- `olist_orders_master.csv`
  - One row per order
  - Best file for Tableau dashboards that need all order statuses
  - Includes order status, customer region, payment summary, product/category summary, seller summary, review summary, and delivery KPIs
- `olist_delivered_orders_master.csv`
  - One row per delivered order only
  - Best file for EDA, KPI analysis, and hypothesis testing where delivery completion matters
- `olist_order_items_enriched.csv`
  - One row per order item
  - Use only if someone needs product-level or seller-level deep dives
- `olist_customers_clean.csv`
- `olist_sellers_clean.csv`
- `olist_products_clean.csv`
- `olist_zip_geolocation_lookup.csv`

## Recommended Downstream Usage

- Person B should start with `olist_delivered_orders_master.csv` for KPI and statistical work.
- Tableau teammates should start with `olist_orders_master.csv` unless they are building a delivery-only view.
- The documentation person can use `data/processed/etl_summary.json` for row counts, data quality notes, and processed output descriptions.

## Notebook Flow

- `notebooks/01_extraction.ipynb`
  - Confirms raw file presence, shape, and schema
- `notebooks/02A_data_quality_audit.ipynb`
  - Documents nulls, duplicates, and one-to-many join risks
- `notebooks/02_cleaning.ipynb`
  - Runs the Olist cleaning and export workflow
- `notebooks/02B_join_validation.ipynb`
  - Confirms the final order-level model is safe for analysis and Tableau

## Key Derived Columns

- `item_count`
- `unique_products`
- `unique_sellers`
- `total_price`
- `total_freight`
- `order_value`
- `payment_value_total`
- `payment_gap_value`
- `payment_type_primary`
- `review_score`
- `review_has_comment`
- `delivery_days`
- `approval_lag_days`
- `carrier_lag_days`
- `estimated_delivery_gap_days`
- `is_delivered`
- `is_canceled`
- `is_late_delivery`
- `primary_product_category`
- `primary_seller_state`
- `order_purchase_month`
- `order_purchase_quarter`
- `purchase_weekday`

## Notes For Person B

- Delivery-time analysis should use delivered orders only.
- Order-level financial views should generally use `order_value = total_price + total_freight`.
- `payment_gap_value` can be used as a data validation check or for payment/order reconciliation analysis.
- Review text was not translated, so treat text analysis as optional unless the team decides to translate it later.

## Notes For Tableau Team

- Avoid loading review comment text into Tableau unless it is needed for a specific tooltip or detail sheet.
- Use extracts, not live joins.
- Use the order-level file first; only add item-level data if a dashboard question truly needs it.
