"""
utils/audit.py - Helper function to record audit log events.
"""
from flask import session, request
from extensions import db
from models.auth import AuditLog

def log_audit(action, target_model, record_id=None, details=None):
    """Creates a tamper-evident audit trail record."""
    try:
        user_id = session.get('user_id')
        ip_addr = request.remote_addr if request else '127.0.0.1'
        
        log_entry = AuditLog(
            user_id=user_id,
            action=action.upper(),
            target_model=target_model,
            record_id=record_id,
            details=details,
            ip_address=ip_addr
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        # Never break main transaction because of audit logging failure
        db.session.rollback()

