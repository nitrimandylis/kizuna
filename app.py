import os
import logging
from flask import Flask, session
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from config import config
from models import db

login_manager = LoginManager()
csrf = CSRFProtect()
talisman = Talisman()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure Talisman for security headers
    # Only enable strict HTTPS in production
    if config_name == 'production':
        talisman.init_app(
            app,
            force_https=True,
            strict_transport_security=True,
            strict_transport_security_preload=True,
            strict_transport_security_max_age=31536000,
            content_security_policy={
                'default-src': "'self'",
                'script-src': ["'self'", "'unsafe-inline'"],
                'style-src': ["'self'", "'unsafe-inline'"],
                'img-src': ["'self'", 'data:', 'https:'],
                'font-src': ["'self'"],
                'connect-src': ["'self'"],
            },
            referrer_policy='strict-origin-when-cross-origin',
            feature_policy={
                'geolocation': "'none'",
                'microphone': "'none'",
                'camera': "'none'",
            }
        )
    else:
        # Development mode - relaxed security
        talisman.init_app(
            app,
            force_https=False,
            content_security_policy=None,
        )
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    login_manager.refresh_view = 'auth.login'
    login_manager.needs_refresh_message = 'Session expired. Please log in again.'
    login_manager.needs_refresh_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # Session security enhancements
    @app.before_request
    def make_session_permanent():
        """Ensure session is marked as permanent for timeout control"""
        from flask import request
        if request.endpoint and not request.endpoint.startswith('static'):
            session.permanent = True
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.clubs import clubs_bp
    from routes.events import events_bp
    from routes.admin import admin_bp
    from routes.newsletter import newsletter_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(clubs_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(newsletter_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
