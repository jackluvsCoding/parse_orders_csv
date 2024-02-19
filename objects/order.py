from objects.product import Product


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

# Class Functions
    def print_order(self):
        products = ''
        for product in self.products:
            product_item = (f"\tid:      {product.product_id}\n"
                            f"\tproduct: {product.product_name}\n"
                            f"\tqty:     {product.quantity}\n"
                            f"\toptions: {product.product_options}\n")
            products += product_item

        print(f"\norder_number:\t{self.order_number}\n"
              f"date:\t{self.date}\n"
              f"status:\t{self.status}\n"
              f"first_name:\t{self.first_name}\n"
              f"last_name:\t{self.last_name}\n"
              f"email:\t{self.email}\n"
              f"address_1:\t{self.address_1}\n"
              f"address_2:\t{self.address_2}\n"
              f"postal_code:\t{self.postal_code}\n"
              f"city:\t{self.city}\n"
              f"state:\t{self.state}\n"
              f"country:\t{self.country}\n"
              f"phone:\t{self.phone}\n"
              f"products:\n{products}\n"
              f"notes:\t{self.notes}\n"
              f"delivery:\t{self.delivery}\n")
