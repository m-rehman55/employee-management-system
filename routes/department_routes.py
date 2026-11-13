"""
routes/department_routes.py - Department Management Blueprint.
Provides full CRUD operations, manager assignments, location linking, and PRG pattern.
"""
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.department import Department, DepartmentLocation, Designation, DepartmentBudget, DepartmentPolicy, DepartmentProject
from models.employee import Employee
from utils.decorators import login_required, role_required
from utils.validators import validate_numeric
from utils.audit import log_audit

department_bp = Blueprint('departments', __name__, url_prefix='/departments')

@department_bp.route('/', methods=['GET'])
@login_required
def list_departments():
    """READ: Displays all departments with metrics."""
    search = request.args.get('search', '').strip()
    query = Department.query

    if search:
        query = query.filter(
            (Department.name.ilike(f'%{search}%')) |
            (Department.code.ilike(f'%{search}%'))
        )

    departments = query.order_by(Department.name).all()
    return render_template('departments/list.html', departments=departments, search=search)


@department_bp.route('/<int:id>', methods=['GET'])
@login_required
def detail(id):
    """READ: Shows department profile, staff list, budget, policies, and active projects."""
    department = db.get_or_404(Department, id)
    return render_template('departments/detail.html', department=department)


@department_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Administrator', 'HR Manager')
def add():
    """CREATE: Adds a new department with server-side validation."""
    employees = Employee.query.filter_by(status='Active').all()
    locations = DepartmentLocation.query.all()

    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        manager_id = request.form.get('manager_id')
        location_id = request.form.get('location_id')
        budget_str = request.form.get('budget', '0').strip()
        is_active = request.form.get('is_active') == 'on'

        errors = []
        if not code:
            errors.append("Department Code is required.")
        elif Department.query.filter_by(code=code).first():
            errors.append(f"Department Code '{code}' already exists.")

        if not name:
            errors.append("Department Name is required.")

        valid_budget, budget_val, budget_err = validate_numeric(budget_str, "Department Budget", min_val=0)
        if not valid_budget:
            errors.append(budget_err)

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'departments/form.html',
                action='Add',
                department=None,
                form_data=request.form,
                employees=employees,
                locations=locations
            )

        new_dept = Department(
            code=code,
            name=name,
            description=description,
            manager_id=int(manager_id) if (manager_id and manager_id.isdigit()) else None,
            location_id=int(location_id) if (location_id and location_id.isdigit()) else None,
            budget=Decimal(str(budget_val)),
            is_active=is_active
        )
        db.session.add(new_dept)
        db.session.commit()

        log_audit('CREATE', 'Department', new_dept.id, f"Created department {new_dept.code} ({new_dept.name})")
        flash(f"Department '{new_dept.name}' was created successfully!", 'success')
        return redirect(url_for('departments.detail', id=new_dept.id))

    return render_template(
        'departments/form.html',
        action='Add',
        department=None,
        form_data={},
        employees=employees,
        locations=locations
    )


@department_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Administrator', 'HR Manager')
def edit(id):
    """UPDATE: Modifies existing department information."""
    department = db.get_or_404(Department, id)
    employees = Employee.query.filter_by(status='Active').all()
    locations = DepartmentLocation.query.all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        manager_id = request.form.get('manager_id')
        location_id = request.form.get('location_id')
        budget_str = request.form.get('budget', '0').strip()
        is_active = request.form.get('is_active') == 'on'

        errors = []
        if not name:
            errors.append("Department Name cannot be empty.")

        valid_budget, budget_val, budget_err = validate_numeric(budget_str, "Department Budget", min_val=0)
        if not valid_budget:
            errors.append(budget_err)

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'departments/form.html',
                action='Edit',
                department=department,
                form_data=request.form,
                employees=employees,
                locations=locations
            )

        department.name = name
        department.description = description
        department.manager_id = int(manager_id) if (manager_id and manager_id.isdigit()) else None
        department.location_id = int(location_id) if (location_id and location_id.isdigit()) else None
        department.budget = Decimal(str(budget_val))
        department.is_active = is_active

        db.session.commit()
        log_audit('UPDATE', 'Department', department.id, f"Updated department {department.code}")

        flash(f"Department '{department.name}' was updated successfully!", 'success')
        return redirect(url_for('departments.detail', id=department.id))

    return render_template(
        'departments/form.html',
        action='Edit',
        department=department,
        form_data={},
        employees=employees,
        locations=locations
    )


@department_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Administrator', 'HR Manager')
def delete(id):
    """DELETE: Safely removes department after checking constraints."""
    department = db.get_or_404(Department, id)
    dept_name = department.name

    # Check if department has assigned employees
    if department.employees:
        flash(f"Cannot delete department '{dept_name}' because it contains active employees. Please reassign them first.", 'warning')
        return redirect(url_for('departments.detail', id=id))

    db.session.delete(department)
    db.session.commit()

    log_audit('DELETE', 'Department', id, f"Deleted department '{dept_name}'")
    flash(f"Department '{dept_name}' has been successfully deleted.", 'info')
    return redirect(url_for('departments.list_departments'))

