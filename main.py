import pandas as pd

from functions import *


def main():
    # Get the file and read it into a DataFrame
    orders_df = pd.read_csv('~/parse_orders_csv/csv/demars_farms_csa_orders_2023_copy.csv', keep_default_na=False)

    # Pass the DataFrame to our build_order function which will return a list of orders
    orders_list = build_order(orders_df)

    #
    print(f"THERE ARE {len(orders_list)} ORDERS:")
    for order in orders_list:
        print_order(order)

    # Build a new CSV file with the list of orders
    create_new_csv(orders_list)


if __name__ == '__main__':
    main()
