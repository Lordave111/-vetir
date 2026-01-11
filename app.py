import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "stylehub_secret_key_2026"

# --- DATABASE CONFIG (MySQL with PyMySQL) ---
# Format: mysql+pymysql://username:password@hostname:port/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://avnadmin:AVNS_kGEUKEqpS9e5vSecN8T@mysql-2f4aa36-nwahiridaviduche-cede.c.aivencloud.com:11573/defaultdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- CLOUDINARY CONFIG ---
cloudinary.config(
    cloud_name = "dvveagfz7",
    api_key = "773538431459482",
    api_secret = "1AO7K4qc0P4P2sVtVE22fJtIAUA",
    secure = True
)

# --- DATABASE MODELS ---
class Seller(db.Model):
    __tablename__ = 'sellers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    whatsapp = db.Column(db.String(20), nullable=False)
    # Relationship to products
    products = db.relationship('Product', backref='seller', lazy=True, cascade="all, delete-orphan")

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    img_url = db.Column(db.String(255), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)

# Initialize Database
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def market():
    """Main store view for buyers"""
    cat = request.args.get('cat')
    if cat and cat != "All":
        items = Product.query.filter_by(category=cat).all()
    else:
        items = Product.query.all()
    return render_template('market.html', items=items, active_cat=cat)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Seller Login and Automatic Registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        whatsapp = request.form.get('whatsapp')

        seller = Seller.query.filter_by(email=email).first()

        if seller:
            # Check Password
            if check_password_hash(seller.password, password):
                session['seller_id'] = seller.id
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid Password")
                return redirect(url_for('login'))
        else:
            # Create New Seller Account
            hashed_pw = generate_password_hash(password)
            new_seller = Seller(email=email, password=hashed_pw, whatsapp=whatsapp)
            db.session.add(new_seller)
            db.session.commit()
            session['seller_id'] = new_seller.id
            return redirect(url_for('dashboard'))
            
    return render_template('auth.html')

@app.route('/dashboard')
def dashboard():
    """Private area for sellers to manage clothes"""
    if 'seller_id' not in session:
        return redirect(url_for('login'))
    
    my_items = Product.query.filter_by(seller_id=session['seller_id']).all()
    return render_template('dashboard.html', seller_items=my_items)

@app.route('/upload', methods=['POST'])
def upload():
    if 'seller_id' not in session:
        return redirect(url_for('login'))

    image_file = request.files.get('image')
    if image_file:
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(image_file)
        
        new_product = Product(
            name=request.form.get('name'),
            price=request.form.get('price'),
            category=request.form.get('category'),
            img_url=upload_result['secure_url'],
            seller_id=session['seller_id']
        )
        db.session.add(new_product)
        db.session.commit()
    
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'seller_id' not in session:
        return redirect(url_for('login'))
        
    product = Product.query.get(product_id)
    # Security: Ensure only the owner can delete
    if product and product.seller_id == session['seller_id']:
        db.session.delete(product)
        db.session.commit()
        
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('market'))

if __name__ == '__main__':
    app.run(debug=True)
