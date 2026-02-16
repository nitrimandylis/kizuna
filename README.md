# Kizuna Platform

A community platform for IBDP students to coordinate CAS experiences, clubs, and events.

## Project Structure

```
kizuna/
├── backend/                # Python backend
│   ├── app.py              # Flask app factory
│   ├── config.py           # Configuration settings
│   ├── models.py           # Database models
│   ├── utils.py            # Utility functions
│   ├── mail.py             # Email utilities
│   ├── logger.py           # Logging configuration
│   ├── routes/             # Route blueprints
│   │   ├── auth.py         # Authentication
│   │   ├── events.py       # Events
│   │   ├── clubs.py        # Clubs
│   │   ├── profile.py      # User profiles
│   │   ├── admin.py        # Admin panel
│   │   ├── main.py         # Main routes
│   │   └── newsletter.py   # Newsletter
│   └── migrations/         # Database migrations
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS, JS, images
├── wsgi.py                 # WSGI entry point
├── requirements.txt        # Python dependencies
└── render.yaml             # Render deployment config
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run database migrations
cd backend && flask db upgrade && cd ..

# Start development server
python wsgi.py
```

Visit http://localhost:5001

## Deployment (Render + Supabase)

1. Create a Supabase project and get the database connection string
2. Push this repo to GitHub
3. Create a new Web Service on Render (connect GitHub repo)
4. Set environment variables:
   - `DATABASE_URL` - Supabase connection string
   - `SECRET_KEY` - Random secret key
5. Deploy!

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Flask secret key for sessions |
| `MAIL_SERVER` | SMTP server (optional) |
| `MAIL_USERNAME` | SMTP username (optional) |
| `MAIL_PASSWORD` | SMTP password (optional) |

## Tech Stack

- **Backend:** Flask, SQLAlchemy, Flask-Login
- **Database:** PostgreSQL (Supabase)
- **Frontend:** Jinja2 templates, CSS, JavaScript
- **Deployment:** Render

---

Kizuna Initiative - CGS Athens
