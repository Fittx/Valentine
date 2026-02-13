import os


class Config:
    """Database configuration for PostgreSQL"""

    # PostgreSQL configuration (for Render.com)
    DATABASE_URL = os.environ.get('DATABASE_URL', '')

    # Parse DATABASE_URL if it exists (Render provides this)
    if DATABASE_URL:
        # Extract individual components from DATABASE_URL if needed
        # But we'll use DATABASE_URL directly in app.py
        DB_HOST = os.environ.get('PGHOST', 'localhost')
        DB_PORT = int(os.environ.get('PGPORT', 5432))
        DB_USER = os.environ.get('PGUSER', 'postgres')
        DB_PASSWORD = os.environ.get('PGPASSWORD', '')
        DB_NAME = os.environ.get('PGDATABASE', 'postgres')  # Changed default from valentine_db to postgres
    else:
        # Local development fallback
        DB_HOST = 'localhost'
        DB_PORT = 5432
        DB_USER = 'postgres'
        DB_PASSWORD = ''
        DB_NAME = 'valentine_db'

    # Flask secret key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production-please')