"""
Script to reset the database - drops all tables and recreates them
WARNING: This will delete all existing data!
"""
import sys
import os

# Setup import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from flask import Flask
from database import db
from config import setup_database
from models import Product, Review, User, CartItem, Wishlist  

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = setup_database()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def reset_database():
    """Drop all tables and recreate them"""
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("Database reset complete!")
        print("Tables created: User, Product, Review, CartItem, Wishlist")

if __name__ == "__main__":
    reset_database()
