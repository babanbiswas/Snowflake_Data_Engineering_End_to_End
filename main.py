from flask import Flask, render_template, request, redirect, url_for, session, jsonify

import config
from flask_session import Session
import snowflake.connector as sno

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key for session management
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


class SnowflakeDatabase:
    def __init__(self, config):
        self.config = config

    def connect(self):
        return sno.connect(**config.snowflake_config)

    def fetch_product_data(self):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM ELT_DB.ELT_SCHEMA.PRODUCT")
                product_data = cursor.fetchall()
                return product_data
        except Exception as e:
            print("Error: ", str(e))
            return []
        finally:
            cursor.close()


class ShoppingCart:
    def __init__(self):
        self.cart = []

    def add_to_cart(self, product):
        self.cart.append(product)

    def clear_cart(self):
        self.cart = []

    def calculate_total_price(self):
        return sum(product['price'] for product in self.cart)


db = SnowflakeDatabase(config.snowflake_config)
shopping_cart = ShoppingCart()


@app.route("/")
def index():
    product_data = db.fetch_product_data()
    products = [{'id': row[0], 'name': row[1], 'price': row[2]} for row in product_data]
    return render_template("index.html", products=products)

@app.route("/product_api")
def show_products():
    product_data = db.fetch_product_data()
    products = [{'id': row[0], 'name': row[1], 'price': row[2]} for row in product_data]
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True)
