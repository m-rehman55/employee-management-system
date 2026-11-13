"""Administrative operations that must not be exposed to ordinary users."""
from flask import Blueprint, redirect, url_for, flash, send_file, abort
from pathlib import Path
from utils.decorators import login_required, role_required
from utils.audit import log_audit
from utils.backup import create_sqlite_backup, sqlite_database_path

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


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
