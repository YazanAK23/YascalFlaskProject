# app/order.py
from datetime import datetime

class Order:
    def __init__(self, cart_items, order_id, date_of_purchase):
        self.cart_items = cart_items  # List of tuples (Book object, quantity)
        self.order_id = order_id
        self.date_of_purchase = date_of_purchase

    def print_order_details(self):
        order_details = {
            'Order ID': self.order_id,
            'Date of Purchase': self.date_of_purchase,
            'Items Purchased': [(item[0].title, item[1]) for item in self.cart_items]
        }
        return order_details
