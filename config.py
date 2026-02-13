import os


class Config:
    """Database configuration for PostgreSQL"""

    # PostgreSQL configuration (for Render.com)
    # Render provides DATABASE_URL with auto-generated database name
    DATABASE_URL = os.environ.get('DATABASE_URL', '')

    # Local development fallback - individual components
    DB_HOST = os.environ.get('PGHOST', 'localhost')
    DB_PORT = int(os.environ.get('PGPORT', 5432))
    DB_USER = os.environ.get('PGUSER', 'postgres')
    DB_PASSWORD = os.environ.get('PGPASSWORD', '')
    DB_NAME = os.environ.get('PGDATABASE', 'valentine_db')

    # Flask secret key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production-please')