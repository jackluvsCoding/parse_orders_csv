import pandas as pd

from file_io import open_file_after_created
from functions import *
from tkinter import filedialog


def main():
    # Select file from finder to create orders
    file_path_string = filedialog.askopenfilename()

    # Get the file and read it into a DataFrame
    orders_df = pd.read_csv(file_path_string, keep_default_na=False)

    # Pass the DataFrame to our build_order function which will return a list of orders
    orders_list = build_order(orders_df)

    # Print Orders in Console to Review
    print_orders_to_console(orders_list)

    # Build a new CSV file with the list of orders
    file = create_new_csv(orders_list)
    print(f"FILE: {file}")

    # Open the file for user to view
    open_file_after_created(file)


if __name__ == '__main__':
    main()
