import os
import subprocess
import sys
from tkinter import filedialog


def asksaveasfile_csv_wrapper():
    file_name = filedialog.asksaveasfile(defaultextension=".csv")
    return file_name.name


def asksaveasfile_xlsx_wrapper():
    file_name = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Workbook", "*.xlsx")],
        initialfile="DeMars Farms Orders - Generated.xlsx",
    )
    if not file_name:
        raise ValueError("No output file selected.")
    return file_name


def open_file_after_created(file):
    try:
        if sys.platform == "darwin":
            subprocess.call(("open", file))
        elif os.name == "nt":
            os.startfile(file)  # type: ignore[attr-defined]
        else:
            subprocess.call(("xdg-open", file))
    except Exception as e:
        raise Exception(e)
