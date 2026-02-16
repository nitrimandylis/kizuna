# Kizuna Initiative Platform

## Overview
Kizuna Initiative is a comprehensive community hub platform designed for the IBDP student community at CGS Athens.

### Branding
- Primary Color: #fe4359 (Vibrant Red)
- Secondary Color: #1a1c37 (Deep Dark Blue)

## Features

### Public Features
- Home page with hero section and featured events
- About page for initiative information
- Clubs directory with details
- CAS Events system (Creativity/Activity/Service)
- Event filtering and search
- Event registration with capacity tracking
- Newsletter subscription

### User Features
- User registration and login
- Event registration/unregistration
- Newsletter management
- Secure session management
- Password reset functionality

### Admin Features
- Admin dashboard with statistics
- Full event CRUD (Create, Read, Update, Delete)
- Club management CRUD
- User management
- Participant tracking and management
- Attendance status updates
- Capacity monitoring
- Event publishing/unpublishing

## Quick Start

### Prerequisites
- Python 3.11+
- pip
- Virtual environment
- PostgreSQL (for production)

### Installation

1. Clone the repository

2. Create virtual environment:
   python -m venv venv
   source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Set up environment variables:
   cp .env.example .env
   Edit .env with your configuration

5. Initialize database:
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade

6. Run development server:
   python app.py

Visit http://localhost:5001

## Database Migrations

This project uses Flask-Migrate for database migrations:

- Initialize: flask db init
- Create migration: flask db migrate -m "Description"
- Apply migrations: flask db upgrade
- Rollback: flask db downgrade

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection
- Rate limiting on auth routes
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy)
- XSS prevention
- Secure session cookies (production)
- Content Security Policy headers
- HSTS (HTTP Strict Transport Security)

## Deployment

### Docker
docker-compose up -d

### Render.com
1. Push to GitHub
2. Create new Web Service on Render
3. Connect repository
4. Set environment variables
5. Deploy!

### Heroku
1. heroku create kizuna-platform
2. heroku addons:create heroku-postgresql
3. git push heroku main

## License

Kizuna Initiative - CGS Athens Community Hub

---

Built for connecting the IBDP community.
