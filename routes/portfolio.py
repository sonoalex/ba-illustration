from flask import Blueprint, render_template, request, jsonify
from models.portfolio import Portfolio

bp = Blueprint('portfolio', __name__)

@bp.route('/')
def index():
    """Portfolio main page with work gallery."""
    category = request.args.get('category', 'all')
    works = Portfolio.get_by_category(category)
    categories = Portfolio.get_categories()
    
    return render_template('portfolio.html', 
                         works=works, 
                         categories=categories, 
                         selected_category=category)

@bp.route('/work/<int:work_id>')
def work_detail(work_id):
    """Individual portfolio work detail page."""
    work = Portfolio.query.get_or_404(work_id)
    related_works = Portfolio.query.filter_by(category=work.category)\
                                  .filter(Portfolio.id != work_id)\
                                  .limit(3).all()
    
    return render_template('work_detail.html', 
                         work=work,
                         related_works=related_works)

@bp.route('/category/<category>')
def category(category):
    """Portfolio filtered by category."""
    works = Portfolio.get_by_category(category)
    categories = Portfolio.get_categories()
    
    return render_template('portfolio.html',
                         works=works,
                         categories=categories,
                         selected_category=category)

@bp.route('/featured')
def featured():
    """Featured portfolio works."""
    works = Portfolio.get_featured()
    categories = Portfolio.get_categories()
    
    return render_template('portfolio.html',
                         works=works,
                         categories=categories,
                         selected_category='featured')