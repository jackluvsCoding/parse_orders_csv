# DeMars Farms CSA Order Processor

A small Python utility for converting the raw Weebly CSA order export into a cleaner seasonal operations workbook.

## What it does

Given a Weebly orders CSV, the script generates:

- `Raw Import` tab with the original Weebly data
- `All Orders - Clean` tab with one row per order
- `All Pickups` tab
- `All Deliveries` tab
- `All Drops` tab
- `Optimo Import` tab formatted for OptimoRoute
- `Review Needed` tab for rows that need a human check
- `Summary` tab with counts by fulfillment and share size
- A separate `- Optimo Import.csv` file next to the workbook

## How to run

```bash
pip install -r requirements.txt
python main.py
```

The app will prompt you to select the Weebly CSV export and then choose where to save the generated workbook.

## Notes

The parser currently expects the Weebly export format where each order can span multiple rows: one row with customer/order details and one or more rows with product details. It groups rows by `Order #`, extracts product options, and derives share size, fulfillment method, route address, and driver notes.

Fulfillment detection is intentionally pragmatic for quick seasonal use. It recognizes delivery orders from `[DELIVERY]` in the product name and treats farm/farmers market pickups separately from drop-site-style pickup locations.
