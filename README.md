# NST DVA Capstone 2 - Project Repository

> **Newton School of Technology | Data Visualization & Analytics**  
> A capstone project using Python, GitHub, and Tableau to turn raw e-commerce data into decision-oriented business insights.

---

## Before You Start

1. Keep the original CSV files unchanged inside `data/raw/`.
2. Run the notebooks in sequence from `01` to `05`.
3. Use the project `.venv` as the notebook kernel in VS Code or Jupyter.
4. Publish the final dashboard and add the public link in `tableau/dashboard_links.md`.
5. Export the final report and presentation assets into `reports/`.

### Quick Start

If you are working locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name capstone-tableau --display-name "capstone-tableau"
jupyter lab
```

If you are working in VS Code:

- Select `Python Environments...`
- Choose the `.venv` interpreter from this project
- Run notebooks using that kernel only

---

## Project Overview

| Field | Details |
|---|---|
| **Project Title** | Olist E-Commerce Analytics Capstone |
| **Sector** | Retail / E-Commerce |
| **Dataset** | Olist Brazilian E-Commerce Public Dataset |
| **Institute** | Newton School of Technology |
| **Tools Used** | Python, Jupyter, Tableau Public, GitHub |

### Working Problem Statement

This project analyzes the Olist Brazilian e-commerce dataset to understand how order value, delivery performance, customer satisfaction, and geography interact in an online marketplace. The goal is to build a reproducible Python ETL and analysis workflow that supports a decision-ready Tableau dashboard.

**Core Business Question**

> How can an e-commerce marketplace improve delivery performance, customer satisfaction, and category-level sales visibility using order-level operational data?

**Decision Supported**

> This analysis helps identify which categories, states, delivery patterns, and order behaviors should be prioritized to improve fulfillment quality and customer experience.

---

## Dataset

| Attribute | Details |
|---|---|
| **Source Name** | Olist Brazilian E-Commerce Public Dataset |
| **Access Link** | [Kaggle Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) |
| **Raw Files Used** | `customers`, `orders`, `order_items`, `payments`, `reviews`, `products`, `sellers`, `geolocation`, `category_translation` |
| **Row Count** | 99,441 orders, 112,650 order items, 1,000,163 raw geolocation rows |
| **Meaningful Columns** | 8+ analytical columns after joins and feature engineering |
| **Format** | CSV |
| **Granularity** | One row per order in the main master dataset |

### Key Analytical Fields

| Column Name | Description | Role in Analysis |
|---|---|---|
| `order_status` | Current order lifecycle state | order health, KPI segmentation |
| `order_purchase_timestamp` | Order purchase datetime | trend analysis, time series |
| `customer_state` | Customer state | geographic drill-down |
| `primary_product_category` | Main product category for the order | category performance |
| `order_value` | Total order value including freight | sales KPIs |
| `delivery_days` | Purchase-to-delivery duration | operational analysis |
| `is_late_delivery` | Late delivery flag | service quality analysis |
| `review_score` | Customer review rating | satisfaction analysis |

For full column definitions, see [`docs/data_dictionary.md`](docs/data_dictionary.md).

---

## Repository Structure

```text
Capstone_Tableau/
|
|-- README.md
|
|-- data/
|   |-- raw/                         # Original dataset files (never edited)
|   `-- processed/                   # Cleaned and derived outputs
|
|-- notebooks/
|   |-- 01_extraction.ipynb
|   |-- 02A_data_quality_audit.ipynb
|   |-- 02_cleaning.ipynb
|   |-- 02B_join_validation.ipynb
|   |-- 03_eda.ipynb
|   |-- 04_statistical_analysis.ipynb
|   `-- 05_final_load_prep.ipynb
|
|-- scripts/
|   `-- etl_pipeline.py
|
|-- tableau/
|   |-- screenshots/
|   `-- dashboard_links.md
|
|-- reports/
|   |-- README.md
|   |-- presentation_outline.md
|   `-- project_report_template.md
|
|-- docs/
|   `-- data_dictionary.md
|
`-- requirements.txt
```

---

## Analytical Pipeline

The project currently follows this workflow:

1. **Extract** - Raw Olist CSV files are stored in `data/raw/` and inspected in `01_extraction.ipynb`.
2. **Audit** - Data quality, missing values, and join risks are profiled in `02A_data_quality_audit.ipynb`.
3. **Clean and Transform** - ETL logic is implemented in `02_cleaning.ipynb` and `scripts/etl_pipeline.py`.
4. **Validate Joins** - Order-level output integrity is checked in `02B_join_validation.ipynb`.
5. **Analyze** - EDA and statistical analysis are performed in notebooks `03` and `04`.
6. **Prepare Tableau Loads** - Final dashboard-ready outputs are prepared in `05_final_load_prep.ipynb`.
7. **Visualize** - Tableau Public dashboards and screenshots are maintained in `tableau/`.

---

## Notebook Execution Order

Run notebooks in this sequence to preserve dependencies:

1. `notebooks/01_extraction.ipynb`
2. `notebooks/02A_data_quality_audit.ipynb`
3. `notebooks/02_cleaning.ipynb`
4. `notebooks/02B_join_validation.ipynb`
5. `notebooks/03_eda.ipynb`
6. `notebooks/04_statistical_analysis.ipynb`
7. `notebooks/05_final_load_prep.ipynb`

---

## Processed Outputs

Main outputs generated by the ETL workflow:

| File | Purpose |
|---|---|
| `data/processed/olist_orders_master.csv` | Main Tableau-ready order-level dataset |
| `data/processed/olist_delivered_orders_master.csv` | Delivered-order subset for deeper analysis |
| `data/processed/olist_order_items_enriched.csv` | Item-level enriched dataset |
| `data/processed/etl_summary.json` | Data quality and output summary |

---

## Setup Notes For Notebook Users

- Use the project `.venv` only.
- Make sure the selected kernel is the `.venv` kernel before running any notebook.
- If imports fail in VS Code, re-select the `.venv` interpreter and restart the notebook kernel.

### Quick Run Commands

```bash
python scripts/etl_pipeline.py --raw-dir data/raw --output-dir data/processed
```

---

## Tableau Handoff

Recommended starting files for downstream dashboard work:

- `olist_orders_master.csv` for order-level Tableau views
- `olist_delivered_orders_master.csv` for delivery and review-focused analysis

Store dashboard screenshots in `tableau/screenshots/` and the public dashboard URL in `tableau/dashboard_links.md`.

---

## Troubleshooting

- If notebook imports fail, confirm `.venv` is activated and reinstall `requirements.txt`.
- If notebook cells run against the wrong Python, re-select the `.venv` kernel.
- If processed files are missing, rerun `02_cleaning.ipynb` or `scripts/etl_pipeline.py`.
- If Tableau numbers mismatch, regenerate the processed files before reconnecting the data source.

---

## Current Status

- Raw Olist source files committed
- ETL pipeline implemented
- Person A notebooks prepared
- Data dictionary in progress
- EDA / statistical analysis / dashboard work continuing
