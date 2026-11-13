"""
models/department.py - Department Management models (7 models).
Handles departments, physical branch locations, fiscal budgets, policies, projects, designations, and transfer logs.
"""
from datetime import datetime, date
from extensions import db
from utils.time import utc_now


class DepartmentLocation(db.Model):
    """Physical office branch or building location for a department."""
    __tablename__ = 'department_locations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(100), nullable=False)
    floor = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False, default='Pakistan')
    postal_code = db.Column(db.String(20), nullable=True)

    departments = db.relationship('Department', back_populates='location', lazy=True)

    def __repr__(self):
        return f"<DepartmentLocation {self.name} - {self.city}>"


class Department(db.Model):
    """Core department master record."""
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id', use_alter=True, name='fk_department_manager'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('department_locations.id'), nullable=True)
    budget = db.Column(db.Numeric(12, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    location = db.relationship('DepartmentLocation', back_populates='departments')
    employees = db.relationship('Employee', foreign_keys='Employee.department_id', back_populates='department', lazy=True)
    manager = db.relationship('Employee', foreign_keys=[manager_id], post_update=True)
    budgets = db.relationship('DepartmentBudget', back_populates='department', cascade='all, delete-orphan', lazy=True)
    policies = db.relationship('DepartmentPolicy', back_populates='department', cascade='all, delete-orphan', lazy=True)
    projects = db.relationship('DepartmentProject', back_populates='department', cascade='all, delete-orphan', lazy=True)
    designations = db.relationship('Designation', back_populates='department', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<Department {self.code} - {self.name}>"


class DepartmentBudget(db.Model):
    """Annual fiscal budget allocations and expenditures per department."""
    __tablename__ = 'department_budgets'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)
    allocated_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    spent_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    remaining_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    approved_date = db.Column(db.Date, default=date.today)

    department = db.relationship('Department', back_populates='budgets')

    def __repr__(self):
        return f"<DepartmentBudget Dept:{self.department_id} FY:{self.fiscal_year}>"


class DepartmentPolicy(db.Model):
    """Standard operating rules and guidelines defined for a department."""
    __tablename__ = 'department_policies'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    policy_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    effective_date = db.Column(db.Date, default=date.today)
    is_active = db.Column(db.Boolean, default=True)

    department = db.relationship('Department', back_populates='policies')

    def __repr__(self):
        return f"<DepartmentPolicy {self.policy_code} - {self.title}>"


class DepartmentProject(db.Model):
    """Operational project assigned to and managed by a department."""
    __tablename__ = 'department_projects'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    project_name = db.Column(db.String(150), nullable=False)
    project_code = db.Column(db.String(50), unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default='In Progress')  # In Progress, Completed, On Hold

    department = db.relationship('Department', back_populates='projects')

    def __repr__(self):
        return f"<DepartmentProject {self.project_code} - {self.project_name}>"


class Designation(db.Model):
    """Job titles and positions tied to specific departments."""
    __tablename__ = 'designations'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    job_code = db.Column(db.String(50), unique=True, nullable=False)
    min_salary = db.Column(db.Numeric(10, 2), default=0.00)
    max_salary = db.Column(db.Numeric(10, 2), default=0.00)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    department = db.relationship('Department', back_populates='designations')
    employees = db.relationship('Employee', back_populates='designation', lazy=True)

    def __repr__(self):
        return f"<Designation {self.job_code} - {self.title}>"


class DepartmentTransferHistory(db.Model):
    """Audit log of employee reassignments between departments."""
    __tablename__ = 'department_transfers'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    from_department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    to_department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    transfer_date = db.Column(db.Date, default=date.today)
    reason = db.Column(db.Text, nullable=False)
    approved_by = db.Column(db.String(100), nullable=False)

    employee = db.relationship('Employee', foreign_keys=[employee_id])
    from_department = db.relationship('Department', foreign_keys=[from_department_id])
    to_department = db.relationship('Department', foreign_keys=[to_department_id])

    def __repr__(self):
        return f"<DepartmentTransfer Emp:{self.employee_id} Dept:{self.from_department_id}->{self.to_department_id}>"

