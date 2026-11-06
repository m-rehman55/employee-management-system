"""
routes/employee_routes.py - Employee Management Blueprint.
Provides full CRUD operations, server-side validation, relational updates, and PRG pattern.
"""
from datetime import datetime, date
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.employee import (
    Employee, EmployeeProfile, EmployeeEmergencyContact, EmployeeEducation,
    EmployeeExperience, EmployeeBankDetail, EmployeeSkill, EmployeeNote, EmployeeAssetAssignment
)
from models.department import Department, Designation
from utils.decorators import login_required
from utils.validators import validate_email, validate_date
from utils.audit import log_audit

employee_bp = Blueprint('employees', __name__, url_prefix='/employees')

@employee_bp.route('/', methods=['GET'])
@login_required
def list_employees():
    """READ: Lists all employees with search and department filtering."""
    search = request.args.get('search', '').strip()
    dept_id = request.args.get('dept_id', '')

    query = Employee.query

    if search:
        query = query.filter(
            (Employee.first_name.ilike(f'%{search}%')) |
            (Employee.last_name.ilike(f'%{search}%')) |
            (Employee.employee_code.ilike(f'%{search}%')) |
            (Employee.email.ilike(f'%{search}%'))
        )
    if dept_id and dept_id.isdigit():
        query = query.filter(Employee.department_id == int(dept_id))

    employees = query.order_by(Employee.id.desc()).all()
    departments = Department.query.order_by(Department.name).all()

    return render_template(
        'employees/list.html',
        employees=employees,
        departments=departments,
        search=search,
        selected_dept_id=dept_id
    )


@employee_bp.route('/<int:id>', methods=['GET'])
@login_required
def detail(id):
    """READ: Displays comprehensive employee profile and relational records."""
    employee = Employee.query.get_or_404(id)
    return render_template('employees/detail.html', employee=employee)


@employee_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """CREATE: Adds a new employee with server-side validation."""
    departments = Department.query.filter_by(is_active=True).all()
    designations = Designation.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        # Form field extraction
        employee_code = request.form.get('employee_code', '').strip().upper()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        dob_str = request.form.get('date_of_birth', '').strip()
        gender = request.form.get('gender', '').strip()
        hire_date_str = request.form.get('hire_date', '').strip()
        dept_id = request.form.get('department_id')
        desig_id = request.form.get('designation_id')
        employment_type = request.form.get('employment_type', 'Full-Time').strip()
        status = request.form.get('status', 'Active').strip()

        # Extended profile fields
        national_id = request.form.get('national_id', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        current_address = request.form.get('current_address', '').strip()
        bank_name = request.form.get('bank_name', '').strip()
        account_number = request.form.get('account_number', '').strip()

        # Server-side validations
        errors = []
        if not employee_code:
            errors.append("Employee Code is required.")
        elif Employee.query.filter_by(employee_code=employee_code).first():
            errors.append(f"Employee Code '{employee_code}' already exists.")

        if not first_name or not last_name:
            errors.append("Both First Name and Last Name are required.")

        valid_email, email_err = validate_email(email)
        if not valid_email:
            errors.append(email_err)
        elif Employee.query.filter_by(email=email).first():
            errors.append(f"Email '{email}' is already registered to another employee.")

        if not phone:
            errors.append("Phone number is required.")

        valid_dob, dob, dob_err = validate_date(dob_str, "Date of Birth")
        if not valid_dob:
            errors.append(dob_err)

        valid_hire, hire_date, hire_err = validate_date(hire_date_str, "Hire Date")
        if not valid_hire:
            errors.append(hire_err)

        if not gender:
            errors.append("Gender selection is required.")

        # Foreign Key validation
        department = Department.query.get(dept_id) if (dept_id and dept_id.isdigit()) else None
        designation = Designation.query.get(desig_id) if (desig_id and desig_id.isdigit()) else None

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'employees/form.html',
                action='Add',
                employee=None,
                form_data=request.form,
                departments=departments,
                designations=designations
            )

        # Database Insertion
        new_emp = Employee(
            employee_code=employee_code,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            date_of_birth=dob,
            gender=gender,
            hire_date=hire_date,
            department_id=department.id if department else None,
            designation_id=designation.id if designation else None,
            employment_type=employment_type,
            status=status
        )
        db.session.add(new_emp)
        db.session.flush()

        # Create Profile
        new_profile = EmployeeProfile(
            employee_id=new_emp.id,
            national_id=national_id,
            blood_group=blood_group,
            current_address=current_address
        )
        db.session.add(new_profile)

        # Create Bank Detail if entered
        if bank_name and account_number:
            new_bank = EmployeeBankDetail(
                employee_id=new_emp.id,
                bank_name=bank_name,
                branch_name='Main Branch',
                account_number=account_number,
                account_holder_name=new_emp.full_name,
                is_primary=True
            )
            db.session.add(new_bank)

        db.session.commit()
        log_audit('CREATE', 'Employee', new_emp.id, f"Created employee {new_emp.employee_code} ({new_emp.full_name})")

        flash(f"Employee {new_emp.full_name} ({new_emp.employee_code}) was successfully created!", 'success')
        return redirect(url_for('employees.detail', id=new_emp.id))

    return render_template(
        'employees/form.html',
        action='Add',
        employee=None,
        form_data={},
        departments=departments,
        designations=designations
    )


