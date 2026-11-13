"""Administrative operations that must not be exposed to ordinary users."""
from flask import Blueprint, redirect, url_for, flash, send_file, abort, render_template, session
from pathlib import Path
from utils.decorators import login_required, role_required
from utils.audit import log_audit
from utils.backup import create_sqlite_backup, sqlite_database_path
from models.auth import PasswordResetRequest, PasswordResetToken
from extensions import db
from utils.time import utc_now

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/password-resets', methods=['GET'])
@login_required
@role_required('Administrator')
def password_resets():
    requests = PasswordResetRequest.query.order_by(PasswordResetRequest.requested_at.desc()).all()
    return render_template('admin/password_resets.html', reset_requests=requests)


@admin_bp.route('/password-resets/<int:id>/approve', methods=['POST'])
@login_required
@role_required('Administrator')
def approve_password_reset(id):
    reset_request = db.get_or_404(PasswordResetRequest, id)
    if reset_request.status != 'Pending':
        flash('This password reset request has already been reviewed.', 'warning')
        return redirect(url_for('admin.password_resets'))
    PasswordResetToken.query.filter_by(user_id=reset_request.user_id, used_at=None).update({'used_at': utc_now()})
    reset, raw_token = PasswordResetToken.issue(reset_request.user)
    reset_request.status = 'Approved'
    reset_request.reviewed_at = utc_now()
    reset_request.reviewed_by = session.get('user_id')
    db.session.add(reset)
    db.session.commit()
    link = url_for('auth.reset_password', token=raw_token, _external=True)
    log_audit('APPROVE', 'PasswordResetRequest', id, f'Approved reset request for {reset_request.user.username}')
    return render_template('admin/password_resets.html', reset_requests=PasswordResetRequest.query.order_by(PasswordResetRequest.requested_at.desc()).all(), generated_link=link)


@admin_bp.route('/password-resets/<int:id>/reject', methods=['POST'])
@login_required
@role_required('Administrator')
def reject_password_reset(id):
    reset_request = db.get_or_404(PasswordResetRequest, id)
    if reset_request.status == 'Pending':
        reset_request.status = 'Rejected'
        reset_request.reviewed_at = utc_now()
        reset_request.reviewed_by = session.get('user_id')
        db.session.commit()
        log_audit('REJECT', 'PasswordResetRequest', id, f'Rejected reset request for {reset_request.user.username}')
    flash('Password reset request rejected.', 'info')
    return redirect(url_for('admin.password_resets'))


@admin_bp.route('/backup', methods=['POST'])
@login_required
@role_required('Administrator')
def backup():
    try:
        destination = create_sqlite_backup()
    except RuntimeError as exc:
        flash(str(exc), 'danger')
        return redirect(url_for('dashboard.index'))
    log_audit('BACKUP', 'Database', None, f'Created database backup {destination.name}')
    flash(f'Database backup created successfully: {destination.name}', 'success')
    return redirect(url_for('dashboard.index'))


@admin_bp.route('/backup/<path:filename>', methods=['GET'])
@login_required
@role_required('Administrator')
def download_backup(filename):
    backup_dir = sqlite_database_path().parent / 'backups'
    requested = (backup_dir / filename).resolve()
    if requested.parent != backup_dir.resolve() or not requested.is_file():
        abort(404)
    return send_file(requested, as_attachment=True, download_name=requested.name)
