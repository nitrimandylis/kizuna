from flask import Blueprint, render_template
from models import Club, Event

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured_events = Event.query.filter_by(is_published=True).limit(6).all()
    clubs_count = Club.query.filter_by(is_active=True).count()
    return render_template('home.html', featured_events=featured_events, clubs_count=clubs_count)

@main_bp.route('/about')
def about():
    return render_template('about.html')
