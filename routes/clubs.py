from flask import Blueprint, render_template, request
from models import Club

clubs_bp = Blueprint('clubs', __name__, url_prefix='/clubs')

@clubs_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    clubs = Club.query.filter_by(is_active=True).paginate(page=page, per_page=12)
    return render_template('clubs/index.html', clubs=clubs)

@clubs_bp.route('/<int:club_id>')
def detail(club_id):
    club = Club.query.get_or_404(club_id)
    events = club.events if club.events else []
    return render_template('clubs/detail.html', club=club, events=events)
