from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Event, EventRegistration

events_bp = Blueprint('events', __name__, url_prefix='/events')

@events_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    cas_type = request.args.get('type')

    query = Event.query.filter_by(is_published=True)
    if cas_type:
        query = query.filter_by(cas_type=cas_type)

    events = query.order_by(Event.event_date.desc()).paginate(page=page, per_page=20)
    return render_template('events/index.html', events=events, selected_type=cas_type)

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

    if EventRegistration.query.filter_by(event_id=event_id, user_id=current_user.id).first():
        flash('You are already registered for this event', 'warning')
        return redirect(url_for('events.detail', event_id=event_id))

    if event.is_full():
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

    flash('You have been unregistered from the event', 'success')
    return redirect(url_for('events.detail', event_id=event_id))
