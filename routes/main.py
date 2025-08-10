from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from models.portfolio import Portfolio
from models.product import Product
from models.order import Order

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Homepage with featured work and products."""
    # Get featured portfolio works
    featured_works = Portfolio.get_featured()
    if not featured_works:
        # If no featured works, get latest 6 works
        featured_works = Portfolio.query.order_by(Portfolio.created_at.desc()).limit(6).all()
    
    # Get featured products
    featured_products = Product.get_featured()
    if not featured_products:
        # If no featured products, get latest 3 products
        featured_products = Product.query.filter_by(is_available=True)\
                                        .order_by(Product.created_at.desc()).limit(3).all()
    
    return render_template('index.html', 
                         featured_works=featured_works,
                         featured_products=featured_products)

@bp.route('/about')
def about():
    """About page with Elena's story, skills, and timeline."""
    return render_template('about.html')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form submission."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', '').strip()
        budget = request.form.get('budget', '').strip()
        timeline = request.form.get('timeline', '').strip()
        message = request.form.get('message', '').strip()
        
        # Basic validation
        if not name or not email or not message:
            flash('Please fill in all required fields (Name, Email, Message).', 'error')
            return render_template('contact.html')
        
        # Email validation (basic)
        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'error')
            return render_template('contact.html')
        
        # Here you would typically:
        # 1. Send an email to Elena with the contact details
        # 2. Save the inquiry to the database
        # 3. Send an auto-reply to the customer
        
        # For now, just store in session for demo purposes
        inquiry_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'subject': subject,
            'budget': budget,
            'timeline': timeline,
            'message': message
        }
        
        # In a real application, you would save this to database or send email
        # For demo, we'll just show success message
        flash(f'Thank you {name}! Your message has been sent successfully. I\'ll get back to you within 24 hours.', 'success')
        
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html')

@bp.route('/services')
def services():
    """Services page with detailed service offerings."""
    services_data = [
        {
            'name': 'Custom Portraits',
            'description': 'Personalized digital and traditional portraits',
            'starting_price': 150,
            'features': ['High-resolution digital files', 'Multiple style options', 'Unlimited revisions', 'Print-ready formats'],
            'delivery_time': '3-5 business days'
        },
        {
            'name': 'Brand Identity',
            'description': 'Complete brand identity packages',
            'starting_price': 800,
            'features': ['Logo design', 'Color palette', 'Typography selection', 'Brand guidelines', 'Business card design'],
            'delivery_time': '1-2 weeks'
        },
        {
            'name': 'Web Design',
            'description': 'Modern, responsive website designs',
            'starting_price': 1200,
            'features': ['Custom design', 'Mobile responsive', 'SEO optimized', 'Content management', 'Performance optimization'],
            'delivery_time': '2-4 weeks'
        },
        {
            'name': 'Print Design',
            'description': 'Professional print materials',
            'starting_price': 200,
            'features': ['Brochures & flyers', 'Posters & banners', 'Packaging design', 'Print-ready files', 'Multiple formats'],
            'delivery_time': '1-2 weeks'
        }
    ]
    
    return render_template('services.html', services=services_data)

@bp.route('/search')
def search():
    """Search functionality across portfolio and products."""
    query = request.args.get('q', '').strip()
    
    if not query:
        flash('Please enter a search term.', 'warning')
        return redirect(url_for('main.index'))
    
    # Search in portfolio
    portfolio_results = Portfolio.query.filter(
        Portfolio.title.contains(query) | 
        Portfolio.description.contains(query) |
        Portfolio.category.contains(query)
    ).all()
    
    # Search in products
    product_results = Product.query.filter(
        Product.name.contains(query) |
        Product.description.contains(query) |
        Product.category.contains(query)
    ).filter_by(is_available=True).all()
    
    total_results = len(portfolio_results) + len(product_results)
    
    return render_template('search_results.html',
                         query=query,
                         portfolio_results=portfolio_results,
                         product_results=product_results,
                         total_results=total_results)

@bp.route('/portfolio')
def portfolio_redirect():
    """Redirect to portfolio blueprint."""
    return redirect(url_for('portfolio.index'))

@bp.route('/shop')
def shop_redirect():
    """Redirect to shop blueprint."""
    return redirect(url_for('shop.index'))

@bp.route('/legal')
def legal():
    """Legal notice page."""
    return render_template('legal.html')

@bp.route('/privacy')
def privacy():
    """Privacy policy page."""
    return render_template('privacy.html')

@bp.route('/cookies')
def cookies():
    """Cookies policy page."""
    return render_template('cookies.html')

@bp.route('/terms')
def terms():
    """Terms and conditions page."""
    return render_template('terms.html')

