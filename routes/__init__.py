"""
routes/__init__.py - Exports all blueprints for registration in the Flask app.
"""
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.employee_routes import employee_bp
from routes.department_routes import department_bp
from routes.leave_routes import leave_bp
from routes.attendance_routes import attendance_bp
from routes.payroll_routes import payroll_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'employee_bp',
    'department_bp',
    'leave_bp',
    'attendance_bp',
    'payroll_bp',
]

