import os
import logging
from flask import Flask, session, request, g, send_from_directory
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_compress import Compress
from config import config
from models import db
from logger import setup_logging

login_manager = LoginManager()
csrf = CSRFProtect()
talisman = Talisman()
compress = Compress()

# Create logger instance
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Get the project root directory (parent of backend)
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    app = Flask(__name__,
                template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))
    app.config.from_object(config[config_name])
    
    # Setup logging
    setup_logging(app)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    compress.init_app(app)
    
    # Initialize Flask-Mail
    from mail import init_mail
    init_mail(app)
    
    # Configure Talisman for security headers
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

    # Request logging
    @app.before_request
    def before_request():
        g.start_time = None
        if request.endpoint and not request.endpoint.startswith('static'):
            from time import time
            g.start_time = time()
            logger.debug(f"Request: {request.method} {request.path} from {request.remote_addr}")

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time') and g.start_time:
            from time import time
            duration = (time() - g.start_time) * 1000
            logger.debug(f"Response: {request.method} {request.path} -> {response.status_code} ({duration:.2f}ms)")
        
        if request.endpoint == 'static' or request.path.startswith('/static/'):
            max_age = 31536000 if config_name == 'production' else 3600
            response.cache_control.max_age = max_age
            response.cache_control.public = True
            response.headers['X-Content-Type-Options'] = 'nosniff'
        
        return response

    @app.before_request
    def make_session_permanent():
        if request.endpoint and not request.endpoint.startswith('static'):
            session.permanent = True
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.clubs import clubs_bp
    from routes.events import events_bp
    from routes.admin import admin_bp
    from routes.newsletter import newsletter_bp
    from routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(clubs_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(newsletter_bp)
    app.register_blueprint(profile_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        logger.warning(f"404 Not Found: {request.path}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        logger.error(f"500 Internal Error: {request.path} - {str(error)}")
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        logger.warning(f"403 Forbidden: {request.path}")
        return render_template('errors/403.html'), 403

    @app.errorhandler(Exception)
    def handle_exception(error):
        import traceback
        db.session.rollback()
        logger.error(f"Unhandled exception: {str(error)}\n{traceback.format_exc()}")
        from flask import render_template
        return render_template('errors/500.html'), 500

    # Create database tables and admin user
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Create admin user if not exists
            from models import User
            admin_username = os.getenv('ADMIN_USERNAME', 'admin')
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            
            admin = User.query.filter_by(username=admin_username).first()
            if not admin:
                admin = User(
                    username=admin_username,
                    email='admin@kizuna.com',
                    is_admin=True,
                    email_verified=True
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                logger.info(f"Admin user created: {admin_username}")
            else:
                logger.info("Admin user already exists")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")

    return app


# For production (gunicorn app:app)
app = create_app()


if __name__ == '__main__':
    app = create_app()
    logger.info("Starting development server on port 5001")
    app.run(debug=True, port=5001)
