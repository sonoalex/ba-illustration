from flask import Blueprint, jsonify, request
from models.portfolio import Portfolio
from models.product import Product
from models.order import Order

bp = Blueprint('api', __name__)

@bp.route('/portfolio')
def portfolio_api():
    """API endpoint for portfolio data."""
    category = request.args.get('category', 'all')
    
    if category == 'all':
        works = Portfolio.query.all()
    else:
        works = Portfolio.query.filter_by(category=category).all()
    
    return jsonify({
        'works': [work.to_dict() for work in works],
        'total': len(works)
    })

@bp.route('/portfolio/<int:work_id>')
def portfolio_item_api(work_id):
    """API endpoint for single portfolio item."""
    work = Portfolio.query.get_or_404(work_id)
    return jsonify(work.to_dict())

@bp.route('/portfolio/categories')
def portfolio_categories_api():
    """API endpoint for portfolio categories."""
    categories = Portfolio.get_categories()
    return jsonify({
        'categories': categories,
        'total': len(categories)
    })

@bp.route('/products')
def products_api():
    """API endpoint for products data."""
    category = request.args.get('category', 'all')
    available_only = request.args.get('available', 'true').lower() == 'true'
    
    query = Product.query
    
    if available_only:
        query = query.filter_by(is_available=True)
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    products = query.all()
    
    return jsonify({
        'products': [product.to_dict() for product in products],
        'total': len(products)
    })

@bp.route('/products/<int:product_id>')
def product_api(product_id):
    """API endpoint for single product."""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@bp.route('/products/categories')
def product_categories_api():
    """API endpoint for product categories."""
    categories = Product.get_categories()
    return jsonify({
        'categories': categories,
        'total': len(categories)
    })

@bp.route('/orders/<order_id>')
def order_api(order_id):
    """API endpoint for order data."""
    order = Order.query.filter_by(order_id=order_id).first_or_404()
    return jsonify(order.to_dict())

@bp.route('/stats')
def stats_api():
    """API endpoint for general statistics."""
    portfolio_count = Portfolio.query.count()
    product_count = Product.query.filter_by(is_available=True).count()
    order_count = Order.query.filter_by(payment_status='paid').count()
    
    portfolio_categories = len(Portfolio.get_categories())
    product_categories = len(Product.get_categories())
    
    return jsonify({
        'portfolio': {
            'total_works': portfolio_count,
            'categories': portfolio_categories
        },
        'products': {
            'available_products': product_count,
            'categories': product_categories
        },
        'orders': {
            'total_orders': order_count
        }
    })