from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- MOCK DATABASE (Demo Data) ---
# This simulates your SQL database. 
products = [
    {
        "id": 1, 
        "name": "Bespoke Emerald Jacket", 
        "price": "45,000", 
        "category": "Men", 
        "seller": "Elite_Store", 
        "phone": "2347037065177",
        "img": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500"
    },
    {
        "id": 2, 
        "name": "Silk Evening Gown", 
        "price": "62,000", 
        "category": "Women", 
        "seller": "GlamHouse", 
        "phone": "2347037065177",
        "img": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=500"
    },
    {
        "id": 3, 
        "name": "Urban Kids Set", 
        "price": "15,000", 
        "category": "Children", 
        "seller": "TinyTrends", 
        "phone": "2347037065177",
        "img": "https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?w=500"
    }
]

# --- ROUTES ---

@app.route('/')
def market():
    # Get the category from the URL (e.g., /?cat=Men)
    category = request.args.get('cat')
    
    if category and category != "All":
        # Filter products based on category
        filtered_products = [p for p in products if p['category'] == category]
    else:
        filtered_products = products
        
    return render_template('market.html', items=filtered_products, active_cat=category)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Logic to check user/seller would go here
        return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/dashboard')
def dashboard():
    # Show only the items belonging to the logged-in seller
    return render_template('dashboard.html', seller_items=products)

@app.route('/upload', methods=['POST'])
def upload():
    # Capture form data
    new_item = {
        "id": len(products) + 1,
        "name": request.form.get('name'),
        "price": request.form.get('price'),
        "category": request.form.get('category'),
        "seller": "name",
        "phone": "2347037065177",
        "img" = "request.files['image']" # Placeholder since we aren't saving real files yet
    }
    products.append(new_item)
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    global products
    products = [p for p in products if p['id'] != item_id]
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
