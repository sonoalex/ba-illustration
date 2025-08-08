from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from models.product import Product
from models.order import Order, OrderItem
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
        data = request.get_json()
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
        
        # Create payment intent with Stripe
        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # Stripe uses cents
            currency='usd',
            automatic_payment_methods={'enabled': True},
            metadata={
                'customer_name': customer_name,
                'customer_email': customer_email,
                'item_count': len(order_items)
            }
        )
        
        # Create order in database
        order = Order(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=data.get('phone', ''),
            total_amount=total_amount,
            stripe_payment_intent_id=intent.id,
            status='pending',
            payment_status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Add order items
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                product_name=item_data['product'].name,
                product_description=item_data['product'].description,
                unit_price=item_data['unit_price'],
                quantity=item_data['quantity']
            )
            db.session.add(order_item)
        
        # Calculate and save totals
        order.calculate_totals()
        db.session.commit()
        
        return jsonify({
            'client_secret': intent.client_secret,
            'order_id': order.order_id,
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
        order = Order.query.filter_by(order_id=order_id).first()
        if order and order.payment_status == 'pending':
            order.mark_as_paid()
            db.session.commit()
            
            # Clear the cart after successful payment
            session.pop('cart', None)
            session.modified = True
    
    return render_template('payment_success.html', order=order)

@bp.route('/order/<order_id>')
def order_detail(order_id):
    """Order detail page."""
    order = Order.query.filter_by(order_id=order_id).first_or_404()
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