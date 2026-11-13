"""
app.py - Main Entry Point for the Employee Management System.
Flask Application Factory with database initialization, blueprints, and error handlers.
"""
import os
from flask import Flask, render_template, request, session
from config import Config
from extensions import db
from utils.csrf import csrf_token, validate_csrf_request
import models  # Ensures all SQLAlchemy models are registered
from routes import (
    auth_bp,
    dashboard_bp,
    employee_bp,
    department_bp,
    leave_bp,
    attendance_bp,
    payroll_bp,
    admin_bp
)


def create_app(config_class=Config):
    """Application factory for the Employee Management System."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance directory exists for SQLite database
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    app.jinja_env.globals['csrf_token'] = csrf_token

    @app.before_request
    def protect_state_changing_requests():
        if app.config.get('CSRF_ENABLED', True) and request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            validate_csrf_request()

    # Register Blueprints for the 5 core modules + Auth + Dashboard
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(leave_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(payroll_bp)
    app.register_blueprint(admin_bp)

    # Global context processor for templates
    @app.context_processor
    def inject_global_data():
        theme_cookie = request.cookies.get('app_theme')
        theme_override = theme_cookie if theme_cookie in {'light', 'dark'} else 'auto'
        return {
            'app_theme': theme_override,
            'current_user_name': session.get('employee_name', session.get('username')),
            'current_role': session.get('role_name'),
            'is_logged_in': 'user_id' in session
        }

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_code=404, error_message="The requested resource or page was not found."), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('base.html', error_code=403, error_message="You do not have permission to view this resource."), 403

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('base.html', error_code=400, error_message=str(getattr(e, 'description', 'Invalid request.'))), 400

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_code=500, error_message="An internal server error occurred."), 500

    return app


# Application instance for WSGI / CLI / Production (Gunicorn)
app = create_app()

with app.app_context():
    # Ensure all tables exist in the database
    db.create_all()
    # Auto-seed initial enterprise records if empty (e.g. fresh Render deployment)
    try:
        from models.auth import User
        if not User.query.filter_by(username='admin').first():
            from seed import create_seed_data
            create_seed_data(app)
    except Exception as e:
        print(f"Database initialization note: {e}")

if __name__ == '__main__':
    print("==================================================")
    print(" Employee Management System is running!")
    print(" Local URL: http://127.0.0.1:5000")
    print(" Login credentials:")
    print("   Admin:      admin / admin123")
    print("   HR Manager: hr_manager / manager123")
    print("   Employee:   employee / user123")
    print("==================================================")
    app.run(debug=True, host='127.0.0.1', port=5000)

