from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, current_user
from authlib.integrations.flask_client import OAuth
from database import db
from config import setup_database, Config
from models.product import Product
from models.review import Review
from models.user import User
from auth import login_manager, init_user_auth_methods, login_required
import requests

app = Flask(__name__)

# Configure app from Config class
app.config.from_object(Config)

# Configuring DB - using config.py to set up database
app.config['SQLALCHEMY_DATABASE_URI'] = setup_database()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db and login manager
db.init_app(app)
login_manager.init_app(app)

# Initialize user authentication methods
init_user_auth_methods()

# Setup OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.route('/')
def root():
    return render_template("root.html")

# Authentication routes
@app.route('/login')
def login():
    """Render login page"""
    return render_template("login.html")

@app.route('/auth/google')
def google_auth():
    """Redirect to Google OAuth"""
    try:
        redirect_uri = url_for('google_callback', _external=True)
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        flash(f'Error initiating Google login: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Get the authorization token
        token = google.authorize_access_token()
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            # Fallback: get user info from Google's userinfo endpoint
            resp = google.get('userinfo')
            user_info = resp.json()
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')
        
        if not google_id or not email:
            flash('Failed to get user information from Google', 'error')
            return redirect(url_for('login'))
        
        # Check if user already exists
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Create new user
            user = User(
                google_id=google_id,
                email=email,
                name=name
            )
            db.session.add(user)
            db.session.commit()
            flash(f'Welcome {name}! Your account has been created.', 'success')
        else:
            flash(f'Welcome back, {user.name}!', 'success')
        
        # Log in the user
        login_user(user)
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('allListings'))
        
    except Exception as e:
        flash(f'Authentication failed: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    """Log out the user"""
    try:
        logout_user()
        session.clear()
        flash('You have been logged out successfully.', 'info')
    except Exception as e:
        flash(f'Error during logout: {str(e)}', 'error')
    
    return redirect(url_for('root'))

#Index route
@app.route("/products/")
def allListings():
    # Query all products
    products = Product.query.all()
    return render_template("index.html", products=products)

#New route
@app.route("/products/new")
@login_required
def renderNewForm():
    return render_template("new.html")

#Show route
@app.route("/products/<id>")
def showListing(id):
    product = Product.query.get_or_404(id)
    return render_template("show.html", product=product)

#Create Route
@app.route("/products", methods=["POST"])
@login_required
def createListing():
        form_data = request.form.to_dict()
        form_data['price'] = int(form_data['price'])
        
        # Remove empty image_url to allow default value to be used
        if 'image_url' in form_data and not form_data['image_url'].strip():
            del form_data['image_url']
        
        # Associate product with current user
        form_data['seller_id'] = current_user.id
        
        new_product = Product(**form_data)
        
        # Add to database and commit
        db.session.add(new_product)
        db.session.commit()
        print("Data Saved")
        
        # Redirect to the product listing page
        return redirect(url_for('allListings'))
    
#Edit route
@app.route("/products/<id>/edit")
@login_required
def renderEditForm(id):
    product = Product.query.get_or_404(id)
    
    # Check if current user is the owner of the product
    if product.seller_id != current_user.id:
        flash('You can only edit your own products.', 'error')
        return redirect(url_for('showListing', id=id))
    
    return render_template("edit.html", product=product)

#Update route
@app.route("/products/<id>", methods=["POST"])
@login_required
def updateListing(id):
     product = Product.query.get_or_404(id)

     # Check if current user is the owner of the product
     if product.seller_id != current_user.id:
         flash('You can only edit your own products.', 'error')
         return redirect(url_for('showListing', id=id))

     form_data = request.form.to_dict()
     
     for key, value in form_data.items():
        if key == 'price':
            value = int(value)
        setattr(product, key, value)

        db.session.commit()

     return redirect(url_for("showListing", id=product.id))

#Destroy Route
@app.route("/products/<id>/delete", methods=["POST"])
@login_required
def deleteListing(id):
     product = Product.query.get_or_404(id)
     
     # Check if current user is the owner of the product
     if product.seller_id != current_user.id:
         flash('You can only delete your own products.', 'error')
         return redirect(url_for('showListing', id=id))
     
     db.session.delete(product)
     db.session.commit()
     flash('Product deleted successfully.', 'success')
     return redirect(url_for("allListings"))

#Review create route
@app.route("/products/<id>/reviews", methods=["POST"])
@login_required
def createReview(id):
    # Get form data
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')
    
    # Create new review with current user info
    new_review = Review(
        product_id=id,
        user_id=current_user.id,
        author=current_user.name,
        rating=rating,
        comment=comment
    )
    
    # Save to database
    db.session.add(new_review)
    db.session.commit()
    
    flash('Review added successfully!', 'success')
    return redirect(url_for('showListing', id=id))


#Review delete route
@app.route("/products/<product_id>/reviews/<review_id>/delete", methods=["POST"])
@login_required
def deleteReview(product_id, review_id):
    # Get the review to ensure it exists
    review = Review.query.get_or_404(review_id)
    
    # Check if current user is the author of the review
    if review.user_id != current_user.id:
        flash('You can only delete your own reviews.', 'error')
        return redirect(url_for('showListing', id=product_id))
    
    # Delete the review
    db.session.delete(review)
    db.session.commit()
    
    flash('Review deleted successfully.', 'success')
    # Redirect back to product page
    return redirect(url_for('showListing', id=product_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
