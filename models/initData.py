import sys
import os

# Setup import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import setup_database
from database import db
from flask import Flask

# Initialize Flask app with database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = setup_database()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Sample product data
products = [
    {
        'title': 'AeroSport Sneakers',
        'description': 'Breathable athletic sneakers ideal for running and everyday wear.',
        'image_url': 'https://picsum.photos/seed/1/600/400',
        'price': 2999,
        'category': 'Sports & Outdoors'
    },
    {
        'title': 'Harmony Wireless Earbuds',
        'description': 'Compact wireless earbuds with noise-cancellation feature.',
        'image_url': 'https://picsum.photos/seed/2/600/400',
        'price': 4999,
        'category': 'Electronics'
    },
    {
        'title': 'Zen Ceramic Mug',
        'description': 'Minimalist ceramic mug perfect for coffee and tea.',
        'image_url': 'https://picsum.photos/seed/3/600/400',
        'price': 799,
        'category': 'Home & Garden'
    },
    {
        'title': 'Urban Backpack 20L',
        'description': 'Durable water-resistant backpack suitable for daily commute.',
        'image_url': 'https://picsum.photos/seed/4/600/400',
        'price': 3499,
        'category': 'Sports & Outdoors'
    },
    {
        'title': 'Classic Leather Belt',
        'description': 'Premium genuine leather belt with antique buckle.',
        'image_url': 'https://picsum.photos/seed/5/600/400',
        'price': 1999,
        'category': 'Clothing & Fashion'
    },
    {
        'title': 'Eco Bamboo Toothbrush',
        'description': 'Biodegradable toothbrush made from sustainable bamboo.',
        'image_url': 'https://picsum.photos/seed/6/600/400',
        'price': 299,
        'category': 'Health & Beauty'
    },
    {
        'title': 'FitPro Yoga Mat',
        'description': 'Non-slip cushioned mat for yoga and pilates routines.',
        'image_url': 'https://picsum.photos/seed/7/600/400',
        'price': 1499,
        'category': 'Sports & Outdoors'
    },
    {
        'title': 'ProKitchen Chef Knife',
        'description': 'High-carbon stainless steel chef knife for precision cutting.',
        'image_url': 'https://picsum.photos/seed/8/600/400',
        'price': 2599,
        'category': 'Home & Garden'
    },
    {
        'title': 'AquaSports Water Bottle',
        'description': 'Insulated stainless steel bottle keeps drinks cold for 24h.',
        'image_url': 'https://picsum.photos/seed/9/600/400',
        'price': 999,
        'category': 'Sports & Outdoors'
    },
    {
        'title': 'TravelTech Power Bank',
        'description': 'Slim 10,000 mAh power bank with dual USB‑C ports.',
        'image_url': 'https://picsum.photos/seed/10/600/400',
        'price': 2199,
        'category': 'Electronics'
    },
    {
        'title': 'Luxe Bath Towel',
        'description': 'Soft, large turkish cotton towel, quick-dry.',
        'image_url': 'https://picsum.photos/seed/11/600/400',
        'price': 1299,
        'category': 'Home & Garden'
    },
    {
        'title': 'SoundMax Bluetooth Speaker',
        'description': 'Portable speaker with deep bass and 12h playtime.',
        'image_url': 'https://picsum.photos/seed/12/600/400',
        'price': 3499,
        'category': 'Electronics'
    },
    {
        'title': 'SmartHome LED Bulb',
        'description': 'Energy-saving smart bulb with app control.',
        'image_url': 'https://picsum.photos/seed/13/600/400',
        'price': 599,
        'category': 'Home & Garden'
    },
    {
        'title': 'Outdoor Ring Lantern',
        'description': 'Rechargeable solar lantern for camping and backyard.',
        'image_url': 'https://picsum.photos/seed/14/600/400',
        'price': 1599,
        'category': 'Sports & Outdoors'
    },
    {
        'title': 'DeskMate LED Lamp',
        'description': 'Adjustable LED desk lamp with USB charging port.',
        'image_url': 'https://picsum.photos/seed/15/600/400',
        'price': 1899,
        'category': 'Home & Garden'
    },
    {
        'title': 'GentleSkincare Cream',
        'description': 'Hydrating daily moisturizing cream for all skin types.',
        'image_url': 'https://picsum.photos/seed/16/600/400',
        'price': 2199,
        'category': 'Health & Beauty'
    },
    {
        'title': 'Precision Screwdriver Kit',
        'description': 'Compact multi-head screwdriver set for electronics.',
        'image_url': 'https://picsum.photos/seed/17/600/400',
        'price': 899,
        'category': 'Automotive'
    },
    {
        'title': 'Retro Vinyl Record',
        'description': 'Classic vinyl record for vintage music lovers.',
        'image_url': 'https://picsum.photos/seed/18/600/400',
        'price': 1599,
        'category': 'Books & Media'
    },
    {
        'title': 'Kids Fun Puzzle',
        'description': 'Colorful 500-piece jigsaw puzzle for children.',
        'image_url': 'https://picsum.photos/seed/19/600/400',
        'price': 699,
        'category': 'Toys & Games'
    },
    {
        'title': 'PetComfort Bed',
        'description': 'Soft cushion bed for small to medium pets.',
        'image_url': 'https://picsum.photos/seed/20/600/400',
        'price': 2499,
        'category': 'Other'
    }
]

def insert_products():
    with app.app_context():
        # Import all models to resolve relationships
        from models.product import Product
        from models.user import User
        from models.cart import CartItem, Wishlist
        from models.review import Review
        
        # Create tables
        db.create_all()
        
        # Skip if products already exist
        if Product.query.count() > 0:
            print(f"Products already exist in database. Skipping insertion.")
            return
        
        try:
            # Create a default seller if no users exist
            default_seller = User.query.filter_by(email="seller@ecofinds.com").first()
            if not default_seller:
                default_seller = User(
                    email="seller@ecofinds.com",
                    name="EcoFinds Store",
                    google_id="default_store_001"
                )
                db.session.add(default_seller)
                db.session.commit()
                print("Created default seller user.")
            
            # Add seller_id to all products
            for product_data in products:
                product_data['seller_id'] = default_seller.id
            
            # Bulk add all products
            for product_data in products:
                db.session.add(Product(**product_data))
            
            db.session.commit()
            print(f"Added {len(products)} products to the database.")
        except Exception as e:
            db.session.rollback()
            print(f"Error inserting products: {e}")

if __name__ == "__main__":
    insert_products()
