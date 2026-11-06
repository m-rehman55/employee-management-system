"""
models/payroll.py - Payroll Management models (8 models).
Handles salary structures, components, employee salary packages, payroll periods, monthly payslips, payslip item details, deductions, and bonuses.
"""
from datetime import datetime, date
from extensions import db


class SalaryStructure(db.Model):
    """Graded salary pay bands (e.g. Grade A Senior Software Engineer)."""
    __tablename__ = 'salary_structures'

    id = db.Column(db.Integer, primary_key=True)
    structure_name = db.Column(db.String(100), nullable=False)
    grade_code = db.Column(db.String(20), unique=True, nullable=False)
    base_salary = db.Column(db.Numeric(10, 2), nullable=False, default=50000.00)
    min_salary = db.Column(db.Numeric(10, 2), default=40000.00)
    max_salary = db.Column(db.Numeric(10, 2), default=80000.00)
    description = db.Column(db.Text, nullable=True)

    employee_assignments = db.relationship('EmployeeSalaryAssignment', back_populates='structure', lazy=True)

    def __repr__(self):
        return f"<SalaryStructure {self.grade_code} - {self.structure_name}>"


class SalaryComponent(db.Model):
    """Component catalog of earnings and deductions."""
    __tablename__ = 'salary_components'

    id = db.Column(db.Integer, primary_key=True)
    component_name = db.Column(db.String(100), nullable=False)
    component_code = db.Column(db.String(30), unique=True, nullable=False)
    component_type = db.Column(db.String(30), nullable=False)  # Earning, Deduction
    is_taxable = db.Column(db.Boolean, default=True)
    calculation_method = db.Column(db.String(30), default='Fixed')  # Fixed, Percentage
    default_amount = db.Column(db.Numeric(10, 2), default=0.00)

    def __repr__(self):
        return f"<SalaryComponent {self.component_code} ({self.component_type})>"


class EmployeeSalaryAssignment(db.Model):
    """Individual employee salary package configuration."""
    __tablename__ = 'employee_salary_assignments'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), unique=True, nullable=False)
    structure_id = db.Column(db.Integer, db.ForeignKey('salary_structures.id'), nullable=True)
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False, default=60000.00)
    house_rent_allowance = db.Column(db.Numeric(10, 2), default=15000.00)
    conveyance_allowance = db.Column(db.Numeric(10, 2), default=5000.00)
    medical_allowance = db.Column(db.Numeric(10, 2), default=5000.00)
    effective_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(30), default='Active')  # Active, Inactive

    employee = db.relationship('Employee', back_populates='salary_assignment')
    structure = db.relationship('SalaryStructure', back_populates='employee_assignments')

    @property
    def gross_monthly(self):
        return (
            (self.basic_salary or 0)
            + (self.house_rent_allowance or 0)
            + (self.conveyance_allowance or 0)
            + (self.medical_allowance or 0)
        )

    def __repr__(self):
        return f"<SalaryAssignment Emp:{self.employee_id} Basic:{self.basic_salary}>"


class PayrollPeriod(db.Model):
    """Monthly wage cycle intervals (e.g. November 2026)."""
    __tablename__ = 'payroll_periods'

    id = db.Column(db.Integer, primary_key=True)
    period_name = db.Column(db.String(60), nullable=False)
    period_month = db.Column(db.Integer, nullable=False)
    period_year = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), default='Draft')  # Draft, Processing, Completed, Closed
    processed_date = db.Column(db.DateTime, nullable=True)

    payroll_records = db.relationship('PayrollRecord', back_populates='period', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<PayrollPeriod {self.period_name} ({self.status})>"


class PayrollRecord(db.Model):
    """Monthly calculated employee payslip record."""
    __tablename__ = 'payroll_records'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    payroll_period_id = db.Column(db.Integer, db.ForeignKey('payroll_periods.id'), nullable=False)
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    total_allowances = db.Column(db.Numeric(10, 2), default=0.00)
    gross_salary = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    total_deductions = db.Column(db.Numeric(10, 2), default=0.00)
    net_salary = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    payment_status = db.Column(db.String(30), default='Unpaid')  # Unpaid, Paid, Pending
    payment_date = db.Column(db.Date, nullable=True)
    payment_method = db.Column(db.String(50), default='Bank Transfer')  # Bank Transfer, Cheque, Cash

    employee = db.relationship('Employee', back_populates='payroll_records')
    period = db.relationship('PayrollPeriod', back_populates='payroll_records')
    items = db.relationship('PayrollItemDetail', back_populates='payroll_record', cascade='all, delete-orphan', lazy=True)
    bonuses = db.relationship('EmployeeBonus', back_populates='payroll_record', lazy=True)

    def __repr__(self):
        return f"<PayrollRecord #{self.id} Emp:{self.employee_id} Net:{self.net_salary}>"


class PayrollItemDetail(db.Model):
    """Detailed breakdown items displayed on an individual payslip."""
    __tablename__ = 'payroll_item_details'

    id = db.Column(db.Integer, primary_key=True)
    payroll_record_id = db.Column(db.Integer, db.ForeignKey('payroll_records.id'), nullable=False)
    component_name = db.Column(db.String(100), nullable=False)
    item_type = db.Column(db.String(30), nullable=False)  # Earning, Deduction
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    payroll_record = db.relationship('PayrollRecord', back_populates='items')

    def __repr__(self):
        return f"<PayrollItem {self.component_name}: {self.amount} ({self.item_type})>"


class EmployeeDeduction(db.Model):
    """Specific recurring deductions (Income Tax, Health Insurance, PF, Advance Loan)."""
    __tablename__ = 'employee_deductions'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    deduction_name = db.Column(db.String(100), nullable=False)
    deduction_type = db.Column(db.String(50), default='Tax')  # Tax, Provident Fund, Insurance, Loan
    amount_or_percentage = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    is_recurring = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.Date, default=date.today)
    end_date = db.Column(db.Date, nullable=True)

    employee = db.relationship('Employee')

    def __repr__(self):
        return f"<EmployeeDeduction Emp:{self.employee_id} {self.deduction_name}: {self.amount_or_percentage}>"


class EmployeeBonus(db.Model):
    """Bonuses, performance awards, and festival incentives."""
    __tablename__ = 'employee_bonuses'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    bonus_type = db.Column(db.String(50), nullable=False)  # Performance, Eid, Annual, Referral
    bonus_amount = db.Column(db.Numeric(10, 2), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    award_date = db.Column(db.Date, default=date.today)
    is_paid = db.Column(db.Boolean, default=False)
    payroll_record_id = db.Column(db.Integer, db.ForeignKey('payroll_records.id'), nullable=True)

    employee = db.relationship('Employee')
    payroll_record = db.relationship('PayrollRecord', back_populates='bonuses')

    def __repr__(self):
        return f"<EmployeeBonus Emp:{self.employee_id} {self.bonus_type}: {self.bonus_amount}>"

