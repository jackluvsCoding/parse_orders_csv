"""User-facing file dialog helpers.

The core parsing/export code should not know anything about Tkinter or opening
files on macOS/Windows/Linux. Keeping that UI behavior here makes the rest of the
project easier to test and maintain.
"""

import os
import subprocess
import sys
from tkinter import filedialog
from typing import Optional

from demars_orders.constants import DEFAULT_OUTPUT_WORKBOOK_NAME


def ask_for_weebly_csv_path() -> Optional[str]:
    """Show a file picker and return the selected Weebly CSV path."""
    file_path = filedialog.askopenfilename(
        title="Select Weebly orders CSV export",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
    )

    return file_path or None


def ask_for_output_workbook_path() -> Optional[str]:
    """Show a save dialog and return the requested workbook path."""
    file_path = filedialog.asksaveasfilename(
        title="Save generated CSA orders workbook",
        defaultextension=".xlsx",
        filetypes=[("Excel Workbook", "*.xlsx")],
        initialfile=DEFAULT_OUTPUT_WORKBOOK_NAME,
    )

    return file_path or None


def open_file(file_path: str) -> None:
    """Open a generated file using the user's operating system.

    This supports the current Mac workflow while also keeping the project usable
    on Windows or Linux if it is run somewhere else later.
    """
    if sys.platform == "darwin":
        subprocess.call(("open", file_path))
    elif os.name == "nt":
        os.startfile(file_path)  # type: ignore[attr-defined]
    else:
        subprocess.call(("xdg-open", file_path))
