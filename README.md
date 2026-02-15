# 🎉 Kizuna Initiative Platform

## Overview
Kizuna Initiative is a comprehensive community hub platform designed for the IBDP student community at CGS Athens.

### Branding
- **Primary Color**: #fe4359 (Vibrant Red)
- **Secondary Color**: #1a1c37 (Deep Dark Blue)
- **Accent Color**: #00d9ff (Cyan)

## Features

### Public Features
- Home page with hero section & featured events
- About page for initiative information
- Clubs directory with details
- CAS Events system (Creativity/Activity/Service)
- Event filtering and search
- Event registration with capacity tracking
- Newsletter subscription

### User Features
- User registration & login
- Event registration/unregistration
- Newsletter management
- Secure session management

### Admin Features
- Admin dashboard with statistics
- Full event CRUD (Create, Read, Update, Delete)
- Participant tracking and management
- Attendance status updates
- Capacity monitoring
- Event publishing/unpublishing

## Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual environment

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kizuna-platform
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize database:
```bash
python << 'EOF'
from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    db.create_all()
    admin = User(email='admin@kizuna.local', username='admin', is_admin=True)
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print("✅ Database initialized! Ready to go!")
EOF
```

5. Run development server:
```bash
flask run
```

Visit http://localhost:5000

## Default Credentials
- Email: admin@kizuna.local
- Username: admin
- Password: admin123

⚠️ **IMPORTANT**: Change these credentials in production!

## Project Structure
```
kizuna-platform/
├── app.py              # Flask application factory
├── config.py           # Configuration management
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
├── .gitignore          # Git ignore rules
│
├── routes/             # Flask blueprints (6 modules)
│   ├── __init__.py
│   ├── auth.py         # Authentication routes
│   ├── main.py         # Home & About pages
│   ├── clubs.py        # Clubs directory
│   ├── events.py       # Events & registration
│   ├── admin.py        # Admin dashboard
│   └── newsletter.py   # Newsletter management
│
├── templates/          # HTML templates
│   ├── base.html       # Master layout
│   ├── home.html       # Home page
│   ├── about.html      # About page
│   ├── auth/           # Auth templates (login, register)
│   ├── clubs/          # Club templates (index, detail)
│   ├── events/         # Event templates (index, detail)
│   └── admin/          # Admin templates (dashboard, events)
│
├── static/             # Static assets
│   ├── css/
│   │   └── style.css   # Main CSS with Kizuna branding
│   ├── js/
│   │   └── main.js     # JavaScript utilities
│   └── images/
│       └── kizuna-logo.svg  # Logo files
│
├── docs/               # Documentation
│   └── FRONTEND_SUMMARY.md
│
└── instance/           # Database (auto-created)
    └── kizuna.db
```

## Database Models

### User
- id, username (unique), email (unique)
- password_hash, is_admin
- Relations: registrations, newsletter_subscription

### Club
- id, name, description, logo_url
- meeting_day, meeting_time, meeting_location
- leader_name, leader_email, website_url
- is_active, created_at, updated_at
- Relations: events

### Event
- id, title, description, cas_type
- event_date, end_time, location, max_capacity
- club_id, organizer_name, organizer_email
- is_published, created_at, updated_at
- Relations: registrations

### EventRegistration
- id, event_id, user_id
- full_name, email, phone, status
- hours_contributed, notes, registered_at

### NewsletterSubscription
- id, user_id, is_active, subscribed_at

## Routes

### Public Routes
- `GET /` - Home page
- `GET /about` - About page
- `GET /clubs/` - Browse clubs
- `GET /clubs/<id>` - Club details
- `GET /events/` - Browse events
- `GET /events/<id>` - Event details

### Authentication Routes
- `GET/POST /auth/register` - Register
- `GET/POST /auth/login` - Login
- `GET /auth/logout` - Logout

### User Routes (Logged In)
- `POST /events/<id>/register` - Register for event
- `POST /events/<id>/unregister` - Unregister
- `POST /newsletter/subscribe` - Subscribe
- `POST /newsletter/unsubscribe` - Unsubscribe

### Admin Routes (Admin Only)
- `GET /admin/` - Dashboard
- `GET /admin/events` - Event management
- `POST /admin/events/create` - Create event
- `POST /admin/events/<id>/delete` - Delete event

## Deployment

### Render.com
1. Push to GitHub
2. Create new Web Service on Render
3. Connect repository
4. Configure:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn 'app:create_app()'`
5. Set environment variables
6. Deploy!

## Documentation

Additional documentation available in `docs/` folder.

## Customization

### Logo Files
- `static/images/kizuna-logo.svg` - Main logo (used on home, auth pages)
- `static/images/kizuna-logo-small.svg` - Small logo (navbar, favicon)

### Change Colors
Edit `static/css/style.css`:
```css
:root {
    --kizuna-red: #fe4359;
    --kizuna-dark: #1a1c37;
    --kizuna-accent: #00d9ff;
}
```

### Add Sample Data
Create `seed_data.py` with Club and Event data, then run it.

## Security Features

✅ Password hashing with Werkzeug
✅ Session-based authentication  
✅ Admin role verification
✅ CSRF protection
✅ SQL injection prevention
✅ XSS prevention

## License

Kizuna Initiative - CGS Athens Community Hub

---

Built with ❤️ for connecting the IBDP community.
