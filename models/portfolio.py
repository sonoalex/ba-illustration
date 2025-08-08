from app import db
from datetime import datetime

class Portfolio(db.Model):
    """Portfolio item model for showcasing work."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    client = db.Column(db.String(100))
    project_url = db.Column(db.String(255))
    technologies = db.Column(db.String(255))  # Comma-separated technologies used
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Portfolio {self.title}>'
    
    def to_dict(self):
        """Convert portfolio item to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'category': self.category,
            'client': self.client,
            'project_url': self.project_url,
            'technologies': self.technologies.split(',') if self.technologies else [],
            'featured': self.featured,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def get_categories():
        """Get all unique categories."""
        categories = db.session.query(Portfolio.category).distinct().all()
        return [cat[0] for cat in categories]
    
    @staticmethod
    def get_featured():
        """Get featured portfolio items."""
        return Portfolio.query.filter_by(featured=True).all()
    
    @staticmethod
    def get_by_category(category):
        """Get portfolio items by category."""
        if category.lower() == 'all':
            return Portfolio.query.all()
        return Portfolio.query.filter_by(category=category).all()