# app/inventory.py
from book import Book

class Inventory:
    def __init__(self):
        self.books = []  # List of Book objects

    def add_book(self, title, author, price, quantity, category):
        new_book = Book(title, author, price, quantity, category)
        self.books.append(new_book)

    def assign_category(self, title, category):
        for book in self.books:
            if book.title == title:
                book.category = category

    def view_inventory(self):
        return [(book.title, book.author, book.price, book.quantity, book.category) for book in self.books]

    def add_stock(self, title, quantity):
        for book in self.books:
            if book.title == title:
                book.quantity += quantity
