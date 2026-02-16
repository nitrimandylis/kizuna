import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, PasswordResetToken, EmailVerificationToken
from datetime import datetime, timedelta
from utils import validate_username, validate_email, validate_password, check_rate_limit, get_client_ip
import secrets

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Rate limit by IP
    ip = get_client_ip()
    allowed, remaining = check_rate_limit(f'register:{ip}', max_requests=5, window_seconds=3600)
    if not allowed:
        logger.warning(f"Registration rate limited for IP: {ip}")
        flash(f'Too many registration attempts. Please try again in {remaining // 60} minutes.', 'error')
        return render_template('auth/register.html')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        errors = []
        
        valid, username_result = validate_username(username)
        if not valid:
            errors.append(username_result)
        
        valid, email_result = validate_email(email)
        if not valid:
            errors.append(email_result)
        
        valid, password_result = validate_password(password)
        if not valid:
            errors.append(password_result)
        
        if password != confirm_password:
            errors.append('Passwords do not match')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')

        # Check existing
        if User.query.filter_by(username=username).first():
            logger.info(f"Registration attempt with existing username: {username}")
            flash('Username already taken', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            logger.info(f"Registration attempt with existing email: {email}")
            flash('Email already registered', 'error')
            return render_template('auth/register.html')

        # Create user
        user = User(username=username, email=email, email_verified=False)
        user.set_password(password)
        db.session.add(user)
        
        # Create verification token
        token = secrets.token_urlsafe(32)
        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        db.session.add(verification_token)
        db.session.commit()
        
        logger.info(f"New user registered: {username} ({email}) from IP: {ip}")
        
        # Send verification email
        from mail import send_verification_email
        result = send_verification_email(user, token)
        
        if isinstance(result, str):
            # Development mode - show the link
            flash(f'Account created! Verify your email: {result}', 'info')
        else:
            flash('Account created! Please check your email to verify your account.', 'success')
        
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    if current_user.is_authenticated and current_user.email_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('main.index'))
    
    verification_token = EmailVerificationToken.query.filter_by(token=token).first()
    
    if not verification_token or not verification_token.is_valid():
        logger.warning(f"Invalid verification token used")
        flash('Invalid or expired verification link', 'error')
        return redirect(url_for('auth.login'))
    
    user = verification_token.user
    user.email_verified = True
    verification_token.used = True
    db.session.commit()
    
    logger.info(f"Email verified for user: {user.username}")
    flash('Email verified successfully! You can now log in.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if user and not user.email_verified:
            # Invalidate old tokens
            EmailVerificationToken.query.filter_by(user_id=user.id, used=False).update({'used': True})
            
            # Create new token
            token = secrets.token_urlsafe(32)
            verification_token = EmailVerificationToken(
                user_id=user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            db.session.add(verification_token)
            db.session.commit()
            
            from mail import send_verification_email
            result = send_verification_email(user, token)
            
            if isinstance(result, str):
                flash(f'Verification link: {result}', 'info')
            else:
                flash('Verification email sent! Check your inbox.', 'success')
        else:
            flash('If that email is registered and unverified, a new verification link has been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/resend_verification.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Rate limit by IP
    ip = get_client_ip()
    allowed, remaining = check_rate_limit(f'login:{ip}', max_requests=10, window_seconds=300)
    if not allowed:
        logger.warning(f"Login rate limited for IP: {ip}")
        flash(f'Too many login attempts. Please try again in {remaining} seconds.', 'error')
        return render_template('auth/login.html')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template('auth/login.html')

        user = User.query.filter(
            (User.username == username) | (User.email == username.lower())
        ).first()

        if user and user.check_password(password):
            # Check if email is verified (skip for admin users)
            if not user.email_verified and not user.is_admin:
                flash('Please verify your email before logging in. Check your inbox or request a new verification link.', 'warning')
                return redirect(url_for('auth.resend_verification'))
            
            login_user(user, remember=remember)
            logger.info(f"User logged in: {user.username} from IP: {ip}")
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            logger.warning(f"Failed login attempt for username: {username} from IP: {ip}")
            flash('Invalid username or password', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    ip = get_client_ip()
    allowed, remaining = check_rate_limit(f'forgot:{ip}', max_requests=3, window_seconds=3600)
    if not allowed:
        logger.warning(f"Password reset rate limited for IP: {ip}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': False, 'error': f'Too many requests. Please try again in {remaining // 60} minutes.'}
        flash(f'Too many requests. Please try again in {remaining // 60} minutes.', 'error')
        return render_template('auth/forgot_password.html')

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not email:
            if is_ajax:
                return {'success': False, 'error': 'Please enter your email address'}
            flash('Please enter your email address', 'error')
            return render_template('auth/forgot_password.html')

        user = User.query.filter_by(email=email).first()
        
        if user:
            PasswordResetToken.query.filter_by(user_id=user.id, used=False).update({'used': True})
            
            token = secrets.token_urlsafe(32)
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            db.session.add(reset_token)
            db.session.commit()
            
            logger.info(f"Password reset token created for user: {user.username} ({email})")
            
            from mail import send_password_reset_email
            result = send_password_reset_email(user, token)
            
            if is_ajax:
                return {'success': True}
            
            if isinstance(result, str):
                flash(f'Password reset link: {result}', 'info')
            else:
                flash('If that email is registered, a reset link has been sent.', 'info')
        else:
            logger.info(f"Password reset requested for non-existent email: {email}")
            if is_ajax:
                return {'success': True}
            flash('If that email is registered, a reset link has been sent.', 'info')
        
        if is_ajax:
            return {'success': True}
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Rate limit by IP
    ip = get_client_ip()
    allowed, remaining = check_rate_limit(f'reset:{ip}', max_requests=5, window_seconds=300)
    if not allowed:
        logger.warning(f"Password reset submit rate limited for IP: {ip}")
        flash(f'Too many attempts. Please try again in {remaining} seconds.', 'error')
        return redirect(url_for('auth.forgot_password'))

    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    
    if not reset_token or not reset_token.is_valid():
        logger.warning(f"Invalid password reset token used from IP: {ip}")
        flash('Invalid or expired reset link', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        valid, password_result = validate_password(password)
        if not valid:
            flash(password_result, 'error')
            return render_template('auth/reset_password.html', token=token)

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/reset_password.html', token=token)

        # Update password
        username = reset_token.user.username
        reset_token.user.set_password(password)
        reset_token.used = True
        db.session.commit()
        
        logger.info(f"Password reset successful for user: {username}")

        flash('Password updated successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)
