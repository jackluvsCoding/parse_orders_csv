"""Excel workbook and CSV export generation.

This module coordinates the full output package:
- one Excel workbook with multiple operational tabs
- one standalone OptimoRoute import CSV beside the workbook

The transformation itself is delegated to focused modules so this file remains
mostly about output shape and Excel formatting.
"""

from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from demars_orders.constants import (
    CLEAN_ORDERS_SHEET,
    DELIVERIES_SHEET,
    DROPS_SHEET,
    OPTIMO_IMPORT_SHEET,
    OPTIMO_IMPORT_SUFFIX,
    PICKUPS_SHEET,
    RAW_IMPORT_SHEET,
    REVIEW_NEEDED_SHEET,
    SUMMARY_SHEET,
)
from demars_orders.orders import build_clean_orders_dataframe
from demars_orders.reports import (
    build_optimo_dataframe,
    build_review_needed_dataframe,
    build_summary_dataframe,
    split_orders_by_fulfillment_category,
)


def autosize_excel_columns(writer: pd.ExcelWriter, sheets: Dict[str, pd.DataFrame]) -> None:
    """Make workbook tabs easier to read.

    The generated workbook is meant to be opened and used directly, not just
    imported elsewhere. Freezing the header row, adding filters, and auto-sizing
    columns saves a little manual cleanup every season.
    """
    for sheet_name, dataframe in sheets.items():
        worksheet = writer.sheets[sheet_name]

        for column_index, column_name in enumerate(dataframe.columns):
            # Use only the first 200 values so very large files remain fast.
            values = dataframe[column_name].astype(str).head(200).tolist()
            max_length = max([len(str(column_name)), *(len(value) for value in values)] or [10])

            # Cap width so columns with long notes/options do not become massive.
            worksheet.set_column(column_index, column_index, min(max(max_length + 2, 10), 45))

        worksheet.freeze_panes(1, 0)

        if len(dataframe.columns) > 0:
            worksheet.autofilter(0, 0, max(len(dataframe), 1), len(dataframe.columns) - 1)


def build_workbook_sheets(raw_orders_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Build every DataFrame that will become a workbook tab."""
    clean_orders = build_clean_orders_dataframe(raw_orders_df)
    optimo_import = build_optimo_dataframe(clean_orders)
    review_needed = build_review_needed_dataframe(clean_orders)
    summary = build_summary_dataframe(clean_orders)
    pickups, deliveries, drops = split_orders_by_fulfillment_category(clean_orders)

    return {
        RAW_IMPORT_SHEET: raw_orders_df,
        CLEAN_ORDERS_SHEET: clean_orders,
        PICKUPS_SHEET: pickups,
        DELIVERIES_SHEET: deliveries,
        DROPS_SHEET: drops,
        OPTIMO_IMPORT_SHEET: optimo_import,
        REVIEW_NEEDED_SHEET: review_needed,
        SUMMARY_SHEET: summary,
    }


def create_orders_workbook(raw_orders_df: pd.DataFrame, output_path: Optional[str] = None) -> str:
    """Create the seasonal workbook and companion OptimoRoute CSV.

    Args:
        raw_orders_df: DataFrame read from the Weebly export CSV.
        output_path: Destination `.xlsx` path selected by the user.

    Returns:
        The path to the generated Excel workbook.
    """
    if output_path is None:
        raise ValueError("An output workbook path is required.")

    workbook_path = Path(output_path)
    sheets = build_workbook_sheets(raw_orders_df)

    with pd.ExcelWriter(workbook_path, engine="xlsxwriter") as writer:
        for sheet_name, dataframe in sheets.items():
            # Excel limits sheet names to 31 characters.
            safe_sheet_name = sheet_name[:31]
            dataframe.to_excel(writer, sheet_name=safe_sheet_name, index=False)

        autosize_excel_columns(writer, {name[:31]: df for name, df in sheets.items()})

    optimo_csv_path = workbook_path.with_name(f"{workbook_path.stem}{OPTIMO_IMPORT_SUFFIX}")
    sheets[OPTIMO_IMPORT_SHEET].to_csv(optimo_csv_path, index=False)

    return str(workbook_path)
