"""Application entry point for the DeMars Farms CSA Order Processor.

This file intentionally stays small. It handles the user interaction flow:
1. Ask for the raw Weebly CSV export.
2. Ask where to save the generated workbook.
3. Read the CSV into pandas.
4. Generate the workbook and OptimoRoute import CSV.
5. Open the generated workbook for review.

Most business logic lives in the `demars_orders` package so the codebase is
easier to maintain season after season.
"""

import pandas as pd

from demars_orders.file_dialogs import ask_for_output_workbook_path, ask_for_weebly_csv_path, open_file
from demars_orders.workbook import create_orders_workbook


def main() -> None:
    """Run the end-to-end CSV-to-workbook workflow."""
    input_csv_path = ask_for_weebly_csv_path()
    if not input_csv_path:
        print("No input file selected. Exiting without creating a workbook.")
        return

    output_workbook_path = ask_for_output_workbook_path()
    if not output_workbook_path:
        print("No output file selected. Exiting without creating a workbook.")
        return

    # Read every column as a string so order numbers, phone numbers, and zip codes
    # are not accidentally converted into numbers or stripped of leading zeros.
    raw_orders_df = pd.read_csv(input_csv_path, keep_default_na=False, dtype=str)

    generated_workbook_path = create_orders_workbook(
        raw_orders_df=raw_orders_df,
        output_path=output_workbook_path,
    )

    print(f"Created workbook: {generated_workbook_path}")
    open_file(generated_workbook_path)


if __name__ == "__main__":
    main()
