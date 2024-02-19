import csv

from objects.order import Order
from objects.product import Product
from file_io import asksaveasfile_csv_wrapper


def create_new_orders_csv(orders: list[Order]):
    file = asksaveasfile_csv_wrapper()

    try:
        with open(file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['order_number', 'date', 'status', 'first_name', 'last_name', 'email', 'address_1',
                             'address_2', 'postal_code', 'city', 'state', 'country', 'phone', 'products', 'notes',
                             'delivery'])
            for order in orders:
                writer.writerow([order.order_number, order.date, order.status, order.first_name, order.last_name,
                                 order.email, order.address_1, order.address_2, order.postal_code, order.city,
                                 order.state, order.country, order.phone, get_product_string(order.products),
                                 order.notes, order.delivery])
            f.close()

    except Exception as e:
        raise Exception(e)

    return file


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

            # If there are more orders, increment 'i' and return to the head of the loop
            if i < len(orders_df) - 1:
                temp_order_id = orders_df['Order #'][i + 1]
                if temp_order_id != order_number:
                    orders_list.append(order)
                i += 1
            # If there are no more orders, break out of the loop
            else:
                if i == len(orders_df) - 1:
                    orders_list.append(order)
                    i += 1
                break
        if i == len(orders_df):
            break
    return orders_list


def print_orders_to_console(orders_list: list[Order]):
    print(f"PRINTING {len(orders_list)} ORDERS TO THE CONSOLE:")
    for order in orders_list:
        order.print_order()
