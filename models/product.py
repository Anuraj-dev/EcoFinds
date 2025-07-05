from database import db
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .review import Review
    from .user import User

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1615397349754-cfa2066a298e?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"

# Product categories
PRODUCT_CATEGORIES = [
    "Electronics",
    "Clothing & Fashion", 
    "Home & Garden",
    "Books & Media",
    "Sports & Outdoors",
    "Toys & Games",
    "Health & Beauty",
    "Automotive",
    "Arts & Crafts",
    "Other"
]

class Product(db.Model):
    __tablename__ = 'product'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), default=DEFAULT_IMAGE)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="Other")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Foreign key to User (seller) - required
    seller_id: Mapped[str] = mapped_column(String(36), ForeignKey('user.id'), nullable=False)
    
    # Foreign key to User (buyer) - optional, null until purchased
    buyer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey('user.id'), nullable=True)
    
    # One-to-many relationship with Review
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    
    # Many-to-one relationship with User (seller)
    seller: Mapped["User"] = relationship("User", back_populates="products_selling", foreign_keys=[seller_id])
    
    # Many-to-one relationship with User (buyer) - optional
    buyer: Mapped[Optional["User"]] = relationship("User", back_populates="products_bought", foreign_keys=[buyer_id])

    def __repr__(self) -> str:
        return f'<Product {self.title}>'
    
    def get_average_rating(self):
        """Calculate and return the average rating for this product"""
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)
    
    def is_available(self):
        """Check if the product is still available for purchase"""
        return self.buyer_id is None

