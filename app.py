from flask import Flask, render_template, request, redirect, url_for
from database import db
from config import setup_database
from models.product import Product
from models.review import Review

app = Flask(__name__)

# Configuring DB - using config.py to set up database
app.config['SQLALCHEMY_DATABASE_URI'] = setup_database()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db
db.init_app(app)

@app.route('/')
def root():
    return render_template("root.html")

#Index route
@app.route("/products/")
def allListings():
    # Query all products
    products = Product.query.all()
    return render_template("index.html", products=products)

#New route
@app.route("/products/new")
def renderNewForm():
    return render_template("new.html")

#Show route
@app.route("/products/<id>")
def showListing(id):
    product = Product.query.get_or_404(id)
    return render_template("show.html", product=product)

#Create Route
@app.route("/products", methods=["POST"])
def createListing():
        form_data = request.form.to_dict()
        form_data['price'] = int(form_data['price'])
        
        # Remove empty image_url to allow default value to be used
        if 'image_url' in form_data and not form_data['image_url'].strip():
            del form_data['image_url']
        
        new_product = Product(**form_data)
        
        # Add to database and commit
        db.session.add(new_product)
        db.session.commit()
        print("Data Saved")
        
        # Redirect to the product listing page
        return redirect(url_for('allListings'))
    
#Edit route
@app.route("/products/<id>/edit")
def renderEditForm(id):
    product = Product.query.get_or_404(id)
    return render_template("edit.html", product=product)

#Update route
@app.route("/products/<id>", methods=["POST"])
def updateListing(id):
     product = Product.query.get_or_404(id)

     form_data = request.form.to_dict()
     
     for key, value in form_data.items():
        if key == 'price':
            value = int(value)
        setattr(product, key, value)

        db.session.commit()

     return redirect(url_for("showListing", id=product.id))

#Destroy Route
@app.route("/products/<id>/delete", methods=["POST"])
def deleteListing(id):
     product = Product.query.get_or_404(id)
     db.session.delete(product)
     db.session.commit()
     return redirect(url_for("allListings"))

#Review create route
@app.route("/products/<id>/reviews", methods=["POST"])
def createReview(id):
    # Get form data
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')
    author = request.form.get('author', 'Anonymous')
    
    # Create new review
    new_review = Review(
        product_id=id,
        author=author,
        rating=rating,
        comment=comment
    )
    
    # Save to database
    db.session.add(new_review)
    db.session.commit()
    
    return redirect(url_for('showListing', id=id))


#Review delete route
@app.route("/products/<product_id>/reviews/<review_id>/delete", methods=["POST"])
def deleteReview(product_id, review_id):
    # Get the review to ensure it exists
    review = Review.query.get_or_404(review_id)
    
    # Delete the review
    db.session.delete(review)
    db.session.commit()
    
    # Redirect back to product page
    return redirect(url_for('showListing', id=product_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
