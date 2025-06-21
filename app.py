from flask import Flask, render_template
from database import db
from config import setup_database
from models.product import Product

app = Flask(__name__)

# Configuring DB - using config.py to set up database
app.config['SQLALCHEMY_DATABASE_URI'] = setup_database()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db
db.init_app(app)

@app.route('/')
def root():
    return "I am Root"

#Index route
@app.route("/products")
def allProducts():
    # Query all products
    products = Product.query.all()
    return render_template("index.html", products=products)

#Show route
@app.route("/products/<id>")
def showListing(id):
    product = Product.query.get_or_404(id)
    return render_template("show.html", product=product)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
