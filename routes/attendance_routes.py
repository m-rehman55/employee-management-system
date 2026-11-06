"""
routes/attendance_routes.py - Attendance Management Blueprint.
Provides full CRUD operations, shift schedules, hours calculation, and PRG pattern.
"""
from datetime import datetime, date, time
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.attendance import AttendanceRecord, WorkShift, AttendanceBreak
from models.employee import Employee
from utils.decorators import login_required
from utils.validators import validate_date, validate_numeric
from utils.audit import log_audit

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@attendance_bp.route('/', methods=['GET'])
@login_required
def list_attendance():
    """READ: Displays attendance records with date and employee filters."""
    date_filter = request.args.get('date', '').strip()
    emp_id = request.args.get('emp_id', '')

    query = AttendanceRecord.query

    if date_filter:
        valid_date, d_val, _ = validate_date(date_filter)
        if valid_date:
            query = query.filter(AttendanceRecord.work_date == d_val)
    if emp_id and emp_id.isdigit():
        query = query.filter(AttendanceRecord.employee_id == int(emp_id))

    records = query.order_by(AttendanceRecord.work_date.desc(), AttendanceRecord.id.desc()).all()
    employees = Employee.query.order_by(Employee.first_name).all()

    return render_template(
        'attendance/list.html',
        records=records,
        employees=employees,
        selected_date=date_filter,
        selected_emp_id=emp_id
    )


@attendance_bp.route('/<int:id>', methods=['GET'])
@login_required
def detail(id):
    """READ: Shows attendance punch log details, hours, and registered breaks."""
    record = AttendanceRecord.query.get_or_404(id)
    return render_template('attendance/detail.html', record=record)


@attendance_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """CREATE: Records a new daily attendance entry with server-side validation."""
    employees = Employee.query.filter_by(status='Active').all()
    shifts = WorkShift.query.all()

    if request.method == 'POST':
        emp_id = request.form.get('employee_id')
        shift_id = request.form.get('shift_id')
        work_date_str = request.form.get('work_date', '').strip()
        check_in_str = request.form.get('check_in_time', '').strip()
        check_out_str = request.form.get('check_out_time', '').strip()
        status = request.form.get('status', 'Present').strip()
        notes = request.form.get('notes', '').strip()

        errors = []
        employee = Employee.query.get(emp_id) if (emp_id and emp_id.isdigit()) else None
        if not employee:
            errors.append("A valid employee must be selected.")

        shift = WorkShift.query.get(shift_id) if (shift_id and shift_id.isdigit()) else None

        valid_date, work_date, date_err = validate_date(work_date_str, "Work Date")
        if not valid_date:
            errors.append(date_err)
        elif employee:
            # Check duplicate entry for same date and employee
            existing = AttendanceRecord.query.filter_by(employee_id=employee.id, work_date=work_date).first()
            if existing:
                errors.append(f"Attendance record already exists for {employee.full_name} on {work_date}.")

        # Parse check-in and check-out
        cin_dt = None
        cout_dt = None
        work_hours = Decimal('0.00')

        if check_in_str:
            try:
                cin_dt = datetime.strptime(f"{work_date_str} {check_in_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                errors.append("Check-in time must be in HH:MM format.")

        if check_out_str:
            try:
                cout_dt = datetime.strptime(f"{work_date_str} {check_out_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                errors.append("Check-out time must be in HH:MM format.")

        if cin_dt and cout_dt:
            if cout_dt <= cin_dt:
                errors.append("Check-out time must be after Check-in time.")
            else:
                duration_sec = (cout_dt - cin_dt).total_seconds()
                work_hours = Decimal(str(round(duration_sec / 3600.0, 2)))

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'attendance/form.html',
                action='Add',
                record=None,
                form_data=request.form,
                employees=employees,
                shifts=shifts
            )

        new_record = AttendanceRecord(
            employee_id=employee.id,
            shift_id=shift.id if shift else None,
            work_date=work_date,
            check_in_time=cin_dt,
            check_out_time=cout_dt,
            total_work_hours=work_hours,
            status=status,
            notes=notes
        )
        db.session.add(new_record)
        db.session.commit()

        log_audit('CREATE', 'AttendanceRecord', new_record.id, f"Recorded attendance for {employee.full_name} on {work_date}")
        flash(f"Attendance record for {employee.full_name} on {work_date} successfully added!", 'success')
        return redirect(url_for('attendance.detail', id=new_record.id))

    return render_template(
        'attendance/form.html',
        action='Add',
        record=None,
        form_data={'work_date': date.today().strftime('%Y-%m-%d')},
        employees=employees,
        shifts=shifts
    )


@attendance_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """UPDATE: Modifies attendance punches and working hours."""
    record = AttendanceRecord.query.get_or_404(id)
    employees = Employee.query.filter_by(status='Active').all()
    shifts = WorkShift.query.all()

    if request.method == 'POST':
        shift_id = request.form.get('shift_id')
        check_in_str = request.form.get('check_in_time', '').strip()
        check_out_str = request.form.get('check_out_time', '').strip()
        status = request.form.get('status', 'Present').strip()
        notes = request.form.get('notes', '').strip()

        errors = []
        shift = WorkShift.query.get(shift_id) if (shift_id and shift_id.isdigit()) else None

        cin_dt = None
        cout_dt = None
        work_hours = record.total_work_hours

        work_date_str = record.work_date.strftime('%Y-%m-%d')

        if check_in_str:
            try:
                cin_dt = datetime.strptime(f"{work_date_str} {check_in_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                errors.append("Check-in time must be in HH:MM format.")

        if check_out_str:
            try:
                cout_dt = datetime.strptime(f"{work_date_str} {check_out_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                errors.append("Check-out time must be in HH:MM format.")

        if cin_dt and cout_dt:
            if cout_dt <= cin_dt:
                errors.append("Check-out time must be after Check-in time.")
            else:
                duration_sec = (cout_dt - cin_dt).total_seconds()
                work_hours = Decimal(str(round(duration_sec / 3600.0, 2)))

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'attendance/form.html',
                action='Edit',
                record=record,
                form_data=request.form,
                employees=employees,
                shifts=shifts
            )

        record.shift_id = shift.id if shift else None
        record.check_in_time = cin_dt
        record.check_out_time = cout_dt
        record.total_work_hours = work_hours
        record.status = status
        record.notes = notes

        db.session.commit()
        log_audit('UPDATE', 'AttendanceRecord', record.id, f"Updated attendance for {record.employee.full_name} on {record.work_date}")

        flash(f"Attendance record #{record.id} updated successfully!", 'success')
        return redirect(url_for('attendance.detail', id=record.id))

    return render_template(
        'attendance/form.html',
        action='Edit',
        record=record,
        form_data={},
        employees=employees,
        shifts=shifts
    )


@attendance_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """DELETE: Safely removes an attendance entry."""
    record = AttendanceRecord.query.get_or_404(id)
    emp_name = record.employee.full_name if record.employee else 'Unknown'
    work_d = record.work_date

    db.session.delete(record)
    db.session.commit()

    log_audit('DELETE', 'AttendanceRecord', id, f"Deleted attendance for {emp_name} on {work_d}")
    flash(f"Attendance record for {emp_name} on {work_d} was deleted.", 'info')
    return redirect(url_for('attendance.list_attendance'))

