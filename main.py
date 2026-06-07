import pandas as pd
from tkinter import filedialog as fd

from file_io import open_file_after_created
from functions import create_orders_workbook


def main():
    file_path_string = fd.askopenfilename(
        title="Select Weebly orders CSV export",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
    )

    if not file_path_string:
        print("No input file selected.")
        return

    orders_df = pd.read_csv(file_path_string, keep_default_na=False, dtype=str)
    output_file = create_orders_workbook(orders_df)
    print(f"Created workbook: {output_file}")
    open_file_after_created(output_file)


if __name__ == '__main__':
    main()
