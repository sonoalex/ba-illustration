from app import db
from datetime import datetime
import uuid

class Order(db.Model):
    """Order model for tracking customer purchases."""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20))
    
    # Address information (for physical products)
    shipping_address = db.Column(db.Text)
    billing_address = db.Column(db.Text)
    
    # Order totals
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    shipping_cost = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Order status
    status = db.Column(db.String(20), default='pending')  # pending, paid, processing, completed, cancelled
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    
    # Payment information
    stripe_payment_intent_id = db.Column(db.String(255))
    payment_method = db.Column(db.String(50))  # card, paypal, etc.
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_id}>'
    
    def to_dict(self):
        """Convert order to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'shipping_cost': self.shipping_cost,
            'total_amount': self.total_amount,
            'status': self.status,
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }
    
    def calculate_totals(self):
        """Calculate order totals from items."""
        self.subtotal = sum(item.subtotal for item in self.items)
        # Add tax calculation if needed
        self.tax_amount = 0.0  # Implement tax calculation logic
        # Add shipping calculation if needed
        self.shipping_cost = 0.0  # Free shipping for digital products
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost
    
    def mark_as_paid(self):
        """Mark order as paid and update timestamp."""
        self.payment_status = 'paid'
        self.status = 'processing'
        self.paid_at = datetime.utcnow()
    
    def mark_as_completed(self):
        """Mark order as completed."""
        self.status = 'completed'
        self.delivered_at = datetime.utcnow()

class OrderItem(db.Model):
    """Order item model for individual products in an order."""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # Item details (stored to preserve data even if product changes)
    product_name = db.Column(db.String(100), nullable=False)
    product_description = db.Column(db.Text)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # Calculated fields
    @property
    def subtotal(self):
        return self.unit_price * self.quantity
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x {self.quantity}>'
    
    def to_dict(self):
        """Convert order item to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_description': self.product_description,
            'unit_price': self.unit_price,
            'quantity': self.quantity,
            'subtotal': self.subtotal
        }