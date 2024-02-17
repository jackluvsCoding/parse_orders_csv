import pandas as pd
import csv


class Product:
    def __init__(self, product_id, product_name, product_options, quantity):
        self.product_id = product_id
        self.product_name = product_name
        self.product_options = product_options
        self.quantity = quantity


class Order:
    def __init__(self, order_number: str, date: str, status: str, first_name: str, last_name: str, email: str,
                 address_1: str, address_2: str, postal_code: str, city: str, state: str, country: str, phone: str,
                 products: list[Product], notes: str):

        self.order_number = order_number
        self.date = date
        self.status = status
        self.first_name = first_name.__str__()
        self.last_name = last_name.__str__()
        self.email = email
        self.address_1 = address_1
        self.address_2 = address_2
        self.postal_code = postal_code
        self.city = city
        self.state = state
        self.country = country
        self.phone = phone
        self.products = products
        self.notes = notes
        self.delivery = False


def create_new_csv(orders: list[Order]):
    new_file = 'csv/output_test.csv'
    try:
        with open(new_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['order_number', 'date', 'status', 'first_name', 'last_name', 'email', 'address_1',
                             'address_2', 'postal_code', 'city', 'state', 'country', 'phone', 'products', 'notes',
                             'delivery'])
            for order in orders:
                writer.writerow([order.order_number, order.date, order.status, order.first_name, order.last_name,
                                 order.email, order.address_1, order.address_2, order.postal_code, order.city,
                                 order.state, order.country, order.phone, get_product_string(order.products),
                                 order.notes, order.delivery])
    except Exception as e:
        raise Exception(e)


def get_product_string(products: list[Product]):
    products_list = ''
    product_item = {}
    for product in products:
        product_item['id'] = product.product_id
        product_item['product'] = product.product_name
        product_item['quantity'] = product.quantity
        product_item['Product Options'] = product.product_options

        products_list += product_item.__str__()
    return products_list


def print_order(order):
    products = ''
    for product in order.products:

        product_item = (f"\tid:      {product.product_id}\n"
                        f"\tproduct: {product.product_name}\n"
                        f"\tqty:     {product.quantity}\n"
                        f"\toptions: {product.product_options}\n")
        products += product_item

    print(f"\norder_number:\t{order.order_number}\n"
          f"date:\t{order.date}\n"
          f"status:\t{order.status}\n"
          f"first_name:\t{order.first_name}\n"
          f"last_name:\t{order.last_name}\n"
          f"email:\t{order.email}\n"
          f"address_1:\t{order.address_1}\n"
          f"address_2:\t{order.address_2}\n"
          f"postal_code:\t{order.postal_code}\n"
          f"city:\t{order.city}\n"
          f"state:\t{order.state}\n"
          f"country:\t{order.country}\n"
          f"phone:\t{order.phone}\n"
          f"products:\n{products}\n"
          f"notes:\t{order.notes}\n"
          f"delivery:\t{order.delivery}\n")


def build_order(orders_df):
    orders_list = []
    temp_order_id = orders_df['Order #'][0]
    for i in range(len(orders_df)):
        order_number = orders_df['Order #'][i]
        products = []
        order = Order(order_number='', date='', status='', first_name='', last_name='', email='', address_1='',
                      address_2='', postal_code='', city='', state='', country='', phone='', products=products,
                      notes='')
        while temp_order_id == order_number:

            # Make Products List
            if orders_df['Product Id'][i] != '':
                product = Product(product_id=orders_df['Product Id'][i],
                                  product_name=orders_df['Product Name'][i],
                                  product_options=orders_df['Product Options'][i],
                                  quantity=orders_df['Product Quantity'][i])
                products.append(product)

            # ORDERS
            if orders_df['Order #'][i] != '':
                order.order_number = orders_df['Order #'][i]
            if orders_df['Date'][i] != '':
                order.date = orders_df['Date'][i]
            if orders_df['Status'][i] != '':
                order.status = orders_df['Status'][i]
            if orders_df['Shipping First Name'][i] != '':
                order.first_name = orders_df['Shipping First Name'][i]
            if orders_df['Shipping Last Name'][i] != '':
                order.last_name = orders_df['Shipping Last Name'][i]
            if orders_df['Shipping Email'][i] != '':
                order.email = orders_df['Shipping Email'][i]
            if orders_df['Shipping Address'][i] != '':
                order.address_1 = orders_df['Shipping Address'][i]
            if orders_df['Shipping Address 2'][i] != '':
                order.address_2 = orders_df['Shipping Address 2'][i]
            if orders_df['Shipping Postal Code'][i] != '':
                order.postal_code = orders_df['Shipping Postal Code'][i]
            if orders_df['Shipping City'][i] != '':
                order.city = orders_df['Shipping City'][i]
            if orders_df['Shipping Region'][i] != '':
                order.state = orders_df['Shipping Region'][i]
            if orders_df['Shipping Country'][i] != '':
                order.country = orders_df['Shipping Country'][i]
            if orders_df['Shipping Phone'][i] != '':
                order.phone = orders_df['Shipping Phone'][i]
            order.products = products
            if orders_df['Order Notes'][i] != '':
                order.notes = orders_df['Order Notes'][i]
            if orders_df['Product Options'][i].find('Delivery') != -1:
                order.delivery = True

            if i < len(orders_df) - 1:
                temp_order_id = orders_df['Order #'][i + 1]
                if temp_order_id != order_number:
                    orders_list.append(order)
                i += 1
            else:
                if i == len(orders_df) - 1:
                    orders_list.append(order)
                    i += 1
                break
        if i == len(orders_df):
            break
    return orders_list


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
