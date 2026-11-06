"""
routes/auth_routes.py - Authentication and Session Management Blueprint.
Handles login, logout, session establishment, cookie demonstration, and PRG redirects.
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from extensions import db
from models.auth import User
from utils.audit import log_audit

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login with session initialization and cookie usage."""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember_me') == 'on'

        # Server-side validation
        if not username or not password:
            flash('Both username and password are required.', 'danger')
            return render_template('auth/login.html', username=username)

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'warning')
                return render_template('auth/login.html', username=username)

            # Establish Session State
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['role_name'] = user.role.role_name if user.role else 'Employee'
            session['employee_id'] = user.employee_id
            session['employee_name'] = user.employee.full_name if user.employee else user.username
            session.permanent = True if remember_me else False

            # Update last login timestamp
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Record audit log
            log_audit('LOGIN', 'User', user.id, f"User '{user.username}' logged in successfully.")

            flash(f'Welcome back, {session["employee_name"]}!', 'success')

            # Post/Redirect/Get Pattern to prevent form resubmission
            next_page = request.args.get('next')
            response = make_response(redirect(next_page if next_page else url_for('dashboard.index')))

            # Demonstrate appropriate cookie usage (remember username for convenience; never store passwords)
            if remember_me:
                response.set_cookie('saved_username', username, max_age=30*24*60*60, httponly=True, samesite='Lax')
            else:
                response.delete_cookie('saved_username')

            return response
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('auth/login.html', username=username)

    # GET request - read cookie for convenience if available
    saved_username = request.cookies.get('saved_username', '')
    return render_template('auth/login.html', saved_username=saved_username)


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logs the user out, cleans the session, and logs the event."""
    username = session.get('username', 'Anonymous')
    user_id = session.get('user_id')

    if user_id:
        log_audit('LOGOUT', 'User', user_id, f"User '{username}' logged out.")

    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

