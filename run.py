import os
from app import create_app, db
from models.portfolio import Portfolio
from models.product import Product
from models.order import Order, OrderItem

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'Portfolio': Portfolio, 
        'Product': Product, 
        'Order': Order, 
        'OrderItem': OrderItem
    }

def init_database():
    """Initialize database with tables and sample data."""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Add sample portfolio data if tables are empty
        if Portfolio.query.count() == 0:
            print("Adding sample portfolio data...")
            sample_portfolio = [
                Portfolio(
                    title="Brand Identity Design",
                    description="Complete brand identity for tech startup including logo, color palette, and guidelines",
                    image_url="https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600",
                    category="branding",
                    featured=True
                ),
                Portfolio(
                    title="Modern Website UI",
                    description="Clean and modern website interface design with focus on user experience",
                    image_url="https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=600",
                    category="web",
                    featured=True
                ),
                Portfolio(
                    title="Mobile App Design",
                    description="iOS app interface design with intuitive navigation and beautiful animations",
                    image_url="https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=600",
                    category="mobile",
                    featured=True
                ),
                Portfolio(
                    title="Minimalist Logo Design",
                    description="Clean and memorable logo design for fashion brand with multiple variations",
                    image_url="https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=600",
                    category="logo",
                    featured=True
                ),
                Portfolio(
                    title="Event Poster Design",
                    description="Eye-catching poster design for music festival with vibrant colors and typography",
                    image_url="https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=600",
                    category="print",
                    featured=True
                ),
                Portfolio(
                    title="Product Packaging",
                    description="Elegant packaging design for premium skincare products with sustainable materials",
                    image_url="https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=600",
                    category="packaging",
                    featured=True
                ),
                Portfolio(
                    title="Restaurant Branding",
                    description="Complete branding package for upscale Italian restaurant including menu design",
                    image_url="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600",
                    category="branding"
                ),
                Portfolio(
                    title="E-commerce Website",
                    description="Full e-commerce website design with shopping cart and payment integration",
                    image_url="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600",
                    category="web"
                )
            ]
            
            for item in sample_portfolio:
                db.session.add(item)
        
        # Add sample product data if tables are empty
        if Product.query.count() == 0:
            print("Adding sample product data...")
            sample_products = [
                Product(
                    name="Custom Portrait - Digital",
                    description="High-quality digital portrait created from your photo with attention to detail and personal style. Perfect for social media, prints, or gifts.",
                    price=150.00,
                    image_url="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400",
                    category="portrait",
                    is_featured=True,
                    digital_product=True,
                    delivery_time="3-5 business days"
                ),
                Product(
                    name="Custom Portrait - Oil Painting Style",
                    description="Traditional oil painting style portrait with rich textures and classical techniques. A timeless piece of art for your home.",
                    price=350.00,
                    image_url="https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
                    category="portrait",
                    is_featured=True,
                    digital_product=True,
                    delivery_time="5-7 business days"
                ),
                Product(
                    name="Pet Portrait",
                    description="Capture your beloved pet's personality in a beautiful watercolor style portrait. Perfect memorial or gift for pet lovers.",
                    price=120.00,
                    image_url="https://images.unsplash.com/photo-1537151625747-768eb6cf92b2?w=400",
                    category="portrait",
                    is_featured=True,
                    digital_product=True,
                    delivery_time="3-5 business days"
                ),
                Product(
                    name="Family Portrait Illustration",
                    description="Custom family illustration in a modern, stylized approach. Great for holiday cards or wall art.",
                    price=200.00,
                    image_url="https://images.unsplash.com/photo-1511895426328-dc8714191300?w=400",
                    category="portrait",
                    digital_product=True,
                    delivery_time="5-7 business days"
                ),
                Product(
                    name="Complete Logo Design Package",
                    description="Professional logo design with multiple concepts, revisions, and final files in all formats. Includes brand guidelines.",
                    price=450.00,
                    image_url="https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=400",
                    category="design",
                    digital_product=True,
                    delivery_time="1-2 weeks"
                ),
                Product(
                    name="Business Card Design",
                    description="Professional business card design that makes a lasting impression. Includes print-ready files and multiple variations.",
                    price=80.00,
                    image_url="https://images.unsplash.com/photo-1551836022-deb4988cc6c0?w=400",
                    category="print",
                    digital_product=True,
                    delivery_time="3-5 business days"
                ),
                Product(
                    name="Brand Identity Package",
                    description="Complete brand identity including logo, color palette, typography, and brand guidelines. Perfect for startups and rebrands.",
                    price=800.00,
                    image_url="https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=400",
                    category="design",
                    digital_product=True,
                    delivery_time="2-3 weeks"
                ),
                Product(
                    name="Website Design Mockup",
                    description="Custom website design mockup with multiple pages and responsive layouts. Includes design files and specifications.",
                    price=600.00,
                    image_url="https://images.unsplash.com/photo-1547658719-da2b51169166?w=400",
                    category="design",
                    digital_product=True,
                    delivery_time="1-2 weeks"
                )
            ]
            
            for item in sample_products:
                db.session.add(item)
        
        try:
            db.session.commit()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Run the application
    print("Starting Berta Albas Portfolio application...")
    print("Visit: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)