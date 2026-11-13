"""
routes/dashboard_routes.py - Dashboard Blueprint.
Computes and renders database-driven analytics and summaries across all 5 modules.
"""
from datetime import date
from flask import Blueprint, render_template, request, session, make_response, redirect, url_for
from extensions import db
from models.employee import Employee
from models.department import Department
from models.leave import LeaveRequest
from models.attendance import AttendanceRecord
from models.payroll import PayrollRecord, PayrollPeriod
from utils.decorators import login_required
from utils.security import safe_local_url

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Renders the executive dashboard with real-time database calculations."""
    # 1. Real-time metric counts
    total_employees = Employee.query.count()
    active_employees = Employee.query.filter_by(status='Active').count()
    total_departments = Department.query.count()
    pending_leaves = LeaveRequest.query.filter_by(status='Pending').count()
    
    # 2. Today's attendance calculation
    today = date.today()
    today_attendance = AttendanceRecord.query.filter_by(work_date=today).count()
    
    # 3. Latest payroll summary
    latest_period = PayrollPeriod.query.order_by(PayrollPeriod.id.desc()).first()
    total_payroll_disbursed = 0
    if latest_period:
        payroll_records = PayrollRecord.query.filter_by(payroll_period_id=latest_period.id).all()
        total_payroll_disbursed = sum(r.net_salary for r in payroll_records)

    # 4. Recent activities for quick review
    recent_employees = Employee.query.order_by(Employee.id.desc()).limit(5).all()
    recent_leaves = LeaveRequest.query.order_by(LeaveRequest.id.desc()).limit(5).all()
    recent_attendance = AttendanceRecord.query.order_by(AttendanceRecord.id.desc()).limit(5).all()
    departments = Department.query.all()

    # Demonstrate reading theme cookie (e.g. light/dark)
    current_theme = request.cookies.get('app_theme')
    if current_theme not in {'light', 'dark'}:
        current_theme = 'auto'

    return render_template(
        'dashboard/index.html',
        total_employees=total_employees,
        active_employees=active_employees,
        total_departments=total_departments,
        pending_leaves=pending_leaves,
        today_attendance=today_attendance,
        total_payroll_disbursed=total_payroll_disbursed,
        latest_period=latest_period,
        recent_employees=recent_employees,
        recent_leaves=recent_leaves,
        recent_attendance=recent_attendance,
        departments=departments,
        current_theme=current_theme
    )

@dashboard_bp.route('/toggle-theme')
def toggle_theme():
    """Toggles UI theme cookie between light and dark."""
    current_theme = request.cookies.get('app_theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    fallback = url_for('dashboard.index') if 'user_id' in session else url_for('auth.login')
    ref = safe_local_url(request.referrer, fallback)
    if 'toggle-theme' in ref:
        ref = fallback
    response = make_response(redirect(ref))
    response.set_cookie('app_theme', new_theme, path='/', max_age=365*24*60*60, samesite='Lax')
    return response

