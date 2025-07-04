from database import db
import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product

class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    google_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # One-to-many relationship with Product
    products_selling: Mapped[list["Product"]] = relationship(
        "Product", 
        back_populates="seller", 
        foreign_keys="Product.seller_id"
    )
    
    # One-to-many relationship with Product
    products_bought: Mapped[list["Product"]] = relationship(
        "Product", 
        back_populates="buyer", 
        foreign_keys="Product.buyer_id"
    )

    def __repr__(self) -> str:
        return f'<User {self.name} ({self.email})>'