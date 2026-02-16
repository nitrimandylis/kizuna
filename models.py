from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('EventRegistration', backref='user', lazy=True, cascade='all, delete-orphan')
    newsletter_subscription = db.relationship('NewsletterSubscription', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class EmailVerificationToken(db.Model):
    __tablename__ = 'email_verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='verification_tokens')
    
    def is_valid(self):
        return not self.used and datetime.utcnow() < self.expires_at


class Club(db.Model):
    __tablename__ = 'clubs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    meeting_day = db.Column(db.String(20))
    meeting_time = db.Column(db.String(10))
    meeting_location = db.Column(db.String(120))
    leader_name = db.Column(db.String(120))
    leader_email = db.Column(db.String(120))
    website_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    events = db.relationship('Event', backref='club', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Club {self.name}>'


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    cas_type = db.Column(db.String(50), nullable=False)  # Creativity, Activity, Service
    event_date = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    max_capacity = db.Column(db.Integer)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'))
    organizer_name = db.Column(db.String(120))
    organizer_email = db.Column(db.String(120))
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    registrations = db.relationship('EventRegistration', backref='event', lazy=True, cascade='all, delete-orphan')

    def is_full(self):
        if not self.max_capacity:
            return False
        return self.get_registered_count() >= self.max_capacity

    def get_registered_count(self):
        return EventRegistration.query.filter_by(event_id=self.id, status='confirmed').count()

    def __repr__(self):
        return f'<Event {self.title}>'


class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='confirmed')  # confirmed, cancelled, attended
    hours_contributed = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<EventRegistration {self.full_name} - {self.event_id}>'


class NewsletterSubscription(db.Model):
    __tablename__ = 'newsletter_subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<NewsletterSubscription {self.user_id}>'


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='reset_tokens')
    
    def is_valid(self):
        return not self.used and datetime.utcnow() < self.expires_at
