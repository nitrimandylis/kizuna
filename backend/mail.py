"""
Email utilities for Kizuna Platform
"""
import logging
from flask import current_app, render_template, url_for
from flask_mail import Mail, Message

mail = Mail()
logger = logging.getLogger(__name__)


def init_mail(app):
    """Initialize Flask-Mail with the application."""
    mail.init_app(app)


def send_password_reset_email(user, token):
    """Send password reset link to user."""
    if not current_app.config.get('MAIL_SERVER') or current_app.config['MAIL_SERVER'] == 'localhost':
        # Development mode - just log the reset URL
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        logger.info(f"Password reset for {user.email}: {reset_url}")
        return reset_url
    
    try:
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        msg = Message(
            subject='Reset Your Password - Kizuna',
            recipients=[user.email],
            html=render_template('emails/reset_password.html',
                               user=user, reset_url=reset_url),
            text=render_template('emails/reset_password.txt',
                               user=user, reset_url=reset_url)
        )
        
        mail.send(msg)
        logger.info(f"Password reset email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        return False


def send_event_registration_email(user, event):
    """Send event registration confirmation email."""
    event_url = url_for('events.detail', event_id=event.id, _external=True)
    
    if not current_app.config.get('MAIL_SERVER') or current_app.config['MAIL_SERVER'] == 'localhost':
        logger.info(f"Event registration: {user.email} for '{event.title}' - {event_url}")
        return True
    
    try:
        msg = Message(
            subject=f'Registration Confirmed: {event.title} - Kizuna',
            recipients=[user.email],
            html=render_template('emails/event_registration.html',
                               user=user, event=event, 
                               event_url=event_url),
            text=render_template('emails/event_registration.txt',
                               user=user, event=event,
                               event_url=event_url)
        )
        
        mail.send(msg)
        logger.info(f"Event registration email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send event registration email: {e}")
        return False
