"""
tests/test_system.py - Comprehensive automated verification test suite.
Validates all 45 SQLAlchemy models, authentication, sessions, cookies,
flash messages, error handling, database persistence, and complete CRUD across all 5 modules.
"""
import os
import sys
import re

# Ensure root workspace directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import date, datetime
from decimal import Decimal
from flask import session
from app import create_app
from config import TestConfig
from extensions import db
import models
from models import (
    Role, User, Department, Designation, DepartmentLocation,
    Employee, EmployeeProfile,
    LeaveType, LeaveRequest, LeaveBalance,
    WorkShift, AttendanceRecord,
    PayrollPeriod, PayrollRecord
)

@pytest.fixture
def app_instance():
    """Provides a cleanly initialized Flask app instance with SQLite in-memory database."""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        # Seed core roles
        role_admin = Role(role_name='Administrator', description='Admin role')
        role_emp = Role(role_name='Employee', description='Employee role')
        db.session.add_all([role_admin, role_emp])
        db.session.flush()

        # Seed admin user
        admin = User(username='testadmin', role_id=role_admin.id, is_active=True)
        admin.set_password('adminpass123')
        db.session.add(admin)

        # Seed base department
        loc = DepartmentLocation(name='HQ', building='Main', address='Street 1', city='Islamabad', state='Federal')
        db.session.add(loc)
        db.session.flush()

        dept = Department(code='DEPT-TEST', name='Test Department', location_id=loc.id, budget=Decimal('100000.00'), is_active=True)
        db.session.add(dept)
        db.session.flush()

        # Seed base designation
        desig = Designation(department_id=dept.id, title='Software Engineer', job_code='SE-TEST')
        db.session.add(desig)

        # Seed base leave type
        lt = LeaveType(name='Annual Leave', code='AL', default_days_per_year=14)
        db.session.add(lt)

        # Seed base shift
        shift = WorkShift(shift_name='General Shift', shift_code='GS-01')
        db.session.add(shift)

        # Seed base payroll period
        period = PayrollPeriod(
            period_name='November 2026', period_month=11, period_year=2026,
            start_date=date(2026, 11, 1), end_date=date(2026, 11, 30), status='Draft'
        )
        db.session.add(period)

        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app_instance):
    """Provides a test client."""
    return app_instance.test_client()

@pytest.fixture
def auth_client(app_instance, client):
    """Provides an authenticated client with active session."""
    with client:
        client.post('/login', data={'username': 'testadmin', 'password': 'adminpass123', 'remember_me': 'on'}, follow_redirects=True)
        yield client


# ==============================================================================
# 1. MODEL COUNT VERIFICATION TEST (Minimum 40 Required)
# ==============================================================================
def test_forty_models_requirement(app_instance):
    """Verifies that at least 40 genuine SQLAlchemy models/tables exist."""
    with app_instance.app_context():
        table_count = len(db.metadata.tables)
        print(f"\n[TEST REPORT] Total Registered Tables: {table_count}")
        assert table_count >= 40, f"Expected >= 40 models, but found {table_count}"


