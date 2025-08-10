from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.user import User, db
from models.order import Order, OrderItem
from models.product import Product
from functools import wraps
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@admin_required
def dashboard():
    # Basic analytics
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_products = Product.query.count()
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Revenue stats (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(
        Order.created_at >= thirty_days_ago,
        Order.payment_status == 'paid'
    ).scalar() or 0
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_orders=total_orders,
                         total_products=total_products,
                         recent_revenue=recent_revenue,
                         recent_orders=recent_orders)

@bp.route('/orders')
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/orders.html', orders=orders)

@bp.route('/orders/<int:order_id>')
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    print(order)
    new_status = request.form.get('status')
    print(new_status)
    
    if new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        print("Updating status")
        order.status = new_status
        db.session.commit()
        flash(f'Estado del pedido actualizado a: {new_status}', 'success')
    else:
        print("Invalid status")
        flash('Estado inválido', 'error')
    
    return redirect(url_for('admin.order_detail', order_id=order_id))

@bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users)

@bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', user=user)

@bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta', 'error')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'activada' if user.is_active else 'desactivada'
        flash(f'Cuenta {status} correctamente', 'success')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))

@bp.route('/analytics')
@admin_required
def analytics():
    # This will be expanded later with more detailed analytics
    return render_template('admin/analytics.html')

@bp.route('/products')
@admin_required
def products():
    """Manage products."""
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/products.html', products=products)

@bp.route('/products/new', methods=['GET', 'POST'])
@admin_required
def new_product():
    """Create new product."""
    if request.method == 'POST':
        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=float(request.form.get('price')),
            image_url=request.form.get('image_url'),
            category=request.form.get('category'),
            is_available=bool(request.form.get('is_available')),
            is_featured=bool(request.form.get('is_featured')),
            requires_image=bool(request.form.get('requires_image')),
            digital_product=bool(request.form.get('digital_product')),
            delivery_time=request.form.get('delivery_time'),
            stock_quantity=int(request.form.get('stock_quantity', 0))
        )
        db.session.add(product)
        db.session.commit()
        flash('Producto creado exitosamente.', 'success')
        return redirect(url_for('admin.products'))
    
    categories = Product.get_categories()
    return render_template('admin/product_form.html', product=None, categories=categories)

@bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    """Edit product."""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.image_url = request.form.get('image_url')
        product.category = request.form.get('category')
        product.is_available = bool(request.form.get('is_available'))
        product.is_featured = bool(request.form.get('is_featured'))
        product.requires_image = bool(request.form.get('requires_image'))
        product.digital_product = bool(request.form.get('digital_product'))
        product.delivery_time = request.form.get('delivery_time')
        product.stock_quantity = int(request.form.get('stock_quantity', 0))
        
        db.session.commit()
        flash('Producto actualizado exitosamente.', 'success')
        return redirect(url_for('admin.products'))
    
    categories = Product.get_categories()
    return render_template('admin/product_form.html', product=product, categories=categories)

@bp.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    """Delete product."""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Producto eliminado exitosamente.', 'success')
    return redirect(url_for('admin.products'))
