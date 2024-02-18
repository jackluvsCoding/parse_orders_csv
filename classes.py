

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