@bp.route('/faq')
def faq():
    """Frequently asked questions page."""
    faqs = [
        {
            'question': 'How long does a custom portrait take?',
            'answer': 'Custom portraits typically take 3-5 business days, depending on complexity and current workload.'
        },
        {
            'question': 'What file formats do you provide?',
            'answer': 'I provide high-resolution files in PNG, JPEG, and PDF formats. For print projects, I also include print-ready files.'
        },
        {
            'question': 'Do you offer revisions?',
            'answer': 'Yes! I include up to 3 rounds of revisions for all projects to ensure you\'re completely satisfied.'
        },
        {
            'question': 'What information do you need for a custom portrait?',
            'answer': 'I need high-quality reference photos, preferred style/mood, dimensions, and any specific requirements or preferences.'
        },
        {
            'question': 'Do you work with international clients?',
            'answer': 'Yes! Since most of my work is digital, I can work with clients worldwide. All prices are in USD.'
        },
        {
            'question': 'What payment methods do you accept?',
            'answer': 'I accept all major credit cards, PayPal, and bank transfers through Stripe\'s secure payment system.'
        }
    ]
    
    return render_template('faq.html', faqs=faqs)

@bp.route('/testimonials')
def testimonials():
    """Client testimonials page."""
    testimonials_data = [
        {
            'name': 'Sarah Johnson',
            'project': 'Brand Identity',
            'rating': 5,
            'text': 'Elena created an absolutely stunning brand identity for my startup. The attention to detail and creative vision exceeded my expectations.',
            'image': 'https://images.unsplash.com/photo-1494790108755-2616c8da3f46?w=150'
        },
        {
            'name': 'Michael Chen',
            'project': 'Custom Portrait',
            'rating': 5,
            'text': 'The family portrait Elena created is now the centerpiece of our living room. She captured our personalities perfectly.',
            'image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150'
        },
        {
            'name': 'Emma Davis',
            'project': 'Web Design',
            'rating': 5,
            'text': 'Professional, creative, and delivered exactly what we needed. Our new website has increased our conversion rate significantly.',
            'image': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150'
        }
    ]
    
    return render_template('testimonials.html', testimonials=testimonials_data)

@bp.route('/blog')
def blog():
    """Blog/articles page."""
    # In a real application, you would fetch blog posts from database
    blog_posts = [
        {
            'id': 1,
            'title': 'The Psychology of Color in Brand Design',
            'excerpt': 'Understanding how colors influence emotions and brand perception...',
            'date': '2024-01-15',
            'image': 'https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=400',
            'category': 'Design Tips'
        },
        {
            'id': 2,
            'title': 'Creating Memorable Logo Designs',
            'excerpt': 'Key principles for designing logos that stand the test of time...',
            'date': '2024-01-10',
            'image': 'https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=400',
            'category': 'Branding'
        }
    ]
    
    return render_template('blog.html', posts=blog_posts)

@bp.route('/sitemap')
def sitemap():
    """Generate sitemap for SEO."""
    # This could return XML sitemap for search engines
    pages = [
        url_for('main.index'),
        url_for('main.about'),
        url_for('main.contact'),
        url_for('main.services'),
        url_for('portfolio.index'),
        url_for('shop.index'),
        url_for('main.faq'),
        url_for('main.testimonials'),
        url_for('main.blog')
    ]
    
    return render_template('sitemap.html', pages=pages)

# AJAX/API endpoints for main functionality
@bp.route('/api/newsletter', methods=['POST'])
def newsletter_signup():
    """Newsletter signup endpoint."""
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email or '@' not in email:
        return jsonify({'error': 'Valid email address required'}), 400
    
    # In a real application, you would:
    # 1. Validate email format
    # 2. Check if already subscribed
    # 3. Add to email marketing service (Mailchimp, etc.)
    # 4. Send welcome email
    
    return jsonify({'success': True, 'message': 'Successfully subscribed to newsletter!'})

@bp.route('/api/quick-quote', methods=['POST'])
def quick_quote():
    """Quick quote estimation endpoint."""
    data = request.get_json()
    service_type = data.get('service_type')
    complexity = data.get('complexity', 'medium')
    timeline = data.get('timeline', 'standard')
    
    # Simple quote estimation logic
    base_prices = {
        'portrait': 150,
        'logo': 450,
        'branding': 800,
        'web': 1200,
        'print': 200
    }
    
    complexity_multiplier = {
        'simple': 0.8,
        'medium': 1.0,
        'complex': 1.5
    }
    
    timeline_multiplier = {
        'rush': 1.5,
        'standard': 1.0,
        'flexible': 0.9
    }
    
    if service_type not in base_prices:
        return jsonify({'error': 'Invalid service type'}), 400
    
    base_price = base_prices[service_type]
    final_price = base_price * complexity_multiplier.get(complexity, 1.0) * timeline_multiplier.get(timeline, 1.0)
    
    return jsonify({
        'estimated_price': round(final_price, 2),
        'price_range': f"${final_price * 0.8:.0f} - ${final_price * 1.2:.0f}",
        'message': 'This is an estimated price. Final quote will be provided after consultation.'
    })

# Error handlers (these could also be in the main app.py)
@bp.app_errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html'), 500