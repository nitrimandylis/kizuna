# Kizuna Platform

A community platform for IBDP students to coordinate CAS experiences, clubs, and events.

## Tech Stack

- **Backend:** Flask, SQLAlchemy, Flask-Login
- **Database:** PostgreSQL (Supabase)
- **Frontend:** Jinja2 templates, CSS, JavaScript
- **Deployment:** Render

## Project Structure

```
kizuna/
├── app.py              # Flask app factory
├── wsgi.py             # WSGI entry point for production
├── config.py           # Configuration settings
├── models.py           # Database models
├── utils.py            # Utility functions
├── mail.py             # Email utilities
├── logger.py           # Logging configuration
├── routes/             # Route blueprints
│   ├── auth.py         # Authentication routes
│   ├── events.py       # Event routes
│   ├── clubs.py        # Club routes
│   ├── profile.py      # User profile routes
│   ├── admin.py        # Admin routes
│   └── main.py         # Main routes
├── templates/          # Jinja2 templates
├── static/             # CSS, JS, images
├── migrations/         # Database migrations
├── requirements.txt    # Python dependencies
└── render.yaml         # Render deployment config
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run database migrations
flask db upgrade

# Start development server
python app.py
```

Visit http://localhost:5001

## Deployment

### Render + Supabase

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

## License

Kizuna Initiative - CGS Athens
