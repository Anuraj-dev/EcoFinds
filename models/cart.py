from database import db
import uuid
from sqlalchemy import String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product
    from .user import User

class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # For anonymous users, we'll use session_id; for logged users, user_id
    session_id: Mapped[str] = mapped_column(String(100), nullable=True)  # For anonymous users
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey('user.id'), nullable=True)  # For logged users
    
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey('product.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # Add quantity field
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product")
    user: Mapped["User"] = relationship("User", back_populates="cart_items")
    
    # Ensure unique user-product combination
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_cart'),
        db.UniqueConstraint('session_id', 'product_id', name='unique_session_product_cart'),
    )

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Only for logged users
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey('user.id'), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey('product.id'), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product")
    user: Mapped["User"] = relationship("User", back_populates="wishlist_items")
    
    # Ensure unique user-product combination
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_wishlist'),)