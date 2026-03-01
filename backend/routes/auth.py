import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from datetime import datetime, timedelta
from utils import check_rate_limit, get_client_ip

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
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
