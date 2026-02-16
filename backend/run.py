#!/usr/bin/env python
"""
Production entry point for Render
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check DATABASE_URL
database_url = os.getenv('DATABASE_URL', '')
if not database_url:
    print("ERROR: DATABASE_URL environment variable is not set!")
    sys.exit(1)

if database_url.startswith('http'):
    print(f"ERROR: DATABASE_URL looks like a web URL, not a database connection string!")
    print(f"Expected: postgresql://user:password@host/database")
    print(f"Got: {database_url[:50]}...")
    sys.exit(1)

# Run migrations
print("Running database migrations...")
os.system('flask db upgrade')

# Create app
from app import create_app
app = create_app()

# Run with gunicorn in production
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    
    # Use gunicorn if available, otherwise Flask dev server
    try:
        import gunicorn.app.base
        
        class StandaloneApplication(gunicorn.app.base.BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()
            
            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key.lower(), value)
            
            def load(self):
                return self.application
        
        options = {
            'bind': f'0.0.0.0:{port}',
            'workers': 1,
        }
        StandaloneApplication(app, options).run()
    except ImportError:
        app.run(host='0.0.0.0', port=port)
