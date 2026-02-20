from flask import Blueprint, render_template, jsonify, request
from models import Club, Event
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    clubs_count = Club.query.filter_by(is_active=True).count()
    return render_template('home.html', clubs_count=clubs_count)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    return render_template('terms.html')

@main_bp.route('/calendar')
def calendar():
    return render_template('calendar.html')

@main_bp.route('/api/events')
def get_events():
    """API endpoint to fetch events for calendar"""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    if not year or not month:
        now = datetime.now()
        year = now.year
        month = now.month
    
    # Get first and last day of month
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year + 1, 1, 1)
    else:
        last_day = datetime(year, month + 1, 1)
    
    # Fetch events for the month
    events = Event.query.filter(
        Event.is_published == True,
        Event.event_date >= first_day,
        Event.event_date < last_day
    ).all()
    
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'date': event.event_date.strftime('%Y-%m-%d'),
            'cas_type': event.cas_type.lower()
        })
    
    return jsonify(events_data)
