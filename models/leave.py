"""
models/leave.py - Leave Management models (8 models).
Handles leave types, leave policies, leave balances, requests, multi-tier approvals, attachments, holidays, and encashments.
"""
from datetime import datetime, date
from extensions import db
from utils.time import utc_now


class LeaveType(db.Model):
    """Catalog of leave types (Annual, Sick, Casual, Maternity, Unpaid)."""
    __tablename__ = 'leave_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    default_days_per_year = db.Column(db.Integer, nullable=False, default=14)
    is_paid = db.Column(db.Boolean, default=True)
    requires_approval = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    policies = db.relationship('LeavePolicy', back_populates='leave_type', cascade='all, delete-orphan', lazy=True)
    balances = db.relationship('LeaveBalance', back_populates='leave_type', cascade='all, delete-orphan', lazy=True)
    requests = db.relationship('LeaveRequest', back_populates='leave_type', cascade='all, delete-orphan', lazy=True)
    encashments = db.relationship('LeaveEncashment', back_populates='leave_type', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<LeaveType {self.code} - {self.name}>"


class LeavePolicy(db.Model):
    """Accrual, carry-over caps, and tenure rules per leave category."""
    __tablename__ = 'leave_policies'

    id = db.Column(db.Integer, primary_key=True)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    policy_name = db.Column(db.String(100), nullable=False)
    max_consecutive_days = db.Column(db.Integer, default=5)
    carry_forward_days = db.Column(db.Integer, default=5)
    min_service_months = db.Column(db.Integer, default=3)
    is_active = db.Column(db.Boolean, default=True)

    leave_type = db.relationship('LeaveType', back_populates='policies')

    def __repr__(self):
        return f"<LeavePolicy {self.policy_name}>"


class LeaveBalance(db.Model):
    """Annual allocated and remaining leave balances per employee."""
    __tablename__ = 'leave_balances'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_allocated = db.Column(db.Numeric(5, 2), default=14.0)
    used_days = db.Column(db.Numeric(5, 2), default=0.0)
    pending_days = db.Column(db.Numeric(5, 2), default=0.0)
    remaining_days = db.Column(db.Numeric(5, 2), default=14.0)

    employee = db.relationship('Employee', back_populates='leave_balances')
    leave_type = db.relationship('LeaveType', back_populates='balances')

    def __repr__(self):
        return f"<LeaveBalance Emp:{self.employee_id} Type:{self.leave_type_id} Rem:{self.remaining_days}>"


class LeaveRequest(db.Model):
    """Formal leave applications submitted by employees."""
    __tablename__ = 'leave_requests'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Numeric(4, 1), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='Pending')  # Pending, Approved, Rejected, Cancelled
    applied_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    employee = db.relationship('Employee', back_populates='leave_requests')
    leave_type = db.relationship('LeaveType', back_populates='requests')
    approvals = db.relationship('LeaveApproval', back_populates='leave_request', cascade='all, delete-orphan', lazy=True)
    attachments = db.relationship('LeaveAttachment', back_populates='leave_request', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<LeaveRequest #{self.id} Emp:{self.employee_id} Status:{self.status}>"


class LeaveApproval(db.Model):
    """Supervisor and HR decision trail for leave requests."""
    __tablename__ = 'leave_approvals'

    id = db.Column(db.Integer, primary_key=True)
    leave_request_id = db.Column(db.Integer, db.ForeignKey('leave_requests.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    approval_level = db.Column(db.Integer, default=1)
    action = db.Column(db.String(30), nullable=False)  # Approved, Rejected, Recommended
    remarks = db.Column(db.Text, nullable=True)
    action_date = db.Column(db.DateTime, default=utc_now)

    leave_request = db.relationship('LeaveRequest', back_populates='approvals')
    approver = db.relationship('Employee')

    def __repr__(self):
        return f"<LeaveApproval Req:{self.leave_request_id} Action:{self.action}>"


class LeaveAttachment(db.Model):
    """Medical certificates or supporting proof files."""
    __tablename__ = 'leave_attachments'

    id = db.Column(db.Integer, primary_key=True)
    leave_request_id = db.Column(db.Integer, db.ForeignKey('leave_requests.id'), nullable=False)
    file_name = db.Column(db.String(150), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size_kb = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=utc_now)

    leave_request = db.relationship('LeaveRequest', back_populates='attachments')

    def __repr__(self):
        return f"<LeaveAttachment {self.file_name}>"


class CompanyHoliday(db.Model):
    """National and company holiday schedule."""
    __tablename__ = 'company_holidays'

    id = db.Column(db.Integer, primary_key=True)
    holiday_name = db.Column(db.String(100), nullable=False)
    holiday_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_recurring = db.Column(db.Boolean, default=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    department = db.relationship('Department')

    def __repr__(self):
        return f"<CompanyHoliday {self.holiday_name} on {self.holiday_date}>"


class LeaveEncashment(db.Model):
    """Conversion of unused annual leaves into salary encashment."""
    __tablename__ = 'leave_encashments'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    days_encashed = db.Column(db.Numeric(4, 1), nullable=False)
    encashment_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(30), default='Pending')  # Pending, Processed, Rejected
    requested_at = db.Column(db.DateTime, default=utc_now)
    processed_at = db.Column(db.DateTime, nullable=True)

    employee = db.relationship('Employee')
    leave_type = db.relationship('LeaveType', back_populates='encashments')

    def __repr__(self):
        return f"<LeaveEncashment Emp:{self.employee_id} Days:{self.days_encashed}>"

