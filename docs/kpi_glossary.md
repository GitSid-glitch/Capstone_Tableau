# KPI Glossary

This glossary aligns KPI naming across notebooks, report, and dashboard.

- **Order Count**: Total number of orders in the selected scope.
- **Total Revenue**: Sum of `order_value` for the selected scope.
- **Average Order Value (AOV)**: `Total Revenue / Order Count`.
- **Late Delivery Rate**: Share of delivered orders where `is_late_delivery = 1`.
- **Average Delivery Days**: Mean `delivery_days` for delivered orders.
- **Average Review Score**: Mean `review_score` (optionally filter `review_score > 0`).
- **Payment Share (%)**: Percentage split of orders or revenue by `payment_type_primary`.
