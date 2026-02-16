import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Event, EventRegistration
from sqlalchemy import or_, func

events_bp = Blueprint('events', __name__, url_prefix='/events')
logger = logging.getLogger(__name__)

@events_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    cas_type = request.args.get('type')
    search = request.args.get('q', '').strip()

    query = Event.query.filter_by(is_published=True)
    
    # Filter by CAS type
    if cas_type:
        query = query.filter_by(cas_type=cas_type)
    
    # Search functionality
    if search:
        search_filter = or_(
            Event.title.ilike(f'%{search}%'),
            Event.description.ilike(f'%{search}%'),
            Event.location.ilike(f'%{search}%'),
            Event.organizer_name.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)

    events = query.order_by(Event.event_date.desc()).paginate(page=page, per_page=20)
    return render_template('events/index.html', events=events, selected_type=cas_type, search=search)

@events_bp.route('/<int:event_id>')
def detail(event_id):
    event = Event.query.get_or_404(event_id)
    is_registered = False

    if current_user.is_authenticated:
        is_registered = EventRegistration.query.filter_by(
            event_id=event_id, 
            user_id=current_user.id,
            status='confirmed'
        ).first() is not None

    return render_template('events/detail.html', event=event, is_registered=is_registered)

@events_bp.route('/<int:event_id>/register', methods=['POST'])
@login_required
def register(event_id):
    event = Event.query.get_or_404(event_id)

    # Check if already registered
    if EventRegistration.query.filter_by(event_id=event_id, user_id=current_user.id).first():
        flash('You are already registered for this event', 'warning')
        return redirect(url_for('events.detail', event_id=event_id))

    # Check capacity with database-level count for accuracy
    if event.max_capacity:
        current_count = db.session.query(func.count(EventRegistration.id)).filter(
            EventRegistration.event_id == event_id,
            EventRegistration.status == 'confirmed'
        ).scalar()
        
        if current_count >= event.max_capacity:
            logger.warning(f"Registration attempt for full event: '{event.title}' (ID: {event_id}) by user: {current_user.username}")
            flash('This event is at full capacity', 'error')
            return redirect(url_for('events.detail', event_id=event_id))

    registration = EventRegistration(
        event_id=event_id,
        user_id=current_user.id,
        full_name=current_user.username,
        email=current_user.email
    )

    db.session.add(registration)
    db.session.commit()
    
    logger.info(f"User registered for event: '{event.title}' (ID: {event_id}) - user: {current_user.username}")

    flash('Successfully registered for the event!', 'success')
    return redirect(url_for('events.detail', event_id=event_id))

@events_bp.route('/<int:event_id>/unregister', methods=['POST'])
@login_required
def unregister(event_id):
    registration = EventRegistration.query.filter_by(
        event_id=event_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(registration)
    db.session.commit()
    
    logger.info(f"User unregistered from event ID: {event_id} - user: {current_user.username}")

    flash('You have been unregistered from the event', 'success')
    return redirect(url_for('events.detail', event_id=event_id))
