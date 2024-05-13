from flask import Flask, render_template, request
import mysql.connector
import requests

app = Flask(__name__)

# Function to fetch inflation rate for the day in Zimbabwe
def fetch_inflation_rate():
    try:
        # Make a request to an API or website that provides the inflation rate data
        response = requests.get('https://your-inflation-api.com/zimbabwe')
        data = response.json()
        inflation_rate = data['inflation_rate']  # Assuming the API returns inflation rate in percentage
        return inflation_rate
    except Exception as e:
        print("Error fetching inflation rate:", e)
        return None

# Configure MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="your_mysql_username",
    password="your_mysql_password",
    database="your_database_name"
)

# Create table if not exists
def create_table():
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            original_price DECIMAL(10, 2) NOT NULL,
            adjusted_price DECIMAL(10, 2) NOT NULL,
            description TEXT
        )
    """)
    cursor.close()

# Initialize the database
create_table()

# Route for the home page
@app.route('/')
def index():
    # Fetch the inflation rate for the day
    inflation_rate = fetch_inflation_rate()

    # Fetch product data from the database
    cursor = db.cursor()
    cursor.execute("SELECT name, original_price, description FROM products")
    products = cursor.fetchall()
    cursor.close()

    # Adjust prices based on inflation rate
    if inflation_rate is not None:
        for product in products:
            original_price = product[1]
            adjusted_price = original_price * (1 + (inflation_rate / 100))
            product['adjusted_price'] = adjusted_price

    return render_template('index.html', products=products)

# Route for adding a new product
@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    original_price = request.form['original_price']
    description = request.form['description']

    cursor = db.cursor()
    cursor.execute("INSERT INTO products (name, original_price, description) VALUES (%s, %s, %s)", (name, original_price, description))
    db.commit()
    cursor.close()

    return 'Product added successfully!'

if __name__ == '__main__':
    app.run(debug=True)
