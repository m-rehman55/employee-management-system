"""
routes/auth_routes.py - Authentication and Session Management Blueprint.
Handles login, logout, session establishment, cookie demonstration, and PRG redirects.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from extensions import db
from models.auth import User, PasswordResetRequest, PasswordResetToken
from utils.audit import log_audit
from utils.security import safe_local_url
from utils.time import utc_now

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
            user.last_login = utc_now()
            db.session.commit()

            # Record audit log
            log_audit('LOGIN', 'User', user.id, f"User '{user.username}' logged in successfully.")

            flash(f'Welcome back, {session["employee_name"]}!', 'success')

            # Post/Redirect/Get Pattern to prevent form resubmission
            next_page = safe_local_url(request.args.get('next'), url_for('dashboard.index'))
            response = make_response(redirect(next_page))

            # Never persist or prefill usernames. The checkbox only controls
            # the session lifetime, and any legacy username cookie is removed.
            response.delete_cookie('saved_username')

            return response
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('auth/login.html', username=username)

    return render_template('auth/login.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Start a password reset without revealing whether an account exists."""
    if request.method == 'POST':
        identity = request.form.get('identity', '').strip()
        user = User.query.filter_by(username=identity).first()

        if user and user.is_active:
            pending = PasswordResetRequest.query.filter_by(user_id=user.id, status='Pending').first()
            if not pending:
                db.session.add(PasswordResetRequest(user_id=user.id))
                db.session.commit()

        flash('If the account exists, a password reset request has been sent to an administrator for review.', 'info')
        return redirect(url_for('auth.forgot_password'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset = PasswordResetToken.find(token)
    if not reset:
        flash('This reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirmation = request.form.get('confirmation', '')
        if len(password) < 10:
            flash('Password must be at least 10 characters long.', 'danger')
        elif password != confirmation:
            flash('Passwords do not match.', 'danger')
        else:
            reset.user.set_password(password)
            reset.used_at = utc_now()
            db.session.commit()
            flash('Password updated successfully. You can now sign in.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    user = db.session.get(User, session['user_id'])
    if request.method == 'POST':
        current = request.form.get('current_password', '')
        password = request.form.get('password', '')
        confirmation = request.form.get('confirmation', '')
        if not user.check_password(current):
            flash('Current password is incorrect.', 'danger')
        elif len(password) < 10:
            flash('New password must be at least 10 characters long.', 'danger')
        elif password != confirmation:
            flash('New passwords do not match.', 'danger')
        else:
            user.set_password(password)
            db.session.commit()
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('dashboard.index'))
    return render_template('auth/change_password.html')


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