@employee_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """UPDATE: Edits existing employee record."""
    employee = Employee.query.get_or_404(id)
    departments = Department.query.filter_by(is_active=True).all()
    designations = Designation.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        dob_str = request.form.get('date_of_birth', '').strip()
        gender = request.form.get('gender', '').strip()
        hire_date_str = request.form.get('hire_date', '').strip()
        dept_id = request.form.get('department_id')
        desig_id = request.form.get('designation_id')
        employment_type = request.form.get('employment_type', 'Full-Time').strip()
        status = request.form.get('status', 'Active').strip()

        # Server-side validation
        errors = []
        if not first_name or not last_name:
            errors.append("First Name and Last Name cannot be empty.")

        valid_email, email_err = validate_email(email)
        if not valid_email:
            errors.append(email_err)
        else:
            existing = Employee.query.filter_by(email=email).first()
            if existing and existing.id != employee.id:
                errors.append(f"Email '{email}' is already in use by another employee.")

        if not phone:
            errors.append("Phone number is required.")

        valid_dob, dob, dob_err = validate_date(dob_str, "Date of Birth")
        if not valid_dob:
            errors.append(dob_err)

        valid_hire, hire_date, hire_err = validate_date(hire_date_str, "Hire Date")
        if not valid_hire:
            errors.append(hire_err)

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'employees/form.html',
                action='Edit',
                employee=employee,
                form_data=request.form,
                departments=departments,
                designations=designations
            )

        # Apply updates
        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email
        employee.phone = phone
        employee.date_of_birth = dob
        employee.gender = gender
        employee.hire_date = hire_date
        employee.department_id = int(dept_id) if (dept_id and dept_id.isdigit()) else None
        employee.designation_id = int(desig_id) if (desig_id and desig_id.isdigit()) else None
        employee.employment_type = employment_type
        employee.status = status

        # Update profile if existing
        if employee.profile:
            employee.profile.national_id = request.form.get('national_id', '').strip()
            employee.profile.blood_group = request.form.get('blood_group', '').strip()
            employee.profile.current_address = request.form.get('current_address', '').strip()

        db.session.commit()
        log_audit('UPDATE', 'Employee', employee.id, f"Updated profile for employee {employee.employee_code}")

        flash(f"Employee {employee.full_name} was updated successfully!", 'success')
        return redirect(url_for('employees.detail', id=employee.id))

    return render_template(
        'employees/form.html',
        action='Edit',
        employee=employee,
        form_data={},
        departments=departments,
        designations=designations
    )


@employee_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """DELETE: Safely removes an employee record after confirmation."""
    employee = Employee.query.get_or_404(id)
    emp_code = employee.employee_code
    emp_name = employee.full_name

    # Unlink any User account attached to this employee
    if employee.user:
        employee.user.employee_id = None

    # Clear department manager reference if this employee manages any department
    managed_depts = Department.query.filter_by(manager_id=employee.id).all()
    for d in managed_depts:
        d.manager_id = None

    # Clean up dependent records across modules
    from models.leave import LeaveApproval, LeaveEncashment
    from models.department import DepartmentTransferHistory
    from models.attendance import AttendanceCorrectionRequest, OvertimeRecord, AttendanceSummary, EmployeeShiftSchedule
    from models.payroll import EmployeeDeduction, EmployeeBonus

    LeaveApproval.query.filter_by(approver_id=employee.id).update({'approver_id': None})
    LeaveEncashment.query.filter_by(employee_id=employee.id).delete()
    DepartmentTransferHistory.query.filter_by(employee_id=employee.id).delete()
    AttendanceCorrectionRequest.query.filter_by(employee_id=employee.id).delete()
    OvertimeRecord.query.filter_by(employee_id=employee.id).delete()
    AttendanceSummary.query.filter_by(employee_id=employee.id).delete()
    EmployeeShiftSchedule.query.filter_by(employee_id=employee.id).delete()
    EmployeeDeduction.query.filter_by(employee_id=employee.id).delete()
    EmployeeBonus.query.filter_by(employee_id=employee.id).delete()

    db.session.delete(employee)
    db.session.commit()

    log_audit('DELETE', 'Employee', id, f"Deleted employee {emp_code} ({emp_name})")
    flash(f"Employee {emp_name} ({emp_code}) was successfully deleted.", 'info')
    return redirect(url_for('employees.list_employees'))

