"""
routes/leave_routes.py - Leave Management Blueprint.
Provides full CRUD operations, leave balance deduction, approval logging, and PRG pattern.
"""
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import and_
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from extensions import db
from models.leave import LeaveRequest, LeaveType, LeaveBalance, LeaveApproval
from models.employee import Employee
from utils.decorators import login_required, role_required
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
    if session.get('role_name') == 'Employee':
        query = query.filter(LeaveRequest.employee_id == session.get('employee_id'))

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
    leave_req = db.get_or_404(LeaveRequest, id)
    if session.get('role_name') == 'Employee' and leave_req.employee_id != session.get('employee_id'):
        abort(403)
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
        if session.get('role_name') == 'Employee':
            emp_id = str(session.get('employee_id') or '')
        type_id = request.form.get('leave_type_id')
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        reason = request.form.get('reason', '').strip()

        errors = []
        employee = db.session.get(Employee, int(emp_id)) if (emp_id and emp_id.isdigit()) else None
        if not employee:
            errors.append("A valid employee must be selected.")

        leave_type = db.session.get(LeaveType, int(type_id)) if (type_id and type_id.isdigit()) else None
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
            if session.get('role_name') == 'Employee' and start_dt < date.today():
                errors.append("Employees can submit leave only from today onward.")
            if employee:
                overlap = LeaveRequest.query.filter(
                    LeaveRequest.employee_id == employee.id,
                    LeaveRequest.status.in_(['Pending', 'Approved']),
                    LeaveRequest.start_date <= end_dt,
                    LeaveRequest.end_date >= start_dt,
                ).first()
                if overlap:
                    errors.append(f"These dates overlap leave request #{overlap.id} ({overlap.status}).")
                balance = LeaveBalance.query.filter_by(
                    employee_id=employee.id, leave_type_id=leave_type.id if leave_type else None, year=start_dt.year
                ).first()
                if balance and (balance.remaining_days or Decimal(0)) - (balance.pending_days or Decimal(0)) < days:
                    errors.append("The requested leave exceeds the available balance after pending requests.")
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
            status='Pending'
        )
        db.session.add(new_leave)
        db.session.flush()

        bal = LeaveBalance.query.filter_by(
            employee_id=employee.id,
            leave_type_id=leave_type.id,
            year=start_dt.year
        ).first()
        if bal:
            bal.pending_days = (bal.pending_days or Decimal(0)) + days

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
@role_required('Administrator', 'HR Manager')
def edit(id):
    """UPDATE: Modifies leave application details or changes status."""
    leave_req = db.get_or_404(LeaveRequest, id)
    employees = Employee.query.filter_by(status='Active').all()
    leave_types = LeaveType.query.all()

    if request.method == 'POST':
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        reason = request.form.get('reason', '').strip()

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

        if leave_req.status != 'Pending':
            errors.append("Only pending leave requests can be edited.")
        if valid_start and valid_end:
            overlap = LeaveRequest.query.filter(
                LeaveRequest.id != leave_req.id,
                LeaveRequest.employee_id == leave_req.employee_id,
                LeaveRequest.status.in_(['Pending', 'Approved']),
                LeaveRequest.start_date <= end_dt,
                LeaveRequest.end_date >= start_dt,
            ).first()
            if overlap:
                errors.append(f"These dates overlap leave request #{overlap.id} ({overlap.status}).")
            balance = LeaveBalance.query.filter_by(
                employee_id=leave_req.employee_id, leave_type_id=leave_req.leave_type_id, year=start_dt.year
            ).first()
            if balance and (balance.remaining_days or Decimal(0)) - max(
                Decimal(0), (balance.pending_days or Decimal(0)) - (leave_req.total_days or Decimal(0))
            ) < days:
                errors.append("The requested leave exceeds the available balance after pending requests.")

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

        old_days = leave_req.total_days or Decimal(0)
        leave_req.start_date = start_dt
        leave_req.end_date = end_dt
        leave_req.total_days = days
        leave_req.reason = reason

        balance = LeaveBalance.query.filter_by(
            employee_id=leave_req.employee_id, leave_type_id=leave_req.leave_type_id, year=start_dt.year
        ).first()
        if balance:
            balance.pending_days = max(Decimal(0), (balance.pending_days or Decimal(0)) - old_days + days)

        db.session.commit()
        log_audit('UPDATE', 'LeaveRequest', leave_req.id, f"Updated leave request #{leave_req.id}")

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


@leave_bp.route('/<int:id>/decision', methods=['POST'])
@login_required
@role_required('Administrator', 'HR Manager')
def decision(id):
    """Record an explicit HR decision and update the leave balance once."""
    leave_req = db.get_or_404(LeaveRequest, id)
    action = request.form.get('decision', '').strip()
    remarks = request.form.get('remarks', '').strip()

    if action not in {'Approved', 'Rejected'}:
        flash('Choose either Approve or Reject for this request.', 'danger')
        return redirect(url_for('leaves.detail', id=id))
    if leave_req.status != 'Pending':
        flash('Only pending leave requests can be decided.', 'warning')
        return redirect(url_for('leaves.detail', id=id))
    if not remarks:
        flash('A decision note is required for approval records.', 'danger')
        return redirect(url_for('leaves.detail', id=id))

    leave_req.status = action
    db.session.add(LeaveApproval(
        leave_request_id=leave_req.id,
        approver_id=session.get('employee_id'),
        approval_level=1,
        action=action,
        remarks=remarks
    ))

    balance = LeaveBalance.query.filter_by(
        employee_id=leave_req.employee_id,
        leave_type_id=leave_req.leave_type_id,
        year=leave_req.start_date.year
    ).first()
    if action == 'Approved' and balance and (balance.remaining_days or Decimal(0)) < leave_req.total_days:
        flash('This request cannot be approved because the available balance is insufficient.', 'danger')
        return redirect(url_for('leaves.detail', id=id))
    if balance:
        balance.pending_days = max(
            Decimal(0), (balance.pending_days or Decimal(0)) - leave_req.total_days
        )
        if action == 'Approved':
            balance.used_days = (balance.used_days or Decimal(0)) + leave_req.total_days
            balance.remaining_days = max(
                Decimal(0), (balance.remaining_days or Decimal(0)) - leave_req.total_days
            )

    db.session.commit()
    log_audit(
        action.upper(), 'LeaveRequest', leave_req.id,
        f"{action} leave request #{leave_req.id}: {remarks}"
    )
    flash(f"Leave request #{leave_req.id} was {action.lower()}.", 'success')
    return redirect(url_for('leaves.detail', id=id))


@leave_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Administrator', 'HR Manager')
def delete(id):
    """DELETE: Safely deletes a leave request."""
    leave_req = db.get_or_404(LeaveRequest, id)
    emp_name = leave_req.employee.full_name if leave_req.employee else 'Unknown'

    db.session.delete(leave_req)
    db.session.commit()

    log_audit('DELETE', 'LeaveRequest', id, f"Deleted leave request #{id} for {emp_name}")
    flash(f"Leave request #{id} for {emp_name} has been deleted.", 'info')
    return redirect(url_for('leaves.list_leaves'))

