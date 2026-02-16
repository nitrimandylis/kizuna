from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Event, EventRegistration, User, Club
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
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
    total_users = User.query.count()

    return render_template('admin/dashboard.html',
                         total_events=total_events,
                         total_registrations=total_registrations,
                         total_users=total_users)

@admin_bp.route('/events')
@login_required
@admin_required
def manage_events():
    page = request.args.get('page', 1, type=int)
    events = Event.query.order_by(Event.event_date.desc()).paginate(page=page, per_page=20)
    return render_template('admin/events.html', events=events)

@admin_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    if request.method == 'POST':
        event = Event(
            title=request.form.get('title'),
            description=request.form.get('description'),
            cas_type=request.form.get('cas_type'),
            location=request.form.get('location'),
            is_published=True
        )

        event_date_str = request.form.get('event_date')
        if event_date_str:
            event.event_date = datetime.strptime(event_date_str, "%Y-%m-%d")
        
        max_capacity = request.form.get('max_capacity')
        if max_capacity:
            event.max_capacity = int(max_capacity)
        
        club_id = request.form.get('club_id')
        if club_id:
            event.club_id = int(club_id)

        db.session.add(event)
        db.session.commit()

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
        event.title = request.form.get('title', event.title)
        event.description = request.form.get('description', event.description)
        event.cas_type = request.form.get('cas_type', event.cas_type)
        event.location = request.form.get('location', event.location)
        
        event_date_str = request.form.get('event_date')
        if event_date_str:
            event.event_date = datetime.strptime(event_date_str, "%Y-%m-%d")
        
        max_capacity = request.form.get('max_capacity')
        if max_capacity:
            event.max_capacity = int(max_capacity)
        else:
            event.max_capacity = None
        
        club_id = request.form.get('club_id')
        if club_id:
            event.club_id = int(club_id)
        else:
            event.club_id = None
        
        event.is_published = request.form.get('is_published') == 'on'
        
        db.session.commit()
        flash('Event updated successfully', 'success')
        return redirect(url_for('admin.manage_events'))
    
    clubs = Club.query.filter_by(is_active=True).all()
    return render_template('admin/edit_event.html', event=event, clubs=clubs)

@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
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
        club = Club(
            name=request.form.get('name'),
            description=request.form.get('description'),
            meeting_day=request.form.get('meeting_day'),
            meeting_time=request.form.get('meeting_time'),
            meeting_location=request.form.get('meeting_location'),
            leader_name=request.form.get('leader_name'),
            leader_email=request.form.get('leader_email'),
            website_url=request.form.get('website_url'),
            is_active=True
        )
        
        db.session.add(club)
        db.session.commit()
        
        flash('Club created successfully', 'success')
        return redirect(url_for('admin.manage_clubs'))
    
    return render_template('admin/create_club.html')

@admin_bp.route('/clubs/<int:club_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_club(club_id):
    club = Club.query.get_or_404(club_id)
    
    if request.method == 'POST':
        club.name = request.form.get('name', club.name)
        club.description = request.form.get('description', club.description)
        club.meeting_day = request.form.get('meeting_day')
        club.meeting_time = request.form.get('meeting_time')
        club.meeting_location = request.form.get('meeting_location')
        club.leader_name = request.form.get('leader_name')
        club.leader_email = request.form.get('leader_email')
        club.website_url = request.form.get('website_url')
        club.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Club updated successfully', 'success')
        return redirect(url_for('admin.manage_clubs'))
    
    return render_template('admin/edit_club.html', club=club)

@admin_bp.route('/clubs/<int:club_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    db.session.delete(club)
    db.session.commit()
    flash('Club deleted', 'success')
    return redirect(url_for('admin.manage_clubs'))

# User Management
@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot modify your own admin status', 'error')
        return redirect(url_for('admin.manage_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"Admin status {'granted' if user.is_admin else 'revoked'}", 'success')
    return redirect(url_for('admin.manage_users'))
