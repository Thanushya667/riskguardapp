import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))


class Config:
    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'riskguard-academic-intelligence-secret-2026'
    )

    # Dual database support: PostgreSQL if specified, fallback to SQLite
    db_url = os.getenv(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'academic_risk.db')}"
    )

    if db_url.startswith("postgres://"):
        db_url = db_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SMTP Configuration
    SMTP_HOST = os.getenv('SMTP_HOST', '')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SENDER_EMAIL = os.getenv(
        'SENDER_EMAIL',
        os.getenv('SMTP_USERNAME', '')
    )
    SMTP_USE_TLS = os.getenv(
        'SMTP_USE_TLS',
        'True'
    ).lower() in ('true', '1', 't')

    # Google Classroom API Configuration
    GOOGLE_CLIENT_ID = os.getenv(
        'GOOGLE_CLIENT_ID',
        ''
    )

    GOOGLE_CLIENT_SECRET = os.getenv(
        'GOOGLE_CLIENT_SECRET',
        ''
    )

    GOOGLE_REDIRECT_URI = os.getenv(
        'GOOGLE_REDIRECT_URI',
        'http://127.0.0.1:5000/api/google-classroom/oauth2callback'
    )

    # Application settings
    STATIC_FOLDER = os.path.join(
        PROJECT_ROOT,
        'frontend',
        'static'
    )

    TEMPLATE_FOLDER = os.path.join(
        PROJECT_ROOT,
        'frontend'
    )