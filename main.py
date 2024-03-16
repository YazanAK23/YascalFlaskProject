from flask import Flask, jsonify, request
from datetime import datetime
from bookstore import Bookstore
from book import Book
from inventory import Inventory
from shopping_cart import ShoppingCart
from order import Order
from flask_sqlalchemy import SQLAlchemy
import os 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('sqlite:///bookstore.db')

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key
db = SQLAlchemy(app)


# Define database models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)

class ShoppingCartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    book = db.relationship('Book', backref=db.backref('cart_items', lazy=True))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    items = db.relationship('ShoppingCartItem', backref='order', lazy=True)

# Routes for CRUD operations and validation for Book class
@app.route('/books', methods=['GET'])
def get_books():
    books = Inventory().books
    book_list = []
    for book in books:
        book_list.append({
            'title': book.title,
            'author': book.author,
            'price': book.price,
            'quantity': book.quantity,
            'category': book.category
        })
    return jsonify({'books': book_list})

@app.route('/books/<title>', methods=['GET'])
def get_book(title):
    books = Inventory().books
    for book in books:
        if book.title == title:
            return jsonify({
                'title': book.title,
                'author': book.author,
                'price': book.price,
                'quantity': book.quantity,
                'category': book.category
            })
    return jsonify({'message': 'Book not found'}), 404

@app.route('/books', methods=['POST'])
def add_book():
    try:
        data = request.get_json()
        if 'title' not in data or 'author' not in data or 'price' not in data or 'quantity' not in data or 'category' not in data:
            raise ValueError("Missing required fields")
        bookstore = Bookstore()
        bookstore.add_book_to_inventory(data['title'], data['author'], data['price'], data['quantity'], data['category'])
        return jsonify({'message': 'Book added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/books/<title>', methods=['PUT'])
def update_book(title):
    try:
        data = request.get_json()
        if 'author' not in data or 'price' not in data or 'quantity' not in data or 'category' not in data:
            raise ValueError("Missing required fields")
        inventory = Inventory()
        for book in inventory.books:
            if book.title == title:
                book.author = data['author']
                book.price = data['price']
                book.quantity = data['quantity']
                book.category = data['category']
                return jsonify({'message': 'Book updated successfully'}), 200
        return jsonify({'message': 'Book not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/books/<title>', methods=['DELETE'])
def delete_book(title):
    inventory = Inventory()
    for book in inventory.books:
        if book.title == title:
            inventory.books.remove(book)
            return jsonify({'message': 'Book deleted successfully'}), 200
    return jsonify({'message': 'Book not found'}), 404

from flask import request

@app.route('/shopping_cart', methods=['GET'])
def get_shopping_cart():
    try:
        # Retrieve shopping cart details
        global shopping_cart, inventory

        # Fetch shopping cart items
        cart_items = shopping_cart.view_cart(inventory)

        # Return the cart items as JSON response
        return jsonify({'cart_items': cart_items}), 200

    except Exception as e:
        # Handle any exceptions and return an appropriate error response
        return jsonify({'error': str(e)}), 500


@app.route('/shopping_cart/add', methods=['POST'])
def add_to_shopping_cart():
    try:
        data = request.get_json()
        title = data.get('title')
        quantity = data.get('quantity')
        if not title or not quantity:
            raise ValueError("Title and quantity are required")
        book = next((book for book in inventory.books if book.title == title), None)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        if book.quantity < quantity:
            return jsonify({'error': 'Not enough stock'}), 400
        shopping_cart.add_to_cart(book, quantity)
        return jsonify({'message': 'Book added to shopping cart'}), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/shopping_cart/remove', methods=['POST'])
def remove_from_shopping_cart():
    try:
        data = request.get_json()
        title = data.get('title')
        quantity = data.get('quantity')
        if not title or not quantity:
            raise ValueError("Title and quantity are required")
        book = next((book for book in inventory.books if book.title == title), None)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        if not shopping_cart.remove_from_cart(book, quantity):
            return jsonify({'error': 'Book not found in shopping cart or quantity exceeds cart quantity'}), 400
        return jsonify({'message': 'Book removed from shopping cart'}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

   
@app.route('/shopping_cart/update', methods=['PUT'])
def update_shopping_cart():
    try:
        data = request.get_json()
        title = data.get('title')
        quantity = data.get('quantity')
        if not title or not quantity:
            raise ValueError("Title and quantity are required")
        book = next((book for book in inventory.books if book.title == title), None)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        if book.quantity < quantity:
            return jsonify({'error': 'Not enough stock'}), 400
        shopping_cart.update_cart(book, quantity)
        return jsonify({'message': 'Shopping cart updated successfully'}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

# Routes for CRUD operations and validation for Order class
@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        # Retrieve order details
        # Implement logic to fetch order details
        # For demonstration purposes, let's assume we have a global variable to store order details
        global orders

        # Fetch order details
        order_details = [order.print_order_details() for order in orders]

        # Return the order details as JSON response
        return jsonify({'orders': order_details}), 200
    except Exception as e:
        # Handle any exceptions and return an appropriate error response
        return jsonify({'error': str(e)}), 500

@app.route('/orders/place', methods=['POST'])
def place_order():
    try:
        data = request.get_json()
        cart_items = data.get('cart_items')
        if not cart_items:
            raise ValueError("Cart items are required")
        
        # Assuming order_id is incremented globally
        global order_id
        order_id += 1
        
        # Create an order object
        new_order = Order(cart_items, order_id, datetime.now())
        
        # Add the order to the list of orders
        orders.append(new_order)
        
        return jsonify({'message': 'Order placed successfully', 'order_id': order_id}), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders/cancel', methods=['POST'])
def cancel_order():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        if not order_id:
            raise ValueError("Order ID is required")
        
        # Find the order with the given order_id
        order_to_cancel = next((order for order in orders if order.order_id == order_id), None)
        if not order_to_cancel:
            return jsonify({'error': 'Order not found'}), 404
        
        # Implement cancelation logic
        # For demonstration, let's assume we have a cancel_order method in the Order class
        order_to_cancel.cancel_order()
        
        return jsonify({'message': 'Order canceled successfully'}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/orders/update', methods=['PUT'])
def update_order():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        cart_items = data.get('cart_items')
        if not order_id or not cart_items:
            raise ValueError("Order ID and cart items are required")
        
        # Find the order with the given order_id
        order_to_update = next((order for order in orders if order.order_id == order_id), None)
        if not order_to_update:
            return jsonify({'error': 'Order not found'}), 404
        
        # Update the order with new cart items
        order_to_update.cart_items = cart_items
        
        return jsonify({'message': 'Order updated successfully'}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True)

def add_dummy_data_on_start():
    # Import Book here to ensure it's imported within the application context
    from book import Book  # Assuming 'book' is the correct module name
    
    # Access the app context
    with app.app_context():
        # Check if data already exists
        if not Book.query.all():
            book1 = Book(title="Rich Dad Poor Dad", author="Robert Kiyosaki", price=10, quantity=100, category="Finance")
            book2 = Book(title="Atomic Habits", author="James Clear", price=15, quantity=80, category="Self-help")
            book3 = Book(title="Miracle Morning", author="Hal Elrod", price=12, quantity=50, category="Personal Development")

            db.session.add_all([book1, book2, book3])
            db.session.commit()

# Call the function to add dummy data after running the Flask application
add_dummy_data_on_start()
