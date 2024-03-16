# app/bookstore.py
from inventory import Inventory
from order import Order

class Bookstore:
    def __init__(self):
        self.inventory = Inventory()
        self.order_id = 0

    def add_book_to_inventory(self, title, author, price, quantity, category):
        self.inventory.add_book(title, author, price, quantity, category)

    def place_order(self, shopping_cart):
        self.order_id += 1
        order = Order(shopping_cart.items, self.order_id, '2024-02')  # Assuming month's date for demonstration
        return order.print_order_details()
