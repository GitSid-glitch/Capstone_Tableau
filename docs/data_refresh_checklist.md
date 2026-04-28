# Data Refresh Checklist

Use this when rerunning the pipeline with updated raw files.

- [ ] Confirm all expected raw CSV files exist in `data/raw/`.
- [ ] Run extraction and audit notebooks to validate schema and null patterns.
- [ ] Run cleaning notebook and verify output row counts.
- [ ] Run join validation notebook and confirm one-row-per-order integrity.
- [ ] Regenerate processed outputs through `05_final_load_prep.ipynb` or `scripts/etl_pipeline.py`.
- [ ] Update report/slide metrics if refreshed outputs changed KPI values.
