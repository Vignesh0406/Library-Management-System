from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    usertype = db.Column(db.Integer) # 1 for Admin/Seller, 2 for Customer

class Book(db.Model):
    __tablename__ = 'books'
    barcode = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), db.ForeignKey('users.email'), nullable=False)
    barcode = db.Column(db.String(100), db.ForeignKey('books.barcode'), nullable=False)
    book_name = db.Column(db.Text)
    qty = db.Column(db.Integer)
    amount = db.Column(db.Float)
    ordered_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='PENDING')
