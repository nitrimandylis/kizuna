import logging
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Event, EventRegistration, Club
from datetime import datetime
from time import time
from utils import (
    sanitize_input, validate_title, validate_description, 
    validate_cas_type, validate_integer, validate_url
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            logger.warning(f"Unauthorized admin access attempt by: {current_user.username if current_user.is_authenticated else 'anonymous'}")
            flash('Admin access required', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_events = Event.query.count()
    total_registrations = EventRegistration.query.count()
    
    logger.debug(f"Admin dashboard accessed by: {current_user.username}")

    return render_template('admin/dashboard.html',
                         total_events=total_events,
                         total_registrations=total_registrations)

@admin_bp.route('/events')
@login_required
@admin_required
def manage_events():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    cas_type = request.args.get('cas_type', '').strip()
    status = request.args.get('status', '').strip()
    
    query = Event.query
    
    if search:
        query = query.filter(Event.title.ilike(f'%{search}%'))
    
    if cas_type:
        query = query.filter(Event.cas_type == cas_type)
    
    if status == 'published':
        query = query.filter(Event.is_published.is_(True))
    elif status == 'draft':
        query = query.filter(Event.is_published.is_(False))
    
    events = query.order_by(Event.event_date.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/events.html', events=events, search=search, cas_type=cas_type, status=status)

@admin_bp.route('/events/bulk-delete', methods=['POST'])
@login_required
@admin_required
def bulk_delete_events():
    event_ids = request.form.getlist('event_ids', type=int)
    
    if not event_ids:
        flash('No events selected', 'error')
        return redirect(url_for('admin.manage_events'))
    
    deleted_count = Event.query.filter(Event.id.in_(event_ids)).delete(synchronize_session='fetch')
    db.session.commit()
    
    logger.info(f"Bulk deleted {deleted_count} events by admin: {current_user.username}")
    flash(f'{deleted_count} event(s) deleted', 'success')
    return redirect(url_for('admin.manage_events'))

@admin_bp.route('/events/bulk-publish', methods=['POST'])
@login_required
@admin_required
def bulk_publish_events():
    event_ids = request.form.getlist('event_ids', type=int)
    publish = request.form.get('publish') == 'true'
    
    if not event_ids:
        flash('No events selected', 'error')
        return redirect(url_for('admin.manage_events'))
    
    updated_count = Event.query.filter(Event.id.in_(event_ids)).update(
        {'is_published': publish}, synchronize_session='fetch'
    )
    db.session.commit()
    
    action = 'published' if publish else 'unpublished'
    logger.info(f"Bulk {action} {updated_count} events by admin: {current_user.username}")
    flash(f'{updated_count} event(s) {action}', 'success')
    return redirect(url_for('admin.manage_events'))

@admin_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    if request.method == 'POST':
        errors = []
        
        # Validate title
        valid, title = validate_title(request.form.get('title', ''))
        if not valid:
            errors.append(title)
        
        # Validate description
        valid, description = validate_description(request.form.get('description', ''))
        if not valid:
            errors.append(description)
        
        # Validate CAS type
        valid, cas_type = validate_cas_type(request.form.getlist('cas_type'))
        if not valid:
            errors.append(cas_type)
        
        # Validate date
        event_date_str = request.form.get('event_date', '')
        if not event_date_str:
            errors.append('Event date is required')
        else:
            try:
                event_date = datetime.strptime(event_date_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                errors.append('Invalid date format')
        
        # Validate end_time
        end_time_str = request.form.get('end_time', '')
        end_time = None
        if end_time_str:
            try:
                end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                errors.append('Invalid end time format')
        
        # Validate max_capacity
        valid, max_capacity = validate_integer(
            request.form.get('max_capacity'), 
            "Maximum capacity", 
            min_val=1, 
            max_val=10000
        )
        if not valid:
            errors.append(max_capacity)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            clubs = Club.query.filter_by(is_active=True).all()
            return render_template('admin/create_event.html', clubs=clubs)
        
        # Create event
        event = Event(
            title=title,
            description=description,
            cas_type=cas_type,
            event_date=event_date,
            end_time=end_time,
            location=sanitize_input(request.form.get('location', ''), max_length=200),
            max_capacity=max_capacity,
            is_published=request.form.get('is_published') == 'on'
        )
        
        club_id = request.form.get('club_id')
        if club_id:
            event.club_id = int(club_id)

        db.session.add(event)
        db.session.commit()
        
        logger.info(f"Event created: '{title}' (ID: {event.id}) by admin: {current_user.username}")

        flash('Event created successfully', 'success')
        return redirect(url_for('admin.manage_events'))
    
    clubs = Club.query.filter_by(is_active=True).all()
    return render_template('admin/create_event.html', clubs=clubs)

@admin_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        errors = []
        
        # Validate title
        valid, title = validate_title(request.form.get('title', ''))
        if not valid:
            errors.append(title)
        else:
            event.title = title
        
        # Validate description
        valid, description = validate_description(request.form.get('description', ''))
        if not valid:
            errors.append(description)
        else:
            event.description = description
        
        # Validate CAS type
        valid, cas_type = validate_cas_type(request.form.getlist('cas_type'))
        if not valid:
            errors.append(cas_type)
        else:
            event.cas_type = cas_type
        
        # Validate date
        event_date_str = request.form.get('event_date', '')
        if event_date_str:
            try:
                event.event_date = datetime.strptime(event_date_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                errors.append('Invalid date format')
        
        # Validate end_time
        end_time_str = request.form.get('end_time', '')
        if end_time_str:
            try:
                event.end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                errors.append('Invalid end time format')
        else:
            event.end_time = None
        
        # Validate max_capacity
        valid, max_capacity = validate_integer(
            request.form.get('max_capacity'), 
            "Maximum capacity", 
            min_val=1, 
            max_val=10000
        )
        if not valid:
            errors.append(max_capacity)
        else:
            event.max_capacity = max_capacity
        
        event.location = sanitize_input(request.form.get('location', ''), max_length=200)
        
        club_id = request.form.get('club_id')
        event.club_id = int(club_id) if club_id else None
        
        event.is_published = request.form.get('is_published') == 'on'
        
        if errors:
            for error in errors:
                flash(error, 'error')
            clubs = Club.query.filter_by(is_active=True).all()
            return render_template('admin/edit_event.html', event=event, clubs=clubs)
        
        db.session.commit()
        logger.info(f"Event updated: '{event.title}' (ID: {event.id}) by admin: {current_user.username}")
        flash('Event updated successfully', 'success')
        return redirect(url_for('admin.manage_events'))
    
    clubs = Club.query.filter_by(is_active=True).all()
    return render_template('admin/edit_event.html', event=event, clubs=clubs)

@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    event_title = event.title
    db.session.delete(event)
    db.session.commit()
    logger.info(f"Event deleted: '{event_title}' (ID: {event_id}) by admin: {current_user.username}")
    flash('Event deleted', 'success')
    return redirect(url_for('admin.manage_events'))

# Club Management
@admin_bp.route('/clubs')
@login_required
@admin_required
def manage_clubs():
    page = request.args.get('page', 1, type=int)
    clubs = Club.query.order_by(Club.name).paginate(page=page, per_page=20)
    return render_template('admin/clubs.html', clubs=clubs)

@admin_bp.route('/clubs/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_club():
    if request.method == 'POST':
        errors = []
        
        # Validate name
        valid, name = validate_title(request.form.get('name', ''), max_length=120)
        if not valid:
            errors.append(name)
        
        # Validate description
        valid, description = validate_description(request.form.get('description', ''))
        if not valid:
            errors.append(description)
        
        # Validate URLs
        valid, website_url = validate_url(request.form.get('website_url', ''))
        if not valid:
            errors.append(website_url)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/create_club.html')
        
        club = Club(
            name=name,
            description=description,
            meeting_day=sanitize_input(request.form.get('meeting_day', ''), max_length=20),
            meeting_time=sanitize_input(request.form.get('meeting_time', ''), max_length=10),
            meeting_location=sanitize_input(request.form.get('meeting_location', ''), max_length=120),
            leader_name=sanitize_input(request.form.get('leader_name', ''), max_length=120),
            leader_email=sanitize_input(request.form.get('leader_email', ''), max_length=120),
            website_url=website_url,
            is_active=True
        )
        
        db.session.add(club)
        db.session.commit()
        
        logger.info(f"Club created: '{name}' (ID: {club.id}) by admin: {current_user.username}")
        
        flash('Club created successfully', 'success')
        return redirect(url_for('admin.manage_clubs'))
    
    return render_template('admin/create_club.html')

@admin_bp.route('/clubs/<int:club_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_club(club_id):
    club = Club.query.get_or_404(club_id)
    
    if request.method == 'POST':
        errors = []
        
        # Validate name
        valid, name = validate_title(request.form.get('name', ''), max_length=120)
        if not valid:
            errors.append(name)
        else:
            club.name = name
        
        # Validate description
        valid, description = validate_description(request.form.get('description', ''))
        if not valid:
            errors.append(description)
        else:
            club.description = description
        
        # Validate URLs
        valid, website_url = validate_url(request.form.get('website_url', ''))
        if not valid:
            errors.append(website_url)
        else:
            club.website_url = website_url
        
        club.meeting_day = sanitize_input(request.form.get('meeting_day', ''), max_length=20)
        club.meeting_time = sanitize_input(request.form.get('meeting_time', ''), max_length=10)
        club.meeting_location = sanitize_input(request.form.get('meeting_location', ''), max_length=120)
        club.leader_name = sanitize_input(request.form.get('leader_name', ''), max_length=120)
        club.leader_email = sanitize_input(request.form.get('leader_email', ''), max_length=120)
        club.is_active = request.form.get('is_active') == 'on'
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/edit_club.html', club=club)
        
        db.session.commit()
        logger.info(f"Club updated: '{club.name}' (ID: {club.id}) by admin: {current_user.username}")
        flash('Club updated successfully', 'success')
        return redirect(url_for('admin.manage_clubs'))
    
    return render_template('admin/edit_club.html', club=club)

@admin_bp.route('/clubs/<int:club_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    club_name = club.name
    db.session.delete(club)
    db.session.commit()
    logger.info(f"Club deleted: '{club_name}' (ID: {club_id}) by admin: {current_user.username}")
    flash('Club deleted', 'success')
    return redirect(url_for('admin.manage_clubs'))

@admin_bp.route('/events/<int:event_id>/participants')
@login_required
@admin_required
def event_participants(event_id):
    """View event participants."""
    event = Event.query.get_or_404(event_id)
    registrations = EventRegistration.query.filter_by(event_id=event_id).order_by(EventRegistration.registered_at).all()
    
    first_registration = None
    last_registration = None
    if registrations:
        first_registration = registrations[0].registered_at
        last_registration = registrations[-1].registered_at
    
    return render_template('admin/event_participants.html', 
                         event=event, 
                         registrations=registrations,
                         first_registration=first_registration,
                         last_registration=last_registration)


@admin_bp.route('/events/<int:event_id>/participants/print')
@login_required
@admin_required
def print_event_participants(event_id):
    """Print event participants."""
    event = Event.query.get_or_404(event_id)
    registrations = EventRegistration.query.filter_by(event_id=event_id).order_by(EventRegistration.registered_at).all()
    return render_template('admin/print_participants.html', event=event, registrations=registrations)

