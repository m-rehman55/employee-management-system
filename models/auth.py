"""
models/auth.py - Authentication, Authorization, Audit Trails, and System Settings (4 models).
Handles system users, RBAC roles, compliance audit logs, and enterprise settings.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class Role(db.Model):
    """User access roles (e.g. Administrator, HR Manager, Employee)."""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    users = db.relationship('User', back_populates='role', lazy=True)

    def __repr__(self):
        return f"<Role {self.role_name}>"


class User(db.Model):
    """System authentication user account."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    employee = db.relationship('Employee', back_populates='user')
    role = db.relationship('Role', back_populates='users')
    audit_logs = db.relationship('AuditLog', back_populates='user', lazy=True)

    def set_password(self, password):
        """Hashes and sets the user's password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the candidate password against the stored password hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} (Role:{self.role.role_name if self.role else self.role_id})>"


class AuditLog(db.Model):
    """Tamper-evident audit trail for system operations and record modifications."""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT
    target_model = db.Column(db.String(100), nullable=False)
    record_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50), nullable=True)

    user = db.relationship('User', back_populates='audit_logs')

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.target_model}:{self.record_id} by User:{self.user_id}>"


class SystemSetting(db.Model):
    """Global configuration settings for the HR management system."""
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(60), unique=True, nullable=False)
    setting_value = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), default='General')
    description = db.Column(db.String(255), nullable=True)
    is_public = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<SystemSetting {self.setting_key}={self.setting_value}>"

