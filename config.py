"""
config.py - Application configuration settings for Employee Management System.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ems-university-secret-key-2026-cse601330')
    
    # Render & local database URI handling
    _raw_db_url = os.environ.get('DATABASE_URL')
    if _raw_db_url and _raw_db_url.startswith('postgres://'):
        _raw_db_url = _raw_db_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = _raw_db_url or f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'ems.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session & Cookie security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds

class TestConfig(Config):
    """Configuration for automated test suite."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

