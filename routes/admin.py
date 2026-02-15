from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Event, EventRegistration, User
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
            location=request.form.get('location')
        )

        event_date_str = request.form.get('event_date')
        if event_date_str:
            event.event_date = datetime.strptime(event_date_str, "%Y-%m-%d")

        db.session.add(event)
        db.session.commit()

        flash('Event created successfully', 'success')
        return redirect(url_for('admin.manage_events'))

    return render_template('admin/create_event.html')

@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted', 'success')
    return redirect(url_for('admin.manage_events'))
