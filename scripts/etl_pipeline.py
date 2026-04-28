"""ETL pipeline for the Olist capstone project.

Builds cleaned dimension tables plus two Tableau-ready fact tables:
1. an order-level master table with one row per order
2. a delivered-orders analysis table for KPI/statistical work
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


DATE_COLUMNS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "reviews": ["review_creation_date", "review_answer_timestamp"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Olist ETL pipeline.")
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing the original Olist CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory where processed outputs will be written.",
    )
    return parser.parse_args()


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    result = df.copy()
    result.columns = cleaned
    return result


def load_csv(path: Path, date_columns: list[str] | None = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = normalize_columns(df).drop_duplicates().reset_index(drop=True)

    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].astype("string").str.strip()

    if date_columns:
        for column in date_columns:
            if column in df.columns:
                df[column] = pd.to_datetime(df[column], errors="coerce")

    return df


def mode_or_na(series: pd.Series) -> str | pd.NA:
    non_null = series.dropna()
    if non_null.empty:
        return pd.NA
    return non_null.mode().iloc[0]


def build_geolocation_lookup(geolocation: pd.DataFrame) -> pd.DataFrame:
    geo = geolocation.rename(columns={"geolocation_zip_code_prefix": "zip_code_prefix"}).copy()
    grouped = (
        geo.groupby("zip_code_prefix", as_index=False)
        .agg(
            geolocation_lat=("geolocation_lat", "mean"),
            geolocation_lng=("geolocation_lng", "mean"),
            geolocation_city=("geolocation_city", mode_or_na),
            geolocation_state=("geolocation_state", mode_or_na),
        )
        .reset_index(drop=True)
    )
    return grouped


def clean_products(products: pd.DataFrame, translation: pd.DataFrame) -> pd.DataFrame:
    merged = products.merge(translation, on="product_category_name", how="left")
    original_missing_metadata = (
        merged["product_category_name"].isna()
        | merged["product_name_lenght"].isna()
        | merged["product_description_lenght"].isna()
        | merged["product_photos_qty"].isna()
        | merged["product_weight_g"].isna()
        | merged["product_length_cm"].isna()
        | merged["product_height_cm"].isna()
        | merged["product_width_cm"].isna()
    )
    merged["product_category_name_clean"] = merged["product_category_name_english"].fillna(
        merged["product_category_name"]
    )
    merged["product_category_name_clean"] = merged["product_category_name_clean"].fillna("unknown")

    numeric_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    for column in numeric_columns:
        merged[column] = pd.to_numeric(merged[column], errors="coerce")
        merged[column] = merged[column].fillna(merged[column].median())

    volume = (
        merged["product_length_cm"] * merged["product_height_cm"] * merged["product_width_cm"]
    )
    merged["product_volume_cm3"] = volume
    merged["product_has_missing_metadata"] = original_missing_metadata.astype(int)

    return merged


def clean_reviews(reviews: pd.DataFrame) -> pd.DataFrame:
    result = reviews.copy()
    result["review_comment_title"] = result["review_comment_title"].fillna("no_title")
    result["review_comment_message"] = result["review_comment_message"].fillna("no_comment")
    result["review_has_comment"] = (result["review_comment_message"] != "no_comment").astype(int)
    return result


def enrich_customers(customers: pd.DataFrame, geo_lookup: pd.DataFrame) -> pd.DataFrame:
    result = customers.rename(
        columns={
            "customer_zip_code_prefix": "zip_code_prefix",
            "customer_city": "customer_city_raw",
            "customer_state": "customer_state_raw",
        }
    ).merge(geo_lookup, on="zip_code_prefix", how="left")

    result["customer_city"] = result["customer_city_raw"].fillna(result["geolocation_city"])
    result["customer_state"] = result["customer_state_raw"].fillna(result["geolocation_state"])

    return result.drop(columns=["customer_city_raw", "customer_state_raw"])


def enrich_sellers(sellers: pd.DataFrame, geo_lookup: pd.DataFrame) -> pd.DataFrame:
    result = sellers.rename(
        columns={
            "seller_zip_code_prefix": "zip_code_prefix",
            "seller_city": "seller_city_raw",
            "seller_state": "seller_state_raw",
        }
    ).merge(geo_lookup, on="zip_code_prefix", how="left")

    result["seller_city"] = result["seller_city_raw"].fillna(result["geolocation_city"])
    result["seller_state"] = result["seller_state_raw"].fillna(result["geolocation_state"])

    return result.drop(columns=["seller_city_raw", "seller_state_raw"])


def build_order_items_fact(
    order_items: pd.DataFrame,
    products: pd.DataFrame,
    sellers: pd.DataFrame,
) -> pd.DataFrame:
    items = order_items.merge(products, on="product_id", how="left").merge(sellers, on="seller_id", how="left")
    items["price"] = pd.to_numeric(items["price"], errors="coerce")
    items["freight_value"] = pd.to_numeric(items["freight_value"], errors="coerce")
    return items


def aggregate_order_items(items: pd.DataFrame) -> pd.DataFrame:
    sorted_items = items.sort_values(["order_id", "order_item_id"]).copy()

    order_level = (
        sorted_items.groupby("order_id", as_index=False)
        .agg(
            item_count=("order_item_id", "count"),
            unique_products=("product_id", "nunique"),
            unique_sellers=("seller_id", "nunique"),
            total_price=("price", "sum"),
            total_freight=("freight_value", "sum"),
            avg_item_price=("price", "mean"),
            max_item_price=("price", "max"),
            primary_product_category=("product_category_name_clean", mode_or_na),
            primary_seller_state=("seller_state", mode_or_na),
            contains_missing_product_metadata=("product_has_missing_metadata", "max"),
        )
        .reset_index(drop=True)
    )
    return order_level


def aggregate_payments(payments: pd.DataFrame) -> pd.DataFrame:
    result = (
        payments.groupby("order_id", as_index=False)
        .agg(
            payment_records=("payment_sequential", "count"),
            payment_value_total=("payment_value", "sum"),
            payment_installments_max=("payment_installments", "max"),
            payment_type_primary=("payment_type", mode_or_na),
            payment_types_count=("payment_type", "nunique"),
        )
        .reset_index(drop=True)
    )
    return result


def aggregate_reviews(reviews: pd.DataFrame) -> pd.DataFrame:
    result = (
        reviews.groupby("order_id", as_index=False)
        .agg(
            review_score=("review_score", "mean"),
            review_has_comment=("review_has_comment", "max"),
            review_created_at=("review_creation_date", "min"),
            review_answered_at=("review_answer_timestamp", "max"),
        )
        .reset_index(drop=True)
    )
    return result


def derive_order_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["order_purchase_date"] = result["order_purchase_timestamp"].dt.date
    result["order_purchase_month"] = result["order_purchase_timestamp"].dt.to_period("M").astype("string")
    result["order_purchase_quarter"] = result["order_purchase_timestamp"].dt.to_period("Q").astype("string")
    result["order_purchase_year"] = result["order_purchase_timestamp"].dt.year
    result["purchase_weekday"] = result["order_purchase_timestamp"].dt.day_name()

    result["delivery_days"] = (
        result["order_delivered_customer_date"] - result["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    result["approval_lag_days"] = (
        result["order_approved_at"] - result["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    result["carrier_lag_days"] = (
        result["order_delivered_carrier_date"] - result["order_approved_at"]
    ).dt.total_seconds() / 86400
    result["estimated_delivery_gap_days"] = (
        result["order_delivered_customer_date"] - result["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400

    result["is_delivered"] = (result["order_status"] == "delivered").astype(int)
    result["is_canceled"] = (result["order_status"] == "canceled").astype(int)
    result["is_late_delivery"] = (
        (result["is_delivered"] == 1) & (result["estimated_delivery_gap_days"] > 0)
    ).astype(int)

    result["order_value"] = result["total_price"].fillna(0) + result["total_freight"].fillna(0)
    result["payment_gap_value"] = result["payment_value_total"] - result["order_value"]
    result["review_score"] = result["review_score"].fillna(0)
    result["review_label"] = pd.cut(
        result["review_score"],
        bins=[-0.1, 0.1, 2, 3, 4, 5],
        labels=["no_review", "poor", "neutral", "good", "excellent"],
    ).astype("string")

    return result


def build_order_master(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    orders = tables["orders"].copy()
    customers = tables["customers"].copy()
    order_items = tables["order_items"].copy()
    payments = tables["payments"].copy()
    reviews = tables["reviews"].copy()

    master = (
        orders.merge(customers, on="customer_id", how="left")
        .merge(order_items, on="order_id", how="left")
        .merge(payments, on="order_id", how="left")
        .merge(reviews, on="order_id", how="left")
    )

    master = derive_order_features(master)
    return master


def build_clean_tables(raw_dir: Path) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    orders = load_csv(raw_dir / "olist_orders_dataset.csv", DATE_COLUMNS["orders"])
    customers = load_csv(raw_dir / "olist_customers_dataset.csv")
    geolocation = load_csv(raw_dir / "olist_geolocation_dataset.csv")
    order_items = load_csv(raw_dir / "olist_order_items_dataset.csv", DATE_COLUMNS["order_items"])
    payments = load_csv(raw_dir / "olist_order_payments_dataset.csv")
    reviews = load_csv(raw_dir / "olist_order_reviews_dataset.csv", DATE_COLUMNS["reviews"])
    products = load_csv(raw_dir / "olist_products_dataset.csv")
    sellers = load_csv(raw_dir / "olist_sellers_dataset.csv")
    translation = load_csv(raw_dir / "product_category_name_translation.csv")

    geo_lookup = build_geolocation_lookup(geolocation)
    clean_products_df = clean_products(products, translation)
    clean_reviews_df = clean_reviews(reviews)
    clean_customers_df = enrich_customers(customers, geo_lookup)
    clean_sellers_df = enrich_sellers(sellers, geo_lookup)

    order_items_fact = build_order_items_fact(order_items, clean_products_df, clean_sellers_df)
    order_items_agg = aggregate_order_items(order_items_fact)
    payments_agg = aggregate_payments(payments)
    reviews_agg = aggregate_reviews(clean_reviews_df)

    clean_tables = {
        "orders": orders,
        "customers": clean_customers_df,
        "geo_lookup": geo_lookup,
        "order_items_fact": order_items_fact,
        "order_items": order_items_agg,
        "payments": payments_agg,
        "reviews": reviews_agg,
        "products": clean_products_df,
        "sellers": clean_sellers_df,
        "translation": translation,
    }

    raw_tables = {
        "orders": orders,
        "customers": customers,
        "geolocation": geolocation,
        "order_items": order_items,
        "payments": payments,
        "reviews": reviews,
        "products": products,
        "sellers": sellers,
        "translation": translation,
    }

    return raw_tables, clean_tables


def write_outputs(output_dir: Path, clean_tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    output_dir.mkdir(parents=True, exist_ok=True)

    order_master = build_order_master(clean_tables)
    delivered_orders = order_master[order_master["is_delivered"] == 1].copy()

    exports = {
        "olist_orders_master.csv": order_master,
        "olist_delivered_orders_master.csv": delivered_orders,
        "olist_order_items_enriched.csv": clean_tables["order_items_fact"],
        "olist_customers_clean.csv": clean_tables["customers"],
        "olist_sellers_clean.csv": clean_tables["sellers"],
        "olist_products_clean.csv": clean_tables["products"],
        "olist_zip_geolocation_lookup.csv": clean_tables["geo_lookup"],
    }

    for filename, df in exports.items():
        df.to_csv(output_dir / filename, index=False)

    return exports


def build_summary(
    raw_tables: dict[str, pd.DataFrame],
    clean_tables: dict[str, pd.DataFrame],
    exports: dict[str, pd.DataFrame],
) -> dict[str, object]:
    orders = raw_tables["orders"]
    products = raw_tables["products"]
    reviews = raw_tables["reviews"]

    summary = {
        "raw_tables": {name: {"rows": len(df), "columns": len(df.columns)} for name, df in raw_tables.items()},
        "data_quality": {
            "orders_missing_delivery_date": int(orders["order_delivered_customer_date"].isna().sum()),
            "orders_missing_carrier_date": int(orders["order_delivered_carrier_date"].isna().sum()),
            "orders_missing_approval_date": int(orders["order_approved_at"].isna().sum()),
            "reviews_missing_comment_message": int(reviews["review_comment_message"].isna().sum()),
            "products_missing_category_name": int(products["product_category_name"].isna().sum()),
        },
        "processed_outputs": {name: {"rows": len(df), "columns": len(df.columns)} for name, df in exports.items()},
        "recommended_analysis_file": "olist_delivered_orders_master.csv",
        "recommended_tableau_file": "olist_orders_master.csv",
        "join_granularity": {
            "olist_orders_master.csv": "one row per order",
            "olist_order_items_enriched.csv": "one row per order item",
        },
        "order_status_distribution": orders["order_status"].value_counts(dropna=False).to_dict(),
        "tableau_notes": [
            "Use olist_orders_master.csv for order-status views that include canceled/unavailable orders.",
            "Use olist_delivered_orders_master.csv when delivery-time or review analysis requires completed orders only.",
            "Avoid loading long review text into Tableau dashboards unless a specific text view is required.",
        ],
    }
    return summary


def main() -> None:
    args = parse_args()

    raw_tables, clean_tables = build_clean_tables(args.raw_dir)
    exports = write_outputs(args.output_dir, clean_tables)
    summary = build_summary(raw_tables, clean_tables, exports)

    summary_path = args.output_dir / "etl_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str))

    print(f"Processed outputs written to: {args.output_dir.resolve()}")
    for name, details in summary["processed_outputs"].items():
        print(f"- {name}: {details['rows']} rows x {details['columns']} columns")


if __name__ == "__main__":
    main()
