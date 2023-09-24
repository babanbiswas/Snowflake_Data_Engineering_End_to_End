from flask import Flask, render_template, request, redirect, url_for, session, jsonify

import config
from flask_session import Session
import snowflake.connector as sno

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key for session management
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def fetch_product_data():
    try:
        # Connecting to Snowflake
        conn = sno.connect(**config.snowflake_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ELT_DB.ELT_SCHEMA.PRODUCT")
        product_data = cursor.fetchall()
        return product_data
    except Exception as e:
        print("Error", str(e))
        return []
    finally:
        cursor.close()
        conn.close()


# Sample product data (you can replace this with your own database)
# products = [
#    {'id': '111', 'name': '1KG APPLE', 'price': 2.00},
#    {'id': '112', 'name': '5KG BASMATI RICE', 'price': 6.00},
# ]

# products = [
#    {'id': 1, 'name': 'Product 1', 'price': 10.00},
#    {'id': 2, 'name': 'Product 2', 'price': 20.00},
#    {'id': 3, 'name': 'Product 3', 'price': 30.00},
# ]


# Fetch Product data from Snowflake
product_data = fetch_product_data()

# Create a list of products fetched from Snowflake
products = [{'id': row[0], 'name': row[1], 'price': row[2]} for row in product_data]


# print(products)

# Webpage displaying the products
@app.route('/')
def index():
    return render_template('index.html', products=products)


# Api End Point displaying the products in json format
@app.route('/product_api')
def show_products():
    return jsonify(products)


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        if 'cart' not in session:
            session['cart'] = []
        session['cart'].append(product)
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    return render_template('cart.html', cart=session.get('cart', []))


@app.route('/checkout')
def checkout():
    cart = session.get('cart', [])
    total_price = sum(product['price'] for product in cart)
    return render_template('checkout.html', cart=cart, total_price=total_price)


@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('index'))


@app.route('/admin')
def admin():
    return render_template("admin.html")


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        id = int(request.form['id'])
        name = request.form['name']
        price = float(request.form['price'])

        try:
            conn = sno.Connect(**config.snowflake_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ELT_DB.ELT_SCHEMA.PRODUCT(ID, NAME, PRICE) VALUES (%s,%s,%s)",
                           (id, name, price))
            conn.commit()

            return redirect(url_for('admin'))

        except Exception as e:
            print("Error:", e)
        finally:
            cursor.close()
            conn.close()
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)
