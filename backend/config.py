import os
from datetime import timedelta
from urllib.parse import urlparse


def get_database_url():
    """
    Get database URL from environment, handling PostgreSQL URL conversion.
    Heroku/Render use postgres:// which needs to be postgresql:// for SQLAlchemy.
    """
    database_url = os.getenv('DATABASE_URL', 'sqlite:///kizuna.db')
    
    # Convert postgres:// to postgresql:// for SQLAlchemy compatibility
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    return database_url


def get_bool_env(key, default=False):
    """Get boolean value from environment variable."""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')


def get_int_env(key, default):
    """Get integer value from environment variable."""
    try:
        return int(os.getenv(key, default))
    except (ValueError, TypeError):
        return default


class Config:
    """Base configuration with environment variable support"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = get_bool_env('DEBUG', False)
    TESTING = False
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Session security
    SESSION_COOKIE_SECURE = get_bool_env('SESSION_COOKIE_SECURE', False)
    SESSION_COOKIE_HTTPONLY = get_bool_env('SESSION_COOKIE_HTTPONLY', True)
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=get_int_env('SESSION_LIFETIME_HOURS', 168)  # 7 days default
    )
    
    # Rate limiting
    RATE_LIMIT_ENABLED = get_bool_env('RATE_LIMIT_ENABLED', True)
    RATE_LIMIT_PER_MINUTE = get_int_env('RATE_LIMIT_PER_MINUTE', 5)
    RATE_LIMIT_PER_HOUR = get_int_env('RATE_LIMIT_PER_HOUR', 20)
    
    # Admin settings
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', None)  # Must be set for first admin
    
    # Email settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT = get_int_env('MAIL_PORT', 25)
    MAIL_USE_TLS = get_bool_env('MAIL_USE_TLS', False)
    MAIL_USE_SSL = get_bool_env('MAIL_USE_SSL', False)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@kizuna.local')
    
    # Application settings
    APP_NAME = os.getenv('APP_NAME', 'Kizuna')
    APP_URL = os.getenv('APP_URL', 'http://localhost:5001')
    
    # Security settings
    PASSWORD_MIN_LENGTH = get_int_env('PASSWORD_MIN_LENGTH', 8)
    MAX_LOGIN_ATTEMPTS = get_int_env('MAX_LOGIN_ATTEMPTS', 5)
    LOGIN_LOCKOUT_DURATION = get_int_env('LOGIN_LOCKOUT_DURATION', 300)  # seconds
    
    # Pagination
    EVENTS_PER_PAGE = get_int_env('EVENTS_PER_PAGE', 10)
    CLUBS_PER_PAGE = get_int_env('CLUBS_PER_PAGE', 12)
    USERS_PER_PAGE = get_int_env('USERS_PER_PAGE', 20)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
    # Relaxed security for development
    SESSION_COOKIE_SECURE = False
    RATE_LIMIT_ENABLED = get_bool_env('RATE_LIMIT_ENABLED', False)


class ProductionConfig(Config):
    """Production configuration with strict security"""
    DEBUG = False
    TESTING = False
    
    # Strict session security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Force HTTPS
    PREFERRED_URL_SCHEME = 'https'
    
    # Production database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': get_int_env('DB_POOL_SIZE', 10),
        'max_overflow': get_int_env('DB_MAX_OVERFLOW', 20),
    }


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    RATE_LIMIT_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
