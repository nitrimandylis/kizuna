"""
Logging configuration for Kizuna Platform
"""
import os
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from datetime import datetime


def setup_logging(app):
    """Configure logging for the Flask application."""
    
    # Set log level based on environment
    log_level = logging.DEBUG if app.debug else logging.INFO
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # File handler for all logs
    file_handler = RotatingFileHandler(
        'logs/kizuna.log',
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # Error-only file handler
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Email handler for production errors
    if not app.debug and app.config.get('MAIL_SERVER'):
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['MAIL_DEFAULT_SENDER'],
            toaddrs=[app.config['MAIL_USERNAME']],
            subject='Kizuna Application Error',
            credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']) if app.config['MAIL_USERNAME'] else None,
            secure=() if app.config['MAIL_USE_TLS'] else None
        )
        mail_handler.setLevel(logging.ERROR)
        root_logger.addHandler(mail_handler)
    
    # Set werkzeug logging (Flask development server)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name):
    """Get a logger with the given name."""
    return logging.getLogger(name)


class RequestLogger:
    """Context manager for logging requests."""
    
    def __init__(self, logger, request):
        self.logger = logger
        self.request = request
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.info(
            f"Request started: {self.request.method} {self.request.path} "
            f"from {self.request.remote_addr}"
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds() * 1000
        
        if exc_type:
            self.logger.error(
                f"Request failed: {self.request.method} {self.request.path} "
                f"({duration:.2f}ms) - {exc_type.__name__}: {exc_val}"
            )
        else:
            self.logger.info(
                f"Request completed: {self.request.method} {self.request.path} "
                f"({duration:.2f}ms)"
            )
        
        return False  # Don't suppress exceptions
