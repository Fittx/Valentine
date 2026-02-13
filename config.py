import os


class Config:
    """Database configuration"""

    # MySQL Database Configuration
    # Update these with your SQL Workbench connection details
    DB_HOST = 'localhost'
    DB_PORT = 3306
    DB_USER = 'root'  # Change to your MySQL username
    DB_PASSWORD = '1234'  # Change to your MySQL password
    DB_NAME = 'valentine_db'

    # Flask secret key
    SECRET_KEY = 'your-secret-key-here-change-in-production'

    # MySQL connection string
    @staticmethod
    def get_db_uri():
        return f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"