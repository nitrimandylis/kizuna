import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from models import db, User, EventRegistration, Event
from utils import validate_email, validate_password

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')
logger = logging.getLogger(__name__)


@profile_bp.route('/')
@login_required
def index():
    """Show user profile with registered events."""
    page = request.args.get('page', 1, type=int)
    
    from datetime import datetime
    
    total_registrations = EventRegistration.query.filter_by(user_id=current_user.id).count()
    attended_count = EventRegistration.query.filter_by(
        user_id=current_user.id, 
        status='attended'
    ).count()
    
    member_days = (datetime.utcnow() - current_user.created_at).days
    
    registrations = EventRegistration.query.filter_by(
        user_id=current_user.id
    ).order_by(EventRegistration.registered_at.desc()).paginate(page=page, per_page=10)
    
    stats = {
        'total_registrations': total_registrations,
        'attended_count': attended_count,
        'member_days': member_days
    }
    
    return render_template('profile/index.html', registrations=registrations, stats=stats)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit user profile."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        errors = []
        
        valid, email_result = validate_email(email)
        if not valid:
            errors.append(email_result)
        elif email != current_user.email:
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != current_user.id:
                errors.append('Email already in use')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('profile/edit.html')
        
        if email != current_user.email:
            current_user.email = email
            current_user.email_verified = False
            logger.info(f"User {current_user.username} changed email to {email}")
            
            from models import EmailVerificationToken
            from datetime import datetime, timedelta
            import secrets
            
            EmailVerificationToken.query.filter_by(
                user_id=current_user.id, 
                used=False
            ).update({'used': True})
            
            token = secrets.token_urlsafe(32)
            verification_token = EmailVerificationToken(
                user_id=current_user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            db.session.add(verification_token)
            
            flash('Email updated. Please verify your new email address.', 'warning')
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('profile/edit.html')


@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password."""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        errors = []
        
        if not current_user.check_password(current_password):
            errors.append('Current password is incorrect')
        
        valid, password_result = validate_password(new_password)
        if not valid:
            errors.append(password_result)
        
        if new_password != confirm_password:
            errors.append('New passwords do not match')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('profile/change_password.html')
        
        current_user.set_password(new_password)
        db.session.commit()
        
        logger.info(f"User {current_user.username} changed password")
        flash('Password changed successfully', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('profile/change_password.html')


@profile_bp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Delete user account with password confirmation."""
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirmation = request.form.get('confirmation', '')
        
        errors = []
        
        if not current_user.check_password(password):
            errors.append('Password is incorrect')
        
        if confirmation != 'DELETE':
            errors.append('Please type DELETE to confirm')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('profile/delete_account.html')
        
        user_id = current_user.id
        username = current_user.username
        
        EventRegistration.query.filter_by(user_id=user_id).delete()
        
        logout_user()
        
        User.query.filter_by(id=user_id).delete()
        db.session.commit()
        
        logger.info(f"User {username} deleted their account")
        flash('Your account has been permanently deleted.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('profile/delete_account.html')
