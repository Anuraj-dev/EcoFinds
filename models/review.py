from database import db
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .product import Product
    from .user import User

class Review(db.Model):
    __tablename__ = 'review'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey('product.id'), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey('user.id'), nullable=True)  # For authenticated users
    author: Mapped[str] = mapped_column(String(100), nullable=False)  # Display name
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # Rating from 1-5
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship back to Product
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
    
    # Relationship to User (review author)
    user: Mapped[Optional["User"]] = relationship("User", back_populates="reviews")
