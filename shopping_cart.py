# app/shopping_cart.py

class ShoppingCart:
    def __init__(self):
        self.items = []  # List of tuples (Book object, quantity)

    def add_to_cart(self, book, quantity):
        self.items.append((book, quantity))

    def view_cart(self):
        return [(item[0].title, item[0].price, item[1]) for item in self.items]

    def calculate_total(self):
        return sum(item[0].price * item[1] for item in self.items)
