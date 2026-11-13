"""
config.py - Application configuration settings for Employee Management System.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _secret_key():
    secret = os.environ.get('SECRET_KEY')
    if secret:
        return secret
    if os.environ.get('APP_ENV', 'development').lower() == 'production':
        raise RuntimeError('SECRET_KEY must be set in production')
    return 'ems-development-only-secret-change-me'

class Config:
    """Base application configuration."""
    APP_ENV = os.environ.get('APP_ENV', 'development').lower()
    SECRET_KEY = _secret_key()
    
    # Render & local database URI handling
    _raw_db_url = os.environ.get('DATABASE_URL')
    if _raw_db_url and _raw_db_url.startswith('postgres://'):
        _raw_db_url = _raw_db_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = _raw_db_url or f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'ems.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session & Cookie security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = APP_ENV == 'production'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    RESET_LINK_LOGGING = APP_ENV != 'production'
    CSRF_ENABLED = True

class TestConfig(Config):
    """Configuration for automated test suite."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    CSRF_ENABLED = False

