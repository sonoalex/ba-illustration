from app import db
from datetime import datetime

class Product(db.Model):
    """Product model for e-commerce functionality."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    stock_quantity = db.Column(db.Integer, default=0)  # 0 = unlimited for digital products
    digital_product = db.Column(db.Boolean, default=True)  # Most design work is digital
    delivery_time = db.Column(db.String(50))  # e.g., "3-5 business days"
    requires_image = db.Column(db.Boolean, default=False)  # For portrait products that need customer image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        """Convert product to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'category': self.category,
            'is_available': self.is_available,
            'is_featured': self.is_featured,
            'digital_product': self.digital_product,
            'delivery_time': self.delivery_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @property
    def formatted_price(self):
        """Return formatted price string."""
        return f"${self.price:.2f}"
    
    @staticmethod
    def get_categories():
        """Get all unique product categories."""
        categories = db.session.query(Product.category).distinct().all()
        return [cat[0] for cat in categories]
    
    @staticmethod
    def get_available():
        """Get all available products."""
        return Product.query.filter_by(is_available=True).all()
    
    @staticmethod
    def get_featured():
        """Get featured products."""
        return Product.query.filter_by(is_available=True, is_featured=True).all()
    
    @staticmethod
    def get_by_category(category):
        """Get products by category."""
        if category.lower() == 'all':
            return Product.query.filter_by(is_available=True).all()
        return Product.query.filter_by(category=category, is_available=True).all()
    
    def check_availability(self, quantity=1):
        """Check if product is available in requested quantity."""
        if not self.is_available:
            return False
        if self.stock_quantity == 0:  # Unlimited stock (digital products)
            return True
        return self.stock_quantity >= quantity