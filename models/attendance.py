"""
models/attendance.py - Attendance Management models (8 models).
Handles work shifts, schedules, daily attendance records, missed-punch corrections, overtime, summaries, biometric devices, and break logs.
"""
from datetime import datetime, date, time
from extensions import db


class WorkShift(db.Model):
    """Standard work shift timetables (e.g. Regular 9-5, Night Shift)."""
    __tablename__ = 'work_shifts'

    id = db.Column(db.Integer, primary_key=True)
    shift_name = db.Column(db.String(60), nullable=False)
    shift_code = db.Column(db.String(20), unique=True, nullable=False)
    start_time = db.Column(db.Time, nullable=False, default=time(9, 0))
    end_time = db.Column(db.Time, nullable=False, default=time(17, 0))
    grace_period_minutes = db.Column(db.Integer, default=15)
    half_day_hours = db.Column(db.Numeric(3, 1), default=4.0)

    schedules = db.relationship('EmployeeShiftSchedule', back_populates='shift', cascade='all, delete-orphan', lazy=True)
    attendance_records = db.relationship('AttendanceRecord', back_populates='shift', lazy=True)

    def __repr__(self):
        return f"<WorkShift {self.shift_code} - {self.shift_name}>"


class EmployeeShiftSchedule(db.Model):
    """Shift assignments for employees across specific calendar spans."""
    __tablename__ = 'employee_shift_schedules'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('work_shifts.id'), nullable=False)
    effective_from = db.Column(db.Date, nullable=False, default=date.today)
    effective_to = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    employee = db.relationship('Employee')
    shift = db.relationship('WorkShift', back_populates='schedules')

    def __repr__(self):
        return f"<ShiftSchedule Emp:{self.employee_id} Shift:{self.shift_id}>"


class AttendanceRecord(db.Model):
    """Daily check-in and check-out logs and calculated worked hours."""
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('work_shifts.id'), nullable=True)
    work_date = db.Column(db.Date, nullable=False, default=date.today)
    check_in_time = db.Column(db.DateTime, nullable=True)
    check_out_time = db.Column(db.DateTime, nullable=True)
    total_work_hours = db.Column(db.Numeric(4, 2), default=0.0)
    status = db.Column(db.String(30), default='Present')  # Present, Late, Half-Day, Absent, On-Leave
    notes = db.Column(db.Text, nullable=True)

    employee = db.relationship('Employee', back_populates='attendance_records')
    shift = db.relationship('WorkShift', back_populates='attendance_records')
    breaks = db.relationship('AttendanceBreak', back_populates='attendance_record', cascade='all, delete-orphan', lazy=True)
    corrections = db.relationship('AttendanceCorrectionRequest', back_populates='attendance_record', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<AttendanceRecord Emp:{self.employee_id} Date:{self.work_date} Status:{self.status}>"


class AttendanceCorrectionRequest(db.Model):
    """Employee request to fix a missing check-in/check-out punch."""
    __tablename__ = 'attendance_corrections'

    id = db.Column(db.Integer, primary_key=True)
    attendance_record_id = db.Column(db.Integer, db.ForeignKey('attendance_records.id'), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    requested_check_in = db.Column(db.DateTime, nullable=False)
    requested_check_out = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='Pending')  # Pending, Approved, Rejected
    reviewed_by = db.Column(db.String(100), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    attendance_record = db.relationship('AttendanceRecord', back_populates='corrections')
    employee = db.relationship('Employee')

    def __repr__(self):
        return f"<AttendanceCorrection Req:{self.id} Status:{self.status}>"


class OvertimeRecord(db.Model):
    """Extra approved working hours records."""
    __tablename__ = 'overtime_records'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False, default=date.today)
    overtime_hours = db.Column(db.Numeric(4, 2), nullable=False, default=1.0)
    overtime_rate_multiplier = db.Column(db.Numeric(3, 2), default=1.5)  # 1.5x standard hourly rate
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='Approved')  # Pending, Approved, Rejected
    approved_by = db.Column(db.String(100), nullable=True)

    employee = db.relationship('Employee')

    def __repr__(self):
        return f"<OvertimeRecord Emp:{self.employee_id} Date:{self.work_date} Hours:{self.overtime_hours}>"


class AttendanceSummary(db.Model):
    """Aggregated monthly attendance statistics used for payroll processing."""
    __tablename__ = 'attendance_summaries'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_working_days = db.Column(db.Integer, default=22)
    present_days = db.Column(db.Numeric(4, 1), default=22.0)
    absent_days = db.Column(db.Numeric(4, 1), default=0.0)
    half_days = db.Column(db.Numeric(4, 1), default=0.0)
    late_days = db.Column(db.Integer, default=0)
    total_overtime_hours = db.Column(db.Numeric(5, 2), default=0.0)

    employee = db.relationship('Employee')

    def __repr__(self):
        return f"<AttendanceSummary Emp:{self.employee_id} {self.month}/{self.year}>"


class BiometricDevice(db.Model):
    """Physical hardware terminals and punch devices."""
    __tablename__ = 'biometric_devices'

    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100), nullable=False)
    device_ip = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    device_model = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    last_sync_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BiometricDevice {self.device_name} @ {self.location}>"


class AttendanceBreak(db.Model):
    """Mid-day pause tracking (lunch, prayer, tea breaks)."""
    __tablename__ = 'attendance_breaks'

    id = db.Column(db.Integer, primary_key=True)
    attendance_record_id = db.Column(db.Integer, db.ForeignKey('attendance_records.id'), nullable=False)
    break_type = db.Column(db.String(50), default='Lunch')  # Lunch, Tea, Prayer, Rest
    break_start = db.Column(db.DateTime, nullable=False)
    break_end = db.Column(db.DateTime, nullable=True)
    break_duration_minutes = db.Column(db.Integer, default=0)

    attendance_record = db.relationship('AttendanceRecord', back_populates='breaks')

    def __repr__(self):
        return f"<AttendanceBreak {self.break_type} ({self.break_duration_minutes} mins)>"

