from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models.product import Product
from models.order import Order, OrderItem
from models.user import User
from app import db
import stripe
import os

bp = Blueprint('shop', __name__)

# Initialize Stripe
def get_stripe_key():
    return current_app.config.get('STRIPE_SECRET_KEY') or os.environ.get('STRIPE_SECRET_KEY')

@bp.route('/')
def index():
    """Shop main page with product grid."""
    category = request.args.get('category', 'all')
    products = Product.get_by_category(category)
    categories = Product.get_categories()
    
    return render_template('shop.html', 
                         products=products, 
                         categories=categories, 
                         selected_category=category)

@bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Individual product detail page."""
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter_by(category=product.category)\
                                  .filter(Product.id != product_id)\
                                  .filter_by(is_available=True)\
                                  .limit(4).all()
    
    return render_template('product_detail.html', 
                         product=product,
                         related_products=related_products)

@bp.route('/cart')
def cart():
    """Shopping cart page."""
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product and product.is_available:
            subtotal = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
    
    stripe_key = current_app.config.get('STRIPE_PUBLISHABLE_KEY') or os.environ.get('STRIPE_PUBLISHABLE_KEY')
    return render_template('cart.html', 
                         cart_items=cart_items, 
                         total=total,
                         stripe_key=stripe_key)

@bp.route('/checkout')
@login_required
def checkout():
    """Checkout page - requires login."""
    cart = session.get('cart', {})
    if not cart:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('shop.cart'))
    
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product and product.is_available:
            subtotal = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
    
    if not cart_items:
        flash('No hay productos válidos en tu carrito.', 'warning')
        return redirect(url_for('shop.cart'))
    
    stripe_key = current_app.config.get('STRIPE_PUBLISHABLE_KEY') or os.environ.get('STRIPE_PUBLISHABLE_KEY')
    return render_template('checkout.html', 
                         cart_items=cart_items, 
                         total=total,
                         stripe_key=stripe_key)

@bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Add product to cart."""
    try:
        data = request.get_json()
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        
        # Verify product exists and is available
        product = Product.query.get(int(product_id))
        if not product or not product.is_available:
            return jsonify({'error': 'Product not available'}), 400
        
        # Check stock if not digital product
        if not product.check_availability(quantity):
            return jsonify({'error': 'Insufficient stock'}), 400
        
        # Initialize cart if it doesn't exist
        if 'cart' not in session:
            session['cart'] = {}
        
        cart = session['cart']
        
        # Add or update quantity in cart
        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity
        
        session['cart'] = cart
        session.modified = True
        
        # Calculate total items in cart
        cart_count = sum(cart.values())
        
        return jsonify({
            'success': True, 
            'cart_count': cart_count,
            'message': f'{product.name} added to cart!'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error adding to cart: {str(e)}")
        return jsonify({'error': 'Failed to add item to cart'}), 500

@bp.route('/update_cart', methods=['POST'])
def update_cart():
    """Update product quantity in cart."""
    try:
        data = request.get_json()
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity'))
        
        if 'cart' not in session:
            return jsonify({'error': 'Cart is empty'}), 400
        
        cart = session['cart']
        
        if quantity > 0:
            # Verify product still exists and is available
            product = Product.query.get(int(product_id))
            if not product or not product.is_available:
                return jsonify({'error': 'Product no longer available'}), 400
            
            # Check stock availability
            if not product.check_availability(quantity):
                return jsonify({'error': 'Insufficient stock'}), 400
            
            cart[product_id] = quantity
        else:
            cart.pop(product_id, None)
        
        session['cart'] = cart
        session.modified = True
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Error updating cart: {str(e)}")
        return jsonify({'error': 'Failed to update cart'}), 500

@bp.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    """Remove product from cart."""
    try:
        data = request.get_json()
        product_id = str(data.get('product_id'))
        
        if 'cart' in session and product_id in session['cart']:
            del session['cart'][product_id]
            session.modified = True
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Error removing from cart: {str(e)}")
        return jsonify({'error': 'Failed to remove item from cart'}), 500

@bp.route('/clear_cart', methods=['POST'])
def clear_cart():
    """Clear entire cart."""
    try:
        session.pop('cart', None)
        session.modified = True
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f"Error clearing cart: {str(e)}")
        return jsonify({'error': 'Failed to clear cart'}), 500

@bp.route('/cart_count')
def cart_count():
    """Get current cart count."""
    cart = session.get('cart', {})
    count = sum(cart.values())
    return jsonify({'count': count})

@bp.route('/cart_total')
def cart_total():
    """Get current cart total."""
    cart = session.get('cart', {})
    total = 0
    
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product and product.is_available:
            total += product.price * quantity
    
    return jsonify({'total': total})

@bp.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """Create Stripe payment intent."""
    try:
        # Handle both JSON and FormData
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = {
                'name': request.form.get('name'),
                'email': request.form.get('email'),
                'address_line1': request.form.get('address_line1'),
                'address_line2': request.form.get('address_line2'),
                'address_city': request.form.get('address_city'),
                'address_postal': request.form.get('address_postal'),
                'address_country': request.form.get('address_country'),
            }
            customer_image_file = request.files.get('customer_image')
        else:
            data = request.get_json()
            customer_image_file = None
            
        cart = session.get('cart', {})
        
        if not cart:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Validate required customer information
        customer_name = data.get('name', '').strip()
        customer_email = data.get('email', '').strip()
        
        if not customer_name or not customer_email:
            return jsonify({'error': 'Customer name and email are required'}), 400
        
        # Calculate total amount and validate cart items
        total_amount = 0
        order_items = []
        
        for product_id, quantity in cart.items():
            product = Product.query.get(int(product_id))
            if not product or not product.is_available:
                return jsonify({'error': f'Product {product_id} is no longer available'}), 400
            
            if not product.check_availability(quantity):
                return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
            
            subtotal = product.price * quantity
            total_amount += subtotal
            order_items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': product.price,
                'subtotal': subtotal
            })
        
        if total_amount == 0:
            return jsonify({'error': 'Invalid cart items'}), 400
        
        # Minimum charge amount for Stripe (50 cents)
        if total_amount < 0.50:
            return jsonify({'error': 'Order total must be at least $0.50'}), 400
        
        # Initialize Stripe with the secret key
        stripe.api_key = get_stripe_key()
        
        if not stripe.api_key:
            current_app.logger.error("Stripe secret key not configured")
            return jsonify({'error': 'Payment processing is not configured'}), 500
        
        # Build shipping details (optional but useful)
        shipping = {
            'name': customer_name,
            'address': {
                'line1': data.get('address_line1', ''),
                'line2': data.get('address_line2', ''),
                'city': data.get('address_city', ''),
                'postal_code': data.get('address_postal', ''),
                'country': data.get('address_country', '')
            }
        }

        # Create payment intent with Stripe
        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # Stripe uses cents
            currency='eur',
            automatic_payment_methods={'enabled': True},
            shipping=shipping,
            metadata={
                'customer_name': customer_name,
                'customer_email': customer_email,
                'item_count': len(order_items)
            }
        )
        
        # Create order in database
        # Persist order with shipping address
        address_line1 = data.get('address_line1', '')
        address_line2 = data.get('address_line2', '')
        address_city = data.get('address_city', '')
        address_postal = data.get('address_postal', '')
        address_country = data.get('address_country', '')
        shipping_address = \
            f"{address_line1}\n{address_line2}\n{address_postal} {address_city}\n{address_country}".strip()

        order = Order(
            user_id=current_user.id if current_user.is_authenticated else None,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=data.get('phone', ''),
            shipping_address=shipping_address,
            total_amount=total_amount,
            stripe_payment_intent_id=intent.id,
            status='pending',
            payment_status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Add order items
        for item_data in order_items:
            customer_image_path = None
            
            # Handle customer image upload for products that require it
            if item_data['product'].requires_image and customer_image_file:
                import os
                from datetime import datetime
                from werkzeug.utils import secure_filename
                
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'customer_images')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                original_filename = secure_filename(customer_image_file.filename)
                file_extension = os.path.splitext(original_filename)[1] or '.jpg'
                filename = f"customer_{order.id}_{item_data['product'].id}_{timestamp}{file_extension}"
                filepath = os.path.join(upload_dir, filename)
                
                # Save the uploaded file
                try:
                    customer_image_file.save(filepath)
                    customer_image_path = f"uploads/customer_images/{filename}"
                except Exception as e:
                    current_app.logger.error(f"Error saving customer image: {str(e)}")
                    return jsonify({'error': 'Error al guardar la imagen'}), 500
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                product_name=item_data['product'].name,
                product_price=item_data['unit_price'],
                quantity=item_data['quantity'],
                customer_image=customer_image_path
            )
            db.session.add(order_item)
        
        # Commit the order
        db.session.commit()
        
        return jsonify({
            'client_secret': intent.client_secret,
            'order_id': order.id,
            'amount': total_amount
        })
        
    except stripe.error.StripeError as e:
        current_app.logger.error(f"Stripe error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Payment processing error. Please try again.'}), 500
    except Exception as e:
        current_app.logger.error(f"Error creating payment intent: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'An unexpected error occurred'}), 500

@bp.route('/payment-success')
def payment_success():
    """Payment success page."""
    order_id = request.args.get('order_id')
    order = None
    
    if order_id:
        order = Order.query.get(order_id)
        if order and order.payment_status == 'pending':
            order.payment_status = 'paid'
            db.session.commit()
            
            # Clear the cart after successful payment
            session.pop('cart', None)
            session.modified = True
    
    return render_template('payment_success.html', order=order)

@bp.route('/order/<order_id>')
def order_detail(order_id):
    """Order detail page."""
    order = Order.query.get_or_404(order_id)
    return render_template('order_detail.html', order=order)

@bp.route('/my-orders')
def my_orders():
    """List customer orders (simple version - in production you'd want proper authentication)."""
    email = request.args.get('email')
    if not email:
        flash('Please provide your email address to view orders.', 'warning')
        return redirect(url_for('main.contact'))
    
    orders = Order.query.filter_by(customer_email=email)\
                       .order_by(Order.created_at.desc()).all()
    
    return render_template('my_orders.html', orders=orders, email=email)

@bp.route('/download-customer-image/<int:order_item_id>')
@login_required
def download_customer_image(order_item_id):
    """Download customer image for admin."""
    from flask import send_from_directory
    
    order_item = OrderItem.query.get_or_404(order_item_id)
    
    if not order_item.customer_image:
        flash('No hay imagen disponible para este pedido.', 'error')
        return redirect(url_for('admin.order_detail', order_id=order_item.order_id))
    
    # Check if user is admin or the order owner
    if not current_user.is_admin() and order_item.order.user_id != current_user.id:
        flash('No tienes permisos para acceder a esta imagen.', 'error')
        return redirect(url_for('main.index'))
    
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'customer_images')
    filename = os.path.basename(order_item.customer_image)
    
    return send_from_directory(upload_dir, filename, as_attachment=True)

@bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks for payment confirmations."""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # In production, you should verify the webhook signature
        # endpoint_secret = 'whsec_...'
        # event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        
        # For now, just parse the event
        import json
        event = json.loads(payload)
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            
            # Find the corresponding order
            order = Order.query.filter_by(
                stripe_payment_intent_id=payment_intent['id']
            ).first()
            
            if order:
                order.mark_as_paid()
                db.session.commit()
                current_app.logger.info(f"Order {order.order_id} marked as paid via webhook")
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        current_app.logger.error(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 400