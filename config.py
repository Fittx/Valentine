import os


class Config:
    """Database configuration"""
    
    # SQLite Database Configuration (works on free hosting!)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'valentine.db')
    
    # Flask secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'valentine-day-secret-key-change-in-production-2026'