# ==============================================================================
# 2. AUTHENTICATION, SESSIONS, COOKIES & PRG TESTS
# ==============================================================================
def test_unauthenticated_access_redirect(client):
    """Tests that protected routes redirect unauthenticated users to /login."""
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_employee_role_cannot_mutate_records(client):
    """Read access does not grant write/delete access to an employee account."""
    with client.session_transaction() as session_data:
        session_data['user_id'] = 999
        session_data['role_name'] = 'Employee'

    response = client.get('/employees/add', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/dashboard')


def test_employee_self_service_cannot_read_other_records(client, app_instance):
    """Employee read access is restricted to the signed-in employee's records."""
    with app_instance.app_context():
        first = Employee(
            employee_code='EMP-SELF', first_name='Self', last_name='User',
            email='self@example.com', phone='03000000001',
            date_of_birth=date(1990, 1, 1), gender='Other'
        )
        second = Employee(
            employee_code='EMP-OTHER', first_name='Other', last_name='User',
            email='other@example.com', phone='03000000002',
            date_of_birth=date(1990, 1, 2), gender='Other'
        )
        db.session.add_all([first, second])
        db.session.flush()
        record = PayrollRecord(
            employee_id=second.id, payroll_period_id=1,
            basic_salary=1000, total_allowances=0, gross_salary=1000,
            total_deductions=0, net_salary=1000, payment_status='Unpaid'
        )
        db.session.add(record)
        db.session.commit()
        other_id = second.id
        payroll_id = record.id

    with client.session_transaction() as session_data:
        session_data['user_id'] = 1001
        session_data['role_name'] = 'Employee'
        session_data['employee_id'] = 1

    employee_list = client.get('/employees/')
    assert b'Other User' not in employee_list.data
    payroll_list = client.get('/payroll/')
    assert b'Other User' not in payroll_list.data
    assert client.get(f'/employees/{other_id}').status_code == 403
    assert client.get(f'/payroll/{payroll_id}').status_code == 403


def test_login_invalid_credentials(client):
    """Tests server-side validation error handling on invalid credentials."""
    response = client.post('/login', data={'username': 'wronguser', 'password': 'badpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


def test_login_does_not_expose_demo_credentials(client):
    """Login UI must not print development usernames or passwords."""
    response = client.get('/login')
    assert b'admin123' not in response.data
    assert b'manager123' not in response.data
    assert b'user123' not in response.data


def test_default_theme_follows_system_preference(client):
    """Without a user override, the rendered shell remains system-controlled."""
    response = client.get('/login')
    assert b'<body class="theme-auto">' in response.data


def test_login_success_and_cookie_demonstration(client):
    """Tests successful login, session establishment, PRG pattern, and cookie creation."""
    response = client.post(
        '/login',
        data={'username': 'testadmin', 'password': 'adminpass123', 'remember_me': 'on'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Executive Dashboard' in response.data
    # Verify cookie was set
    cookie = client.get_cookie('saved_username')
    assert cookie is not None
    assert cookie.value == 'testadmin'


def test_login_rejects_external_next_redirect(client):
    """A login redirect must stay on this application."""
    response = client.post(
        '/login?next=https://evil.example/phishing',
        data={'username': 'testadmin', 'password': 'adminpass123'},
        follow_redirects=False
    )
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/dashboard')


def test_password_reset_is_single_use(client, app_instance):
    """Development reset flow changes the password and rejects token reuse."""
    response = client.post('/forgot-password', data={'identity': 'testadmin'}, follow_redirects=True)
    assert response.status_code == 200
    match = re.search(rb'/reset-password/([^\s<]+)', response.data)
    assert match is not None
    token = match.group(1).decode()

    reset = client.post(
        f'/reset-password/{token}',
        data={'password': 'newsecurepass123', 'confirmation': 'newsecurepass123'},
        follow_redirects=True
    )
    assert b'Password updated successfully' in reset.data
    reused = client.get(f'/reset-password/{token}', follow_redirects=True)
    assert b'invalid or has expired' in reused.data

def test_logout(auth_client):
    """Tests logout clears the session."""
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data
    # Trying to visit dashboard now should redirect
    dash_resp = auth_client.get('/dashboard', follow_redirects=False)
    assert dash_resp.status_code == 302


def test_toggle_theme(auth_client):
    """Tests theme toggle endpoint sets and flips the app_theme cookie without 500 error."""
    # First toggle: defaults from light to dark
    resp = auth_client.get('/toggle-theme', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Executive Dashboard' in resp.data
    cookie = auth_client.get_cookie('app_theme')
    assert cookie is not None
    assert cookie.value == 'dark'

    # Second toggle: flips back to light
    resp2 = auth_client.get('/toggle-theme', follow_redirects=True)
    assert resp2.status_code == 200
    cookie2 = auth_client.get_cookie('app_theme')
    assert cookie2.value == 'light'


def test_toggle_theme_rejects_external_referrer(auth_client):
    """A theme toggle must not redirect to an external referrer."""
    response = auth_client.get(
        '/toggle-theme',
        headers={'Referer': 'https://evil.example/phishing'},
        follow_redirects=False
    )
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/dashboard')


# ==============================================================================
# 3. DEPARTMENT CRUD TESTS
# ==============================================================================
def test_department_crud(auth_client, app_instance):
    """Full CRUD lifecycle test for Department Management."""
    # CREATE
    post_data = {
        'code': 'DEPT-ENG',
        'name': 'Engineering & R&D',
        'description': 'Software architecture and development',
        'budget': '5000000',
        'is_active': 'on'
    }
    create_resp = auth_client.post('/departments/add', data=post_data, follow_redirects=True)
    assert create_resp.status_code == 200
    assert b'Engineering &amp; R&amp;D' in create_resp.data

    with app_instance.app_context():
        dept = Department.query.filter_by(code='DEPT-ENG').first()
        assert dept is not None
        dept_id = dept.id

    # READ list and detail
    list_resp = auth_client.get('/departments/')
    assert b'DEPT-ENG' in list_resp.data

    detail_resp = auth_client.get(f'/departments/{dept_id}')
    assert b'Engineering &amp; R&amp;D' in detail_resp.data

    # UPDATE
    edit_data = {
        'name': 'Engineering & AI Research',
        'description': 'Advanced artificial intelligence and engineering',
        'budget': '7500000',
        'is_active': 'on'
    }
    edit_resp = auth_client.post(f'/departments/{dept_id}/edit', data=edit_data, follow_redirects=True)
    assert edit_resp.status_code == 200
    assert b'Engineering &amp; AI Research' in edit_resp.data

    # DELETE
    del_resp = auth_client.post(f'/departments/{dept_id}/delete', follow_redirects=True)
    assert del_resp.status_code == 200

    with app_instance.app_context():
        assert db.session.get(Department, dept_id) is None


# ==============================================================================
# 4. EMPLOYEE CRUD & VALIDATION TESTS
# ==============================================================================
def test_employee_crud(auth_client, app_instance):
    """Full CRUD lifecycle and server-side validation test for Employee Management."""
    with app_instance.app_context():
        dept = Department.query.first()
        desig = Designation.query.first()
        dept_id = dept.id
        desig_id = desig.id

    # CREATE
    emp_data = {
        'employee_code': 'EMP-TEST-01',
        'first_name': 'Ali',
        'last_name': 'Raza',
        'email': 'ali.raza@apex.local',
        'phone': '+92-300-5554433',
        'date_of_birth': '1995-05-15',
        'gender': 'Male',
        'hire_date': '2025-01-10',
        'department_id': str(dept_id),
        'designation_id': str(desig_id),
        'employment_type': 'Full-Time',
        'status': 'Active',
        'national_id': '61101-9988776-1',
        'blood_group': 'B+',
        'current_address': 'Sector F-8, Islamabad',
        'bank_name': 'HBL Bank',
        'account_number': 'PK12HABB000999888'
    }
    create_resp = auth_client.post('/employees/add', data=emp_data, follow_redirects=True)
    assert create_resp.status_code == 200
    assert b'Ali Raza' in create_resp.data

    with app_instance.app_context():
        emp = Employee.query.filter_by(employee_code='EMP-TEST-01').first()
        assert emp is not None
        assert emp.profile is not None
        assert emp.profile.national_id == '61101-9988776-1'
        emp_id = emp.id

    # READ list and detail
    list_resp = auth_client.get('/employees/')
    assert b'EMP-TEST-01' in list_resp.data

    detail_resp = auth_client.get(f'/employees/{emp_id}')
    assert b'Ali Raza' in detail_resp.data
    assert b'HBL Bank' in detail_resp.data

    # UPDATE
    update_data = {
        'first_name': 'Ali',
        'last_name': 'Raza Khan',
        'email': 'ali.razakhan@apex.local',
        'phone': '+92-300-5554433',
        'date_of_birth': '1995-05-15',
        'gender': 'Male',
        'hire_date': '2025-01-10',
        'department_id': str(dept_id),
        'designation_id': str(desig_id),
        'employment_type': 'Full-Time',
        'status': 'Active',
        'national_id': '61101-9988776-1',
        'blood_group': 'B+'
    }
    edit_resp = auth_client.post(f'/employees/{emp_id}/edit', data=update_data, follow_redirects=True)
    assert edit_resp.status_code == 200
    assert b'Ali Raza Khan' in edit_resp.data

    # DELETE
    del_resp = auth_client.post(f'/employees/{emp_id}/delete', follow_redirects=True)
    assert del_resp.status_code == 200

    with app_instance.app_context():
        deactivated = db.session.get(Employee, emp_id)
        assert deactivated is not None
        assert deactivated.status == 'Inactive'

    restore_resp = auth_client.post(f'/employees/{emp_id}/restore', follow_redirects=True)
    assert restore_resp.status_code == 200
    with app_instance.app_context():
        assert db.session.get(Employee, emp_id).status == 'Active'


def test_employee_validation_duplicate_code(auth_client, app_instance):
    """Tests server-side validation error on duplicate employee code."""
    with app_instance.app_context():
        dept = Department.query.first()
        emp1 = Employee(
            employee_code='EMP-DUP-1', first_name='Test', last_name='User',
            email='test.user1@apex.local', phone='1234', date_of_birth=date(1990, 1, 1),
            gender='Male', hire_date=date(2025, 1, 1), department_id=dept.id
        )
        db.session.add(emp1)
        db.session.commit()

    # Attempt to add another employee with duplicate code
    bad_data = {
        'employee_code': 'EMP-DUP-1',
        'first_name': 'Another',
        'last_name': 'User',
        'email': 'different.email@apex.local',
        'phone': '5678',
        'date_of_birth': '1992-02-02',
        'gender': 'Female',
        'hire_date': '2025-02-02'
    }
    resp = auth_client.post('/employees/add', data=bad_data, follow_redirects=True)
    assert resp.status_code == 200
    assert b"already exists" in resp.data


# ==============================================================================
# 5. LEAVE CRUD TESTS
# ==============================================================================
def test_leave_crud(auth_client, app_instance):
    """Full CRUD lifecycle test for Leave Management."""
    with app_instance.app_context():
        dept = Department.query.first()
        emp = Employee(
            employee_code='EMP-LV-1', first_name='Sara', last_name='Ahmed',
            email='sara.ahmed@apex.local', phone='1234567', date_of_birth=date(1993, 3, 3),
            gender='Female', hire_date=date(2024, 1, 1), department_id=dept.id
        )
        db.session.add(emp)
        db.session.commit()
        emp_id = emp.id
        lt_id = LeaveType.query.first().id

    # CREATE
    leave_data = {
        'employee_id': str(emp_id),
        'leave_type_id': str(lt_id),
        'start_date': '2026-11-15',
        'end_date': '2026-11-17',
        'reason': 'Medical recovery and doctor consultation',
        'status': 'Pending'
    }
    create_resp = auth_client.post('/leaves/add', data=leave_data, follow_redirects=True)
    assert create_resp.status_code == 200

    with app_instance.app_context():
        leave = LeaveRequest.query.filter_by(employee_id=emp_id).first()
        assert leave is not None
        assert leave.total_days == Decimal('3.0')
        leave_id = leave.id

    # READ list and detail
    list_resp = auth_client.get('/leaves/')
    assert b'Sara Ahmed' in list_resp.data

    detail_resp = auth_client.get(f'/leaves/{leave_id}')
    assert b'Medical recovery' in detail_resp.data

    # UPDATE request details without changing its status
    update_data = {
        'start_date': '2026-11-15',
        'end_date': '2026-11-17',
        'reason': 'Medical recovery and doctor consultation',
    }
    edit_resp = auth_client.post(f'/leaves/{leave_id}/edit', data=update_data, follow_redirects=True)
    assert edit_resp.status_code == 200

    # APPROVE through the dedicated decision workflow
    decision_resp = auth_client.post(
        f'/leaves/{leave_id}/decision',
        data={'decision': 'Approved', 'remarks': 'Approved by Department Head'},
        follow_redirects=True
    )
    assert decision_resp.status_code == 200

    with app_instance.app_context():
        updated_leave = db.session.get(LeaveRequest, leave_id)
        assert updated_leave.status == 'Approved'

    # DELETE
    del_resp = auth_client.post(f'/leaves/{leave_id}/delete', follow_redirects=True)
    assert del_resp.status_code == 200

    with app_instance.app_context():
        assert db.session.get(LeaveRequest, leave_id) is None


# ==============================================================================
# 6. ATTENDANCE CRUD TESTS
# ==============================================================================
def test_attendance_crud(auth_client, app_instance):
    """Full CRUD lifecycle test for Attendance Management."""
    with app_instance.app_context():
        dept = Department.query.first()
        emp = Employee(
            employee_code='EMP-ATT-1', first_name='Usman', last_name='Tariq',
            email='usman.tariq@apex.local', phone='987654', date_of_birth=date(1991, 1, 1),
            gender='Male', hire_date=date(2024, 1, 1), department_id=dept.id
        )
        db.session.add(emp)
        db.session.commit()
        emp_id = emp.id
        shift_id = WorkShift.query.first().id

    # CREATE
    att_data = {
        'employee_id': str(emp_id),
        'shift_id': str(shift_id),
        'work_date': '2026-11-05',
        'check_in_time': '09:00',
        'check_out_time': '17:30',
        'status': 'Present',
        'notes': 'Normal biometric check'
    }
    create_resp = auth_client.post('/attendance/add', data=att_data, follow_redirects=True)
    assert create_resp.status_code == 200

    with app_instance.app_context():
        rec = AttendanceRecord.query.filter_by(employee_id=emp_id).first()
        assert rec is not None
        assert rec.total_work_hours == Decimal('8.50')
        rec_id = rec.id

    # READ list and detail
    list_resp = auth_client.get('/attendance/')
    assert b'Usman Tariq' in list_resp.data

    detail_resp = auth_client.get(f'/attendance/{rec_id}')
    assert b'Normal biometric check' in detail_resp.data

    # UPDATE
    update_data = {
        'shift_id': str(shift_id),
        'check_in_time': '09:15',
        'check_out_time': '17:30',
        'status': 'Late',
        'notes': 'Traffic delay'
    }
    edit_resp = auth_client.post(f'/attendance/{rec_id}/edit', data=update_data, follow_redirects=True)
    assert edit_resp.status_code == 200

    with app_instance.app_context():
        updated_rec = db.session.get(AttendanceRecord, rec_id)
        assert updated_rec.status == 'Late'

    # DELETE
    del_resp = auth_client.post(f'/attendance/{rec_id}/delete', follow_redirects=True)
    assert del_resp.status_code == 200

    with app_instance.app_context():
        assert db.session.get(AttendanceRecord, rec_id) is None


# ==============================================================================
# 7. PAYROLL CRUD TESTS
# ==============================================================================
def test_payroll_crud(auth_client, app_instance):
    """Full CRUD lifecycle test for Payroll Management."""
    with app_instance.app_context():
        dept = Department.query.first()
        emp = Employee(
            employee_code='EMP-PAY-1', first_name='Khadija', last_name='Bibi',
            email='khadija.bibi@apex.local', phone='5551234', date_of_birth=date(1994, 4, 4),
            gender='Female', hire_date=date(2023, 1, 1), department_id=dept.id
        )
        db.session.add(emp)
        db.session.commit()
        emp_id = emp.id
        period_id = PayrollPeriod.query.first().id

    # CREATE
    pay_data = {
        'employee_id': str(emp_id),
        'payroll_period_id': str(period_id),
        'basic_salary': '100000',
        'total_allowances': '25000',
        'total_deductions': '10000',
        'payment_status': 'Paid',
        'payment_method': 'Bank Transfer',
        'payment_date': '2026-11-30'
    }
    create_resp = auth_client.post('/payroll/add', data=pay_data, follow_redirects=True)
    assert create_resp.status_code == 200

    with app_instance.app_context():
        rec = PayrollRecord.query.filter_by(employee_id=emp_id).first()
        assert rec is not None
        assert rec.gross_salary == Decimal('125000.00')
        assert rec.net_salary == Decimal('115000.00')
        rec_id = rec.id

    # READ list and detail
    list_resp = auth_client.get('/payroll/')
    assert b'Khadija Bibi' in list_resp.data

    detail_resp = auth_client.get(f'/payroll/{rec_id}')
    assert b'Official Salary Payslip' in detail_resp.data
    assert b'115,000.00' in detail_resp.data

    # UPDATE
    update_data = {
        'basic_salary': '110000',
        'total_allowances': '25000',
        'total_deductions': '10000',
        'payment_status': 'Paid',
        'payment_method': 'Bank Transfer',
        'payment_date': '2026-11-30'
    }
    edit_resp = auth_client.post(f'/payroll/{rec_id}/edit', data=update_data, follow_redirects=True)
    assert edit_resp.status_code == 200

    with app_instance.app_context():
        updated_rec = db.session.get(PayrollRecord, rec_id)
        assert updated_rec.net_salary == Decimal('125000.00')

    # DELETE
    del_resp = auth_client.post(f'/payroll/{rec_id}/delete', follow_redirects=True)
    assert del_resp.status_code == 200

    with app_instance.app_context():
        assert db.session.get(PayrollRecord, rec_id) is None


# ==============================================================================
# 8. ERROR HANDLER (404) TEST
# ==============================================================================
def test_404_error_handler(auth_client):
    """Tests custom 404 error template response on non-existent endpoints."""
    response = auth_client.get('/non_existent_page_route')
    assert response.status_code == 404
    assert b'404' in response.data
    assert b'not found' in response.data
