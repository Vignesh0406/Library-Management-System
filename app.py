import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Book, Order
from datetime import datetime
import uuid

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///onlinebookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("SECRET_KEY","Vigneshwarnaik") # In a real app, use a secure random key

db.init_app(app)

# Initialize database
with app.app_context():
    db.create_all()
    # Add a default admin/seller if not exists
    admin = User.query.filter_by(email='admin@bookstore.com').first()
    if not admin:
        admin = User(
            email='admin@bookstore.com',
            password='admin',
            firstname='Admin',
            lastname='User',
            address='Store Head Office',
            phone='1234567890',
            usertype=1
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/CustomerLogin.html')
@app.route('/login')
def customer_login_page():
    return render_template('CustomerLogin.html')

@app.route('/SellerLogin.html')
def seller_login_page():
    return render_template('SellerLogin.html')

@app.route('/CustomerRegister.html')
@app.route('/register')
def register_page():
    return render_template('CustomerRegister.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email') or request.form.get('username')
    password = request.form.get('password')
    
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        session['user_email'] = user.email
        session['user_type'] = user.usertype
        session['user_name'] = user.firstname
        
        if user.usertype == 1: # Admin/Seller
            return redirect(url_for('admin_dashboard'))
        else: # Customer
            return redirect(url_for('home'))
    else:
        flash('Incorrect Email or Password', 'danger')
        return redirect(url_for('customer_login_page'))

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('mailid').strip()
    password = request.form.get('password').strip()
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    address = request.form.get('address')
    phone = request.form.get('phone')
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('User already exists', 'danger')
        return redirect(url_for('register_page'))
    
    new_user = User(
        email=email,
        password=password,
        firstname=firstname,
        lastname=lastname,
        address=address,
        phone=phone,
        usertype=2 # Default to Customer
    )
    db.session.add(new_user)
    db.session.commit()
    flash('User Registered Successfully', 'success')
    return redirect(url_for('customer_login_page'))

@app.route('/home')
@app.route('/view_books')
def home():
    if 'user_email' not in session:
        return redirect(url_for('customer_login_page'))
    books = Book.query.all()
    return render_template('CustomerHome.html', books=books)

@app.route('/viewbook') # Compatibility with original links
def view_books():
    return redirect(url_for('home'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_email' not in session:
        return redirect(url_for('customer_login_page'))
    
    barcode = request.form.get('barcode')
    book = Book.query.get(barcode)
    
    if book and book.quantity > 0:
        cart = session.get('cart', {})
        cart[barcode] = cart.get(barcode, 0) + 1
        session['cart'] = cart
        flash(f'Added {book.name} to cart', 'success')
    else:
        flash('Book out of stock', 'danger')
        
    return redirect(request.referrer or url_for('home'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'user_email' not in session:
        return redirect(url_for('customer_login_page'))
    
    barcode = request.form.get('barcode')
    cart = session.get('cart', {})
    
    if barcode in cart:
        if cart[barcode] > 1:
            cart[barcode] -= 1
        else:
            del cart[barcode]
        session['cart'] = cart
        flash('Removed item from cart', 'success')
        
    return redirect(request.referrer or url_for('home'))

@app.route('/cart')
def cart():
    if 'user_email' not in session:
        return redirect(url_for('customer_login_page'))

    cart = session.get('cart', {})
    cart_items = []
    total_amount = 0

    for barcode, qty in cart.items():
        book = Book.query.get(barcode)
        if book:
            item_total = book.price * qty
            total_amount += item_total
            cart_items.append({
                "book": book,
                "qty": qty,
                "total": item_total
            })

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_amount=total_amount
    )
    

@app.route('/checkout')
def checkout():
    if 'user_email' not in session:
        return redirect(url_for('customer_login_page'))
    
    cart = session.get('cart', {})
    cart_items = []
    total_amount = 0
    
    for barcode, qty in cart.items():
        book = Book.query.get(barcode)
        if book:
            item_total = book.price * qty
            total_amount += item_total
            cart_items.append({
                'barcode': barcode,
                'name': book.name,
                'author': book.author,
                'price': book.price,
                'qty': qty,
                'total': item_total
            })
            
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('home'))
        
    return render_template('payment.html', cart_items=cart_items, total_amount=total_amount)

@app.route('/pay', methods=['POST'])
def pay():
    if 'user_email' not in session:
        return redirect(url_for('customer_login_page'))
    
    cart = session.get('cart', {})
    if not cart:
        flash('No items to pay for', 'warning')
        return redirect(url_for('home'))
    
    user_email = session['user_email']
    
    for barcode, qty in cart.items():
        book = Book.query.get(barcode)
        if book and book.quantity >= qty:
            # Update book quantity
            book.quantity -= qty
            
            # Generate Order ID: ORD + BookID + TM - SeqNum
            existing_orders_count = Order.query.filter_by(barcode=barcode).count()
            display_bcode = barcode[:8].upper() if len(barcode) > 13 else barcode
            generated_order_id = f"ORD{display_bcode}TM-{existing_orders_count + 1:02d}"
            
            # Create Order
            new_order = Order(
                order_id=generated_order_id,
                username=user_email,
                barcode=barcode,
                book_name=book.name,
                qty=qty,
                amount=book.price,
                status='PENDING'
            )
            db.session.add(new_order)
        else:
            flash(f'Some items are out of stock: {book.name if book else barcode}', 'danger')
            return redirect(url_for('cart'))
            
    db.session.commit()
    session.pop('cart', None)
    flash('Order placed successfully!', 'success')
    return redirect(url_for('my_orders'))

@app.route('/myorders')
@app.route('/my_orders')
def my_orders():
    if 'user_email' not in session:
        return redirect(url_for('customer_login_page'))
    
    user_email = session['user_email']
    orders = Order.query.filter_by(username=user_email).order_by(Order.ordered_date.desc()).all()
    return render_template('MyOrders.html', orders=orders)

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    if 'user_email' not in session:
        return redirect(url_for('customer_login_page'))
    
    order_id_internal = request.form.get('order_id')
    order = Order.query.get(order_id_internal)
    
    if order and order.username == session['user_email'] and order.status == 'PENDING':
        order.status = 'CANCELLED'
        # Restore stock
        book = Book.query.get(order.barcode)
        if book:
            book.quantity += order.qty
        db.session.commit()
        flash('Order cancelled successfully', 'success')
    else:
        flash('Unable to cancel order', 'danger')
        
    return redirect(url_for('my_orders'))

@app.route('/admin')
@app.route('/admin_dashboard')


def admin_dashboard():
    if 'user_email' not in session or session.get('user_type') != 1:
        return redirect(url_for('seller_login_page'))

    return redirect(url_for('admin_orders'))

@app.route('/adminorders')
@app.route('/admin_orders')
def admin_orders():
    if 'user_email' not in session or session.get('user_type') != 1:
        return redirect(url_for('seller_login_page'))
    
    orders = Order.query.order_by(Order.ordered_date.desc()).all()
    return render_template('AdminOrders.html', orders=orders)

@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    if 'user_email' not in session or session.get('user_type') != 1:
        return redirect(url_for('seller_login_page'))
    
    order_id_internal = request.form.get('orderId')
    new_status = request.form.get('status')
    order = Order.query.get(order_id_internal)
    
    if order:
        order.status = new_status
        db.session.commit()
        flash(f'Order {order.order_id} updated to {new_status}', 'success')
    else:
        flash('Order not found', 'danger')
        
    return redirect(url_for('admin_orders'))

@app.route('/manage_books')
@app.route('/storebooks')
def manage_books():
    if 'user_email' not in session or session.get('user_type') != 1:
        return redirect(url_for('seller_login_page'))
    
    books = Book.query.all()
    return render_template('ManageBooks.html', books=books)

@app.route('/addbook', methods=['GET', 'POST'])
@app.route('/add_book_page', methods=['GET'])
def add_book_page():
    if 'user_email' not in session or session.get('user_type') != 1:
        return redirect(url_for('seller_login_page'))
    
    if request.method == 'POST':
        barcode = request.form.get('barcode')
        if not barcode:
            barcode = str(uuid.uuid4())[:8].upper()
            
        name = request.form.get('name')
        author = request.form.get('author')
        price = float(request.form.get('price'))
        quantity = int(request.form.get('quantity'))
        
        new_book = Book(barcode=barcode, name=name, author=author, price=price, quantity=quantity)
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('manage_books'))
        
    return render_template('AddBook.html', generated_id=str(uuid.uuid4())[:8].upper())

@app.route('/updatebook', methods=['POST'])
def update_book():
    if 'user_email' not in session or session.get('user_type') != 1:
        return redirect(url_for('seller_login_page'))
    
    barcode = request.form.get('bookId')
    book = Book.query.get(barcode)
    
    if request.form.get('name'): # If it's the actual update submission
        book.name = request.form.get('name')
        book.author = request.form.get('author')
        book.price = float(request.form.get('price'))
        book.quantity = int(request.form.get('quantity'))
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('manage_books'))
        
    return render_template('UpdateBook.html', book=book)

@app.route('/removebook', methods=['GET', 'POST'])
def remove_book():
    if 'user_email' not in session or session.get('user_type') != 1:
        return redirect(url_for('seller_login_page'))
    
    if request.method == 'POST':
        barcode = request.form.get('bookId')
        book = Book.query.get(barcode)
        if book:
            db.session.delete(book)
            db.session.commit()
            flash('Book removed successfully!', 'success')
        else:
            flash('Book not found', 'danger')
        return redirect(url_for('manage_books'))
        
    books = Book.query.all()
    return render_template('RemoveBook.html', books=books)

@app.route('/about')
def about():
    if 'user_email' not in session:
        return redirect(url_for('customer_login_page'))
    return render_template('About.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', code="404", message="Page Not Found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', code="500", message="Internal Server Error"), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
