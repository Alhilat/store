import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = '12487fgh' # Change this for a real site

# 1. Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'store.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 2. Database Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)

# Create the database file automatically
with app.app_context():
    db.create_all()

# 3. Routes: Public Store
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    session.modified = True
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    cart_ids = session.get('cart', [])
    # Fetch actual product objects from DB based on IDs in session
    cart_items = [Product.query.get(pid) for pid in cart_ids if Product.query.get(pid)]
    total = sum(item.price for item in cart_items)
    return render_template('cart.html', items=cart_items, total=total)

# 4. Routes: Admin Panel
@app.route('/admin')
def admin_dashboard():
    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/admin/add', methods=['POST'])
def admin_add_product():
    name = request.form.get('name')
    price = int(request.form.get('price'))
    new_product = Product(name=name, price=price)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:product_id>')
def admin_delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))
@app.route('/cart/remove/<int:index>')
def remove_from_cart(index):
    # Get the cart from the session
    cart = session.get('cart', [])
    
    # Remove the item at the specific index
    if 0 <= index < len(cart):
        cart.pop(index)
        session.modified = True # Tell Flask the session has changed
        
    return redirect(url_for('view_cart'))
if __name__ == '__main__':
    app.run(debug=True)