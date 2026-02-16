import re
from html import escape
from markupsafe import Markup

def sanitize_input(text, max_length=None):
    """Sanitize user input to prevent XSS"""
    if not text:
        return ''
    
    # Strip whitespace
    text = text.strip()
    
    # Escape HTML entities
    text = escape(text)
    
    # Enforce max length
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

def validate_email(email):
    """Validate email format"""
    if not email:
        return False, "Email is required"
    
    email = email.strip().lower()
    
    if len(email) > 120:
        return False, "Email is too long"
    
    # Simple email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, email

def validate_username(username):
    """Validate username format"""
    if not username:
        return False, "Username is required"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 80:
        return False, "Username is too long"
    
    # Allow alphanumeric, underscore, hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, username

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if len(password) > 128:
        return False, "Password is too long"
    
    return True, "Password is valid"

def validate_title(title, max_length=200):
    """Validate title/heading fields"""
    if not title:
        return False, "Title is required"
    
    title = title.strip()
    
    if len(title) < 2:
        return False, "Title is too short"
    
    if len(title) > max_length:
        return False, f"Title must be less than {max_length} characters"
    
    return True, sanitize_input(title, max_length)

def validate_description(description, max_length=5000):
    """Validate description/text fields"""
    if not description:
        return True, ""  # Description is often optional
    
    description = description.strip()
    
    if len(description) > max_length:
        return False, f"Description must be less than {max_length} characters"
    
    return True, sanitize_input(description, max_length)

def validate_cas_type(cas_type):
    """Validate CAS type"""
    valid_types = ['Creativity', 'Activity', 'Service']
    
    if not cas_type:
        return False, "CAS type is required"
    
    if cas_type not in valid_types:
        return False, "Invalid CAS type"
    
    return True, cas_type

def validate_integer(value, field_name="Value", min_val=None, max_val=None):
    """Validate integer input"""
    if not value:
        return True, None  # Optional field
    
    try:
        value = int(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a number"
    
    if min_val is not None and value < min_val:
        return False, f"{field_name} must be at least {min_val}"
    
    if max_val is not None and value > max_val:
        return False, f"{field_name} must be at most {max_val}"
    
    return True, value

def validate_url(url, max_length=500):
    """Validate URL format"""
    if not url:
        return True, ""  # Optional
    
    url = url.strip()
    
    if len(url) > max_length:
        return False, f"URL is too long"
    
    # Basic URL validation
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url, re.IGNORECASE):
        return False, "Invalid URL format"
    
    return True, url

# Simple in-memory rate limiting (use Redis in production)
_rate_limit_store = {}

def check_rate_limit(key, max_requests=5, window_seconds=300):
    """
    Check if a rate limit has been exceeded.
    Returns (allowed, remaining_seconds)
    
    Args:
        key: Unique identifier (e.g., IP address or username)
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
    """
    import time
    
    current_time = time.time()
    window_start = current_time - window_seconds
    
    # Clean old entries
    if key in _rate_limit_store:
        _rate_limit_store[key] = [
            timestamp for timestamp in _rate_limit_store[key]
            if timestamp > window_start
        ]
    else:
        _rate_limit_store[key] = []
    
    # Check if limit exceeded
    if len(_rate_limit_store[key]) >= max_requests:
        oldest = min(_rate_limit_store[key])
        remaining = int(oldest + window_seconds - current_time)
        return False, max(0, remaining)
    
    # Record this request
    _rate_limit_store[key].append(current_time)
    return True, 0


def get_client_ip():
    """Get client IP address from request"""
    from flask import request
    
    # Check for X-Forwarded-For header (behind proxy)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    
    return request.remote_addr
