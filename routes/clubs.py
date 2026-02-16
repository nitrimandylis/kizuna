from flask import Blueprint, render_template, request
from models import Club
from sqlalchemy import or_

clubs_bp = Blueprint('clubs', __name__, url_prefix='/clubs')

@clubs_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    
    query = Club.query.filter_by(is_active=True)
    
    # Search functionality
    if search:
        search_filter = or_(
            Club.name.ilike(f'%{search}%'),
            Club.description.ilike(f'%{search}%'),
            Club.leader_name.ilike(f'%{search}%'),
            Club.meeting_location.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)
    
    clubs = query.paginate(page=page, per_page=12)
    return render_template('clubs/index.html', clubs=clubs, search=search)

@clubs_bp.route('/<int:club_id>')
def detail(club_id):
    club = Club.query.get_or_404(club_id)
    events = club.events if club.events else []
    return render_template('clubs/detail.html', club=club, events=events)
