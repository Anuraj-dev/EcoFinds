from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_user, logout_user, current_user
from authlib.integrations.flask_client import OAuth
from database import db
from config import setup_database, Config
from models import Product, PRODUCT_CATEGORIES, Review, User, CartItem, Wishlist
from auth import login_manager, init_user_auth_methods, login_required
import uuid

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

# Ensure tables exist (safe to call repeatedly). On Vercel serverless, this
# runs once per cold start to guarantee schema is present.
@app.before_request
def _ensure_tables():
    if not getattr(app, "_tables_created", False):
        try:
            with app.app_context():
                db.create_all()
            app._tables_created = True
        except Exception as e:
            # Non-fatal; queries will fail if DB is unreachable/misconfigured
            print(f"[startup] DB init skipped/failed: {e}")

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

# Helper functions for cart management
def get_session_id():
    """Get or create session ID for anonymous users"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_cart_items():
    """Get cart items for current user (logged in or anonymous) - only available products"""
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    else:
        session_id = get_session_id()
        cart_items = CartItem.query.filter_by(session_id=session_id).all()
    
    # Filter out sold items and remove them from cart
    available_items = []
    for item in cart_items:
        if item.product.is_available():
            available_items.append(item)
        else:
            # Remove sold items from cart automatically
            db.session.delete(item)
    
    db.session.commit()
    return available_items

def get_cart_count():
    """Get total number of items in cart (only available products)"""
    return len(get_cart_items())

def remove_product_from_all_carts(product_id):
    """Remove a product from all users' carts when it's sold"""
    CartItem.query.filter_by(product_id=product_id).delete()
    db.session.commit()

# Add this context processor to make cart count available in all templates
@app.context_processor
def inject_cart_count():
    return dict(cart_count=get_cart_count())

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
        
        # Transfer anonymous cart to user account after login
        if 'session_id' in session:
            anonymous_cart_items = CartItem.query.filter_by(session_id=session['session_id']).all()
            for item in anonymous_cart_items:
                # Check if product is still available
                if item.product.is_available():
                    # Check if user already has this product in cart
                    existing_item = CartItem.query.filter_by(
                        user_id=user.id, 
                        product_id=item.product_id
                    ).first()
                    
                    if not existing_item:
                        item.user_id = user.id
                        item.session_id = None
                    else:
                        db.session.delete(item)
                else:
                    # Remove sold items
                    db.session.delete(item)
            
            db.session.commit()
        
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
    # Get filter parameters
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    status_filter = request.args.get('status', '')
    
    # Start with base query
    query = Product.query
    
    # Apply search filter
    if search_query:
        query = query.filter(
            Product.title.ilike(f'%{search_query}%') | 
            Product.description.ilike(f'%{search_query}%')
        )
    
    # Apply category filter
    if category_filter and category_filter in PRODUCT_CATEGORIES:
        query = query.filter(Product.category == category_filter)
    
    # Apply price range filter
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Apply status filter
    if status_filter == 'available':
        query = query.filter(Product.buyer_id.is_(None))
    elif status_filter == 'sold':
        query = query.filter(Product.buyer_id.isnot(None))
    
    # Execute query and get results
    products = query.order_by(Product.created_at.desc()).all()
    
    return render_template("index.html", 
                         products=products, 
                         categories=PRODUCT_CATEGORIES,
                         search_query=search_query,
                         category_filter=category_filter,
                         min_price=min_price,
                         max_price=max_price,
                         status_filter=status_filter)

# Search route
@app.route("/search")
def search():
    return redirect(url_for('allListings', **request.args))

# Category route
@app.route("/products/category/<category_name>")
def categoryListings(category_name):
    if category_name not in PRODUCT_CATEGORIES:
        flash(f'Category "{category_name}" not found.', 'error')
        return redirect(url_for('allListings'))
    
    return redirect(url_for('allListings', category=category_name))

#New route
@app.route("/products/new")
@login_required
def renderNewForm():
    return render_template("new.html", categories=PRODUCT_CATEGORIES)

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
    
    return render_template("edit.html", product=product, categories=PRODUCT_CATEGORIES)

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
     
     # Remove from all carts and wishlists before deleting
     remove_product_from_all_carts(product.id)
     Wishlist.query.filter_by(product_id=product.id).delete()
     
     db.session.delete(product)
     db.session.commit()
     flash('Product deleted successfully.', 'success')
     return redirect(url_for("allListings"))

# Cart Routes
@app.route('/cart')
def view_cart():
    """View cart page"""
    cart_items = get_cart_items()
    total_price = sum(item.product.price for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/cart/add/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Check if product is available
    if not product.is_available():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'This product is no longer available.'}), 400
        flash('This product is no longer available.', 'error')
        return redirect(url_for('showListing', id=product_id))
    
    # Check if user is trying to add their own product
    if current_user.is_authenticated and product.seller_id == current_user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'You cannot add your own product to cart.'}), 400
        flash('You cannot add your own product to cart.', 'error')
        return redirect(url_for('showListing', id=product_id))
    
    try:
        if current_user.is_authenticated:
            # For logged-in users
            existing_item = CartItem.query.filter_by(
                user_id=current_user.id, 
                product_id=product_id
            ).first()
            
            if existing_item:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'Product is already in your cart.'}), 400
                flash('Product is already in your cart.', 'info')
            else:
                cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
                db.session.add(cart_item)
                db.session.commit()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True, 'message': 'Product added to cart!'})
                flash('Product added to cart!', 'success')
        else:
            # For anonymous users
            session_id = get_session_id()
            existing_item = CartItem.query.filter_by(
                session_id=session_id, 
                product_id=product_id
            ).first()
            
            if existing_item:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'Product is already in your cart.'}), 400
                flash('Product is already in your cart.', 'info')
            else:
                cart_item = CartItem(session_id=session_id, product_id=product_id, quantity=1)
                db.session.add(cart_item)
                db.session.commit()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True, 'message': 'Product added to cart!'})
                flash('Product added to cart!', 'success')
    
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Error adding product to cart.'}), 500
        flash('Error adding product to cart.', 'error')
    
    return redirect(url_for('showListing', id=product_id))

@app.route('/cart/remove/<item_id>', methods=['POST'])
def remove_from_cart(item_id):
    """Remove item from cart"""
    try:
        if current_user.is_authenticated:
            cart_item = CartItem.query.filter_by(
                id=item_id, 
                user_id=current_user.id
            ).first_or_404()
        else:
            session_id = get_session_id()
            cart_item = CartItem.query.filter_by(
                id=item_id, 
                session_id=session_id
            ).first_or_404()
        
        db.session.delete(cart_item)
        db.session.commit()
        
        # Get updated count
        count = get_cart_count()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Item removed from cart', 'count': count})
        
        flash('Item removed from cart.', 'info')
        return redirect(url_for('view_cart'))
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 500
        flash('Error removing item from cart.', 'error')
        return redirect(url_for('view_cart'))

@app.route('/checkout')
@login_required
def checkout():
    """Checkout page - requires login"""
    cart_items = get_cart_items()  # This automatically removes sold items
    
    if not cart_items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('view_cart'))
    
    total_price = sum(item.product.price for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)

@app.route('/buy-now/<product_id>')
@login_required
def buy_now(product_id):
    """Direct checkout for a single product - requires login"""
    product = Product.query.get_or_404(product_id)
    
    # Check if product is available
    if not product.is_available():
        flash('This product is no longer available.', 'error')
        return redirect(url_for('showListing', id=product_id))
    
    # Check if user is trying to buy their own product
    if product.seller_id == current_user.id:
        flash('You cannot buy your own product.', 'error')
        return redirect(url_for('showListing', id=product_id))
    
    return render_template('buy_now.html', product=product)

@app.route('/buy-now/process/<product_id>', methods=['POST'])
@login_required
def process_buy_now(product_id):
    """Process direct purchase of a single product"""
    product = Product.query.get_or_404(product_id)
    
    # Double-check if product is still available
    if not product.is_available():
        flash('This product is no longer available.', 'error')
        return redirect(url_for('showListing', id=product_id))
    
    # Check if user is trying to buy their own product
    if product.seller_id == current_user.id:
        flash('You cannot buy your own product.', 'error')
        return redirect(url_for('showListing', id=product_id))
    
    try:
        # Mark as sold
        product.buyer_id = current_user.id
        
        # Remove this product from ALL carts and wishlists
        remove_product_from_all_carts(product.id)
        Wishlist.query.filter_by(product_id=product.id).delete()
        
        db.session.commit()
        
        flash(f'Successfully purchased "{product.title}"!', 'success')
        return redirect(url_for('my_orders'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while processing your purchase. Please try again.', 'error')
        return redirect(url_for('showListing', id=product_id))

@app.route('/checkout/process', methods=['POST'])
@login_required
def process_checkout():
    """Process the checkout - mark products as sold"""
    cart_items = get_cart_items()
    
    if not cart_items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('view_cart'))
    
    successful_purchases = []
    failed_purchases = []
    
    for item in cart_items:
        # Double-check if product is still available
        if item.product.is_available():
            # Mark as sold
            item.product.buyer_id = current_user.id
            successful_purchases.append(item.product.title)
            
            # Remove this product from ALL carts (including current user's)
            remove_product_from_all_carts(item.product.id)
        else:
            failed_purchases.append(item.product.title)
    
    db.session.commit()
    
    # Show results
    if successful_purchases:
        flash(f'Successfully purchased: {", ".join(successful_purchases)}', 'success')
    
    if failed_purchases:
        flash(f'These items were no longer available: {", ".join(failed_purchases)}', 'warning')
    
    return redirect(url_for('allListings'))

# Wishlist Routes (requires login)
@app.route('/wishlist')
@login_required
def view_wishlist():
    """View wishlist page - shows all items, available and sold"""
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist.html', wishlist_items=wishlist_items)

@app.route('/wishlist/add/<product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    """Add product to wishlist"""
    product = Product.query.get_or_404(product_id)
    
    # Check if product is available
    if not product.is_available():
        flash('This product is no longer available and cannot be added to wishlist.', 'error')
        return redirect(url_for('showListing', id=product_id))
    
    # Check if user is trying to add their own product
    if product.seller_id == current_user.id:
        flash('You cannot add your own product to wishlist.', 'error')
        return redirect(url_for('showListing', id=product_id))
    
    # Check if already in wishlist
    existing_item = Wishlist.query.filter_by(
        user_id=current_user.id, 
        product_id=product_id
    ).first()
    
    if existing_item:
        flash('Product is already in your wishlist.', 'info')
    else:
        wishlist_item = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
        flash('Product added to wishlist!', 'success')
    
    return redirect(url_for('showListing', id=product_id))

@app.route('/wishlist/remove/<product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    """Remove product from wishlist"""
    wishlist_item = Wishlist.query.filter_by(
        user_id=current_user.id, 
        product_id=product_id
    ).first_or_404()
    
    db.session.delete(wishlist_item)
    db.session.commit()
    flash('Product removed from wishlist.', 'info')
    return redirect(url_for('view_wishlist'))

@app.route('/wishlist/add-to-cart/<product_id>', methods=['POST'])
@login_required
def add_wishlist_to_cart(product_id):
    """Add wishlist item to cart - with availability check"""
    product = Product.query.get_or_404(product_id)
    
    # Check if product is still available
    if not product.is_available():
        # Remove from wishlist since it's sold
        wishlist_item = Wishlist.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id
        ).first()
        if wishlist_item:
            db.session.delete(wishlist_item)
            db.session.commit()
        
        flash('This product is no longer available and has been removed from your wishlist.', 'error')
        return redirect(url_for('view_wishlist'))
    
    # Check if user is trying to add their own product to cart
    if product.seller_id == current_user.id:
        flash('You cannot add your own product to cart.', 'error')
        return redirect(url_for('view_wishlist'))
    
    # Check if already in cart
    existing_cart_item = CartItem.query.filter_by(
        user_id=current_user.id, 
        product_id=product_id
    ).first()
    
    if existing_cart_item:
        flash('Product is already in your cart.', 'info')
    else:
        # Add to cart
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
        db.session.commit()
        flash('Product added to cart from wishlist!', 'success')
    
    return redirect(url_for('view_wishlist'))

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

# My Orders and Listings Routes
@app.route('/my-orders')
@login_required
def my_orders():
    """View user's purchase history"""
    orders = Product.query.filter_by(buyer_id=current_user.id).order_by(Product.id.desc()).all()
    return render_template('my_orders.html', orders=orders)

@app.route('/my-listings')
@login_required
def my_listings():
    """View user's product listings"""
    listings = Product.query.filter_by(seller_id=current_user.id).order_by(Product.id.desc()).all()
    return render_template('my_listings.html', listings=listings)

# API Routes for AJAX interactions
@app.route('/api/cart/count', methods=['GET'])
def get_cart_count_api():
    """API endpoint to get current cart count"""
    try:
        count = get_cart_count()
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
