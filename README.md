# DeMars Farms CSA Order Processor

A small Python utility that converts the raw Weebly CSA order export into a clean seasonal operations workbook and an OptimoRoute-ready import CSV.

The project is designed for the annual DeMars Farms CSA workflow:

```text
Weebly orders export
  -> generated seasonal workbook
  -> OptimoRoute import CSV
  -> delivery/drop-site route planning
```

## What it creates

Given a Weebly orders CSV, the app generates an Excel workbook with these tabs:

| Tab | Purpose |
|---|---|
| `Raw Import` | Original Weebly export, preserved for audit/reference. |
| `All Orders - Clean` | One row per order with full parsed details. |
| `All Pickups` | Lean working tab for pickup orders. |
| `All Deliveries` | Lean working tab for home delivery orders. |
| `All Drops` | Lean working tab for drop-site orders. |
| `Optimo Import` | Route-planning rows formatted for OptimoRoute. |
| `Review Needed` | Rows with missing/suspicious data to check manually. |
| `Summary` | Counts by fulfillment category, fulfillment, and share size. |

It also creates a separate file next to the workbook:

```text
<workbook name> - Optimo Import.csv
```

## How to run

From the project folder:

```bash
pip install -r requirements.txt
python main.py
```

The app will prompt you to:

1. Select the raw Weebly CSV export.
2. Choose where to save the generated workbook.
3. Review the workbook when it opens automatically.

## Project structure

```text
parse_orders_csv/
  main.py
  requirements.txt
  README.md
  .gitignore
  demars_orders/
    __init__.py
    constants.py
    file_dialogs.py
    fulfillment.py
    orders.py
    product_options.py
    reports.py
    text_utils.py
    workbook.py
```

### Module guide

| Module | Responsibility |
|---|---|
| `main.py` | Small application entry point and user workflow. |
| `demars_orders/constants.py` | Shared column names, sheet names, categories, and default filenames. |
| `demars_orders/file_dialogs.py` | Tkinter file pickers and cross-platform file opening. |
| `demars_orders/fulfillment.py` | Delivery/pickup/drop-site classification logic. |
| `demars_orders/orders.py` | Converts raw Weebly rows into one clean row per order. |
| `demars_orders/product_options.py` | Parses values from Weebly's combined `Product Options` text. |
| `demars_orders/reports.py` | Builds working tabs, Optimo import, review queue, and summary data. |
| `demars_orders/text_utils.py` | Common cleanup and formatting helpers. |
| `demars_orders/workbook.py` | Writes the Excel workbook and companion OptimoRoute CSV. |

## Key workflow notes

- Weebly can export each order across multiple rows. The parser groups by `Order #` to create one clean row per order.
- Product options are exported as one combined text field. The app parses pickup/drop site, delivery override, allergies, and preferences out of that field.
- Delivery route addresses use the clean Weebly shipping address by default. Customer-entered delivery overrides are flagged in `Review Needed` when they differ from the shipping address.
- Drop-site rows use the route address parsed from the pickup/drop-site option when available.
- True pickup rows are not included in the OptimoRoute import.

## Annual maintenance checklist

Before running the season workflow each year:

1. Export orders from Weebly as CSV.
2. Run the app and generate a test workbook.
3. Review the `Review Needed` tab.
4. Confirm pickup/drop-site names are classified correctly.
5. Confirm drop-site route addresses are present when those rows should go to OptimoRoute.
6. Upload the generated `- Optimo Import.csv` file to OptimoRoute.

## Future improvement ideas

These are not required for the current workflow, but would make the tool even easier to maintain:

- Add a yearly `config/locations.csv` file for drop-site and pickup-location rules.
- Add a tiny clickable Mac app build using PyInstaller.
- Add a small regression test using a sanitized sample Weebly export.
