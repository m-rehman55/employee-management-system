"""
utils/decorators.py - Authentication and Role Authorization decorators.
Enforces session security for protected endpoints.
"""
from functools import wraps
from flask import session, flash, redirect, url_for, request

def login_required(f):
    """Ensures that a user session exists before accessing the view."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first to access this resource.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Ensures that the logged-in user possesses one of the allowed roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first to access this resource.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            user_role = session.get('role_name', '')
            if user_role not in allowed_roles:
                flash(f'Access restricted. Requires one of: {", ".join(allowed_roles)}', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

