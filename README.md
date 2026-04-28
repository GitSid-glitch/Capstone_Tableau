# Olist E-Commerce Capstone

This repository contains the data engineering, analysis notebooks, and Tableau handoff assets for the Olist Brazilian e-commerce capstone project.

## Project Structure

- `data/raw/` - original source CSV files
- `data/processed/` - cleaned and derived outputs used for analysis and Tableau
- `notebooks/` - extraction, cleaning, EDA, statistical analysis, and final load preparation
- `docs/` - proposal, data dictionary, and teammate handoff notes
- `reports/` - final report and presentation drafting templates
- `tableau/` - dashboard link tracker and screenshot assets

## Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Use Python 3.10+ for best compatibility with the notebook workflow.

## Notebook Execution Order

Run notebooks in this sequence to preserve dependencies:

1. `notebooks/01_extraction.ipynb`
2. `notebooks/02A_data_quality_audit.ipynb`
3. `notebooks/02_cleaning.ipynb`
4. `notebooks/02B_join_validation.ipynb`
5. `notebooks/03_eda.ipynb`
6. `notebooks/04_statistical_analysis.ipynb`
7. `notebooks/05_final_load_prep.ipynb`

## Quick Run Commands

Use these commands after activating the virtual environment:

```bash
jupyter lab
python scripts/etl_pipeline.py --raw-dir data/raw --output-dir data/processed
```

## Troubleshooting

- If notebook imports fail, confirm `.venv` is activated and reinstall `requirements.txt`.
- If charts appear empty, rerun `02_cleaning.ipynb` before EDA/statistical notebooks.
- If Tableau numbers mismatch, regenerate files in `data/processed/` using the ETL script.
