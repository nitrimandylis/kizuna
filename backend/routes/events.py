import logging
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Event, EventRegistration
from sqlalchemy import or_, func

events_bp = Blueprint('events', __name__, url_prefix='/events')
logger = logging.getLogger(__name__)

@events_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    cas_type = request.args.get('type')
    search = request.args.get('q', '').strip()
    time_filter = request.args.get('time', 'upcoming')

    query = Event.query.filter_by(is_published=True)
    
    # Filter by CAS type
    if cas_type:
        query = query.filter_by(cas_type=cas_type)
    
    # Filter by time (upcoming/past)
    today = date.today()
    if time_filter == 'past':
        query = query.filter(Event.event_date < today)
    else:
        query = query.filter(Event.event_date >= today)
    
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
    
    today = date.today()
    related_query = Event.query.filter(
        Event.id != event_id,
        Event.is_published == True,
        Event.event_date >= today
    )
    
    if event.club_id:
        related_query = related_query.filter(
            or_(
                Event.cas_type == event.cas_type,
                Event.club_id == event.club_id
            )
        )
    else:
        related_query = related_query.filter(Event.cas_type == event.cas_type)
    
    related_events = related_query.order_by(Event.event_date.asc()).limit(3).all()

    return render_template('events/detail.html', event=event, related_events=related_events)

@events_bp.route('/<int:event_id>/register', methods=['GET', 'POST'])
def register(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()

        if not full_name or not email:
            flash('Please fill in all fields.', 'error')
            return render_template('events/register.html', event=event)

        # Check if already registered
        if EventRegistration.query.filter_by(event_id=event_id, email=email).first():
            flash('You are already registered for this event with this email address.', 'warning')
            return redirect(url_for('events.detail', event_id=event_id))

        # Check capacity
        if event.is_full():
            flash('This event is at full capacity.', 'error')
            return redirect(url_for('events.detail', event_id=event_id))

        registration = EventRegistration(
            event_id=event_id,
            full_name=full_name,
            email=email
        )

        db.session.add(registration)
        db.session.commit()
        
        logger.info(f"New registration for event: '{event.title}' (ID: {event_id}) - Name: {full_name}, Email: {email}")
        
        # Send confirmation email
        try:
            from mail import send_event_registration_email
            # The send_event_registration_email function needs a user object, so we create a dummy one
            class DummyUser:
                def __init__(self, full_name, email):
                    self.username = full_name
                    self.email = email
            
            dummy_user = DummyUser(full_name, email)
            send_event_registration_email(dummy_user, event)
        except Exception as e:
            logger.error(f"Failed to send registration email: {e}")

        flash('Successfully registered for the event!', 'success')
        return redirect(url_for('events.detail', event_id=event_id))

    return render_template('events/register.html', event=event)
