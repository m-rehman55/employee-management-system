"""
tests/test_persistence.py - Tests database persistence across application restarts.
"""
import os
import sys

# Ensure root workspace directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import date
from decimal import Decimal
from flask import Flask
from config import Config
from extensions import db
import models
from models import Department, Employee

TEST_DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_persist.db')

def create_persist_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{TEST_DB_PATH}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def test_database_persistence_across_restarts():
    """Verifies that data persists on disk when the application is stopped and restarted."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    # 1. Session 1: Create DB and insert records
    app1 = create_persist_app()
    with app1.app_context():
        db.create_all()
        dept = Department(code='DEPT-PERSIST', name='Persistent Department', budget=Decimal('350000.00'), is_active=True)
        db.session.add(dept)
        db.session.flush()

        emp = Employee(
            employee_code='EMP-PERSIST-1',
            first_name='Farhan',
            last_name='Saeed',
            email='farhan.saeed@apex.local',
            phone='+92-300-8889900',
            date_of_birth=date(1992, 8, 20),
            gender='Male',
            hire_date=date(2025, 3, 1),
            department_id=dept.id
        )
        db.session.add(emp)
        db.session.commit()
        db.session.remove()
        db.engine.dispose()

    # 2. Simulate complete application shutdown
    del app1

    # Verify physical file existence
    assert os.path.exists(TEST_DB_PATH), "Database file must physically exist on disk"

    # 3. Session 2: Launch completely new application instance connecting to existing DB
    app2 = create_persist_app()
    with app2.app_context():
        # Query existing records
        saved_dept = Department.query.filter_by(code='DEPT-PERSIST').first()
        assert saved_dept is not None, "Department must persist in database across app restarts"
        assert saved_dept.name == 'Persistent Department'
        assert saved_dept.budget == Decimal('350000.00')

        saved_emp = Employee.query.filter_by(employee_code='EMP-PERSIST-1').first()
        assert saved_emp is not None, "Employee must persist across app restarts"
        assert saved_emp.full_name == 'Farhan Saeed'
        # Verify relationship persistence
        assert saved_emp.department is not None
        assert saved_emp.department.code == 'DEPT-PERSIST'

        db.session.remove()
        db.engine.dispose()

    # Clean up test file
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
