"""
extensions.py - Initializes shared Flask extensions.
Keeps extensions decoupled from the application instance to prevent circular imports.
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy ORM instance
db = SQLAlchemy()

