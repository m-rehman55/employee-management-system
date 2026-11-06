"""
routes/leave_routes.py - Leave Management Blueprint.
Provides full CRUD operations, leave balance deduction, approval logging, and PRG pattern.
"""
from datetime import datetime, date
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models.leave import LeaveRequest, LeaveType, LeaveBalance, LeaveApproval
from models.employee import Employee
from utils.decorators import login_required
from utils.validators import validate_date
from utils.audit import log_audit

leave_bp = Blueprint('leaves', __name__, url_prefix='/leaves')

@leave_bp.route('/', methods=['GET'])
@login_required
def list_leaves():
    """READ: Displays all leave applications with status filter."""
    status_filter = request.args.get('status', '').strip()
    leave_type_id = request.args.get('type_id', '')

    query = LeaveRequest.query

    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)
    if leave_type_id and leave_type_id.isdigit():
        query = query.filter(LeaveRequest.leave_type_id == int(leave_type_id))

    leave_requests = query.order_by(LeaveRequest.id.desc()).all()
    leave_types = LeaveType.query.all()

    return render_template(
        'leaves/list.html',
        leave_requests=leave_requests,
        leave_types=leave_types,
        selected_status=status_filter,
        selected_type_id=leave_type_id
    )


@leave_bp.route('/<int:id>', methods=['GET'])
@login_required
def detail(id):
    """READ: Displays details of a specific leave application and its approval history."""
    leave_req = LeaveRequest.query.get_or_404(id)
    # Fetch employee's current leave balance for this leave type
    current_balance = LeaveBalance.query.filter_by(
        employee_id=leave_req.employee_id,
        leave_type_id=leave_req.leave_type_id,
        year=leave_req.start_date.year
    ).first()

    return render_template('leaves/detail.html', leave=leave_req, balance=current_balance)


@leave_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """CREATE: Submits a new leave request with server-side validation."""
    employees = Employee.query.filter_by(status='Active').all()
    leave_types = LeaveType.query.all()

    if request.method == 'POST':
        emp_id = request.form.get('employee_id')
        type_id = request.form.get('leave_type_id')
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        reason = request.form.get('reason', '').strip()
        status = request.form.get('status', 'Pending').strip()

        errors = []
        employee = Employee.query.get(emp_id) if (emp_id and emp_id.isdigit()) else None
        if not employee:
            errors.append("A valid employee must be selected.")

        leave_type = LeaveType.query.get(type_id) if (type_id and type_id.isdigit()) else None
        if not leave_type:
            errors.append("A valid leave category must be selected.")

        valid_start, start_dt, start_err = validate_date(start_date_str, "Start Date")
        if not valid_start:
            errors.append(start_err)

        valid_end, end_dt, end_err = validate_date(end_date_str, "End Date")
        if not valid_end:
            errors.append(end_err)

        if valid_start and valid_end:
            if end_dt < start_dt:
                errors.append("End Date cannot be earlier than Start Date.")
            days = Decimal((end_dt - start_dt).days + 1)
        else:
            days = Decimal(1)

        if not reason:
            errors.append("Reason for leave is required.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'leaves/form.html',
                action='Add',
                leave=None,
                form_data=request.form,
                employees=employees,
                leave_types=leave_types
            )

        new_leave = LeaveRequest(
            employee_id=employee.id,
            leave_type_id=leave_type.id,
            start_date=start_dt,
            end_date=end_dt,
            total_days=days,
            reason=reason,
            status=status
        )
        db.session.add(new_leave)
        db.session.flush()

        # If created as Approved, add approval log and update balance
        if status == 'Approved':
            approver_emp_id = session.get('employee_id')
            db.session.add(LeaveApproval(
                leave_request_id=new_leave.id,
                approver_id=approver_emp_id,
                approval_level=1,
                action='Approved',
                remarks='Direct approval upon creation'
            ))
            # Deduct balance
            bal = LeaveBalance.query.filter_by(employee_id=employee.id, leave_type_id=leave_type.id, year=start_dt.year).first()
            if bal:
                bal.used_days += days
                bal.remaining_days = max(Decimal(0), bal.remaining_days - days)

        db.session.commit()
        log_audit('CREATE', 'LeaveRequest', new_leave.id, f"Created leave request for {employee.full_name} ({days} days)")

        flash(f"Leave request for {employee.full_name} ({days} days) has been recorded!", 'success')
        return redirect(url_for('leaves.detail', id=new_leave.id))

    return render_template(
        'leaves/form.html',
        action='Add',
        leave=None,
        form_data={},
        employees=employees,
        leave_types=leave_types
    )


@leave_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """UPDATE: Modifies leave application details or changes status."""
    leave_req = LeaveRequest.query.get_or_404(id)
    employees = Employee.query.filter_by(status='Active').all()
    leave_types = LeaveType.query.all()

    if request.method == 'POST':
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        reason = request.form.get('reason', '').strip()
        new_status = request.form.get('status', leave_req.status).strip()
        remarks = request.form.get('remarks', '').strip()

        errors = []
        valid_start, start_dt, start_err = validate_date(start_date_str, "Start Date")
        if not valid_start:
            errors.append(start_err)

        valid_end, end_dt, end_err = validate_date(end_date_str, "End Date")
        if not valid_end:
            errors.append(end_err)

        if valid_start and valid_end:
            if end_dt < start_dt:
                errors.append("End Date cannot be earlier than Start Date.")
            days = Decimal((end_dt - start_dt).days + 1)
        else:
            days = leave_req.total_days

        if not reason:
            errors.append("Reason for leave is required.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'leaves/form.html',
                action='Edit',
                leave=leave_req,
                form_data=request.form,
                employees=employees,
                leave_types=leave_types
            )

        # Status transition check
        old_status = leave_req.status
        leave_req.start_date = start_dt
        leave_req.end_date = end_dt
        leave_req.total_days = days
        leave_req.reason = reason
        leave_req.status = new_status

        # If status changed to Approved or Rejected, log an approval record
        if old_status != new_status:
            approver_emp_id = session.get('employee_id')
            db.session.add(LeaveApproval(
                leave_request_id=leave_req.id,
                approver_id=approver_emp_id,
                approval_level=1,
                action=new_status,
                remarks=remarks or f"Status changed from {old_status} to {new_status}"
            ))

            # Adjust balance if approved
            if new_status == 'Approved' and old_status != 'Approved':
                bal = LeaveBalance.query.filter_by(
                    employee_id=leave_req.employee_id,
                    leave_type_id=leave_req.leave_type_id,
                    year=start_dt.year
                ).first()
                if bal:
                    bal.used_days += days
                    bal.remaining_days = max(Decimal(0), bal.remaining_days - days)

        db.session.commit()
        log_audit('UPDATE', 'LeaveRequest', leave_req.id, f"Updated leave request #{leave_req.id} (Status: {new_status})")

        flash(f"Leave request #{leave_req.id} was updated successfully!", 'success')
        return redirect(url_for('leaves.detail', id=leave_req.id))

    return render_template(
        'leaves/form.html',
        action='Edit',
        leave=leave_req,
        form_data={},
        employees=employees,
        leave_types=leave_types
    )


@leave_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """DELETE: Safely deletes a leave request."""
    leave_req = LeaveRequest.query.get_or_404(id)
    emp_name = leave_req.employee.full_name if leave_req.employee else 'Unknown'

    db.session.delete(leave_req)
    db.session.commit()

    log_audit('DELETE', 'LeaveRequest', id, f"Deleted leave request #{id} for {emp_name}")
    flash(f"Leave request #{id} for {emp_name} has been deleted.", 'info')
    return redirect(url_for('leaves.list_leaves'))

