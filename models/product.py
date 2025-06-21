from database import db
import uuid

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Product {self.title}>'
