import logging
from flask import Blueprint, render_template, request
from models import Club, Event
from sqlalchemy import or_, func

clubs_bp = Blueprint('clubs', __name__, url_prefix='/clubs')
logger = logging.getLogger(__name__)

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

@clubs_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    day = request.args.get('day', '').strip()
    
    query = Club.query.filter_by(is_active=True)
    
    if day and day in DAYS:
        query = query.filter(Club.meeting_day == day)
    
    if search:
        search_filter = or_(
            Club.name.ilike(f'%{search}%'),
            Club.description.ilike(f'%{search}%'),
            Club.leader_name.ilike(f'%{search}%'),
            Club.meeting_location.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)
    
    clubs = query.paginate(page=page, per_page=12)
    
    event_counts = {}
    for club in clubs.items:
        event_counts[club.id] = Event.query.filter_by(club_id=club.id).count()
    
    return render_template('clubs/index.html', clubs=clubs, search=search, day=day, days=DAYS, event_counts=event_counts)

@clubs_bp.route('/<int:club_id>')
def detail(club_id):
    club = Club.query.get_or_404(club_id)
    events = club.events if club.events else []
    logger.debug(f"Club detail viewed: '{club.name}' (ID: {club_id})")
    return render_template('clubs/detail.html', club=club, events=events)
