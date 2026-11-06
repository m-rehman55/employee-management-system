"""
routes/payroll_routes.py - Payroll Management Blueprint.
Provides full CRUD operations, automated salary calculations, payslip generation, and PRG pattern.
"""
from datetime import datetime, date
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.payroll import PayrollRecord, PayrollPeriod, PayrollItemDetail, EmployeeSalaryAssignment
from models.employee import Employee
from utils.decorators import login_required
from utils.validators import validate_numeric, validate_date
from utils.audit import log_audit

payroll_bp = Blueprint('payroll', __name__, url_prefix='/payroll')

@payroll_bp.route('/', methods=['GET'])
@login_required
def list_payroll():
    """READ: Displays generated payslips with period and status filtering."""
    period_id = request.args.get('period_id', '')
    status_filter = request.args.get('status', '').strip()

    query = PayrollRecord.query

    if period_id and period_id.isdigit():
        query = query.filter(PayrollRecord.payroll_period_id == int(period_id))
    if status_filter:
        query = query.filter(PayrollRecord.payment_status == status_filter)

    records = query.order_by(PayrollRecord.id.desc()).all()
    periods = PayrollPeriod.query.order_by(PayrollPeriod.id.desc()).all()

    return render_template(
        'payroll/list.html',
        records=records,
        periods=periods,
        selected_period_id=period_id,
        selected_status=status_filter
    )


@payroll_bp.route('/<int:id>', methods=['GET'])
@login_required
def detail(id):
    """READ: Renders the printable official payslip with itemized line items."""
    record = PayrollRecord.query.get_or_404(id)
    return render_template('payroll/detail.html', record=record)


@payroll_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """CREATE: Generates a new payroll record / payslip with server-side validation."""
    employees = Employee.query.filter_by(status='Active').all()
    periods = PayrollPeriod.query.order_by(PayrollPeriod.id.desc()).all()

    if request.method == 'POST':
        emp_id = request.form.get('employee_id')
        period_id = request.form.get('payroll_period_id')
        basic_str = request.form.get('basic_salary', '0').strip()
        allowances_str = request.form.get('total_allowances', '0').strip()
        deductions_str = request.form.get('total_deductions', '0').strip()
        payment_status = request.form.get('payment_status', 'Unpaid').strip()
        payment_method = request.form.get('payment_method', 'Bank Transfer').strip()
        payment_date_str = request.form.get('payment_date', '').strip()

        errors = []
        employee = Employee.query.get(emp_id) if (emp_id and emp_id.isdigit()) else None
        if not employee:
            errors.append("A valid employee must be selected.")

        period = PayrollPeriod.query.get(period_id) if (period_id and period_id.isdigit()) else None
        if not period:
            errors.append("A valid payroll cycle period must be selected.")

        if employee and period:
            # Check duplicate payslip in this period
            existing = PayrollRecord.query.filter_by(employee_id=employee.id, payroll_period_id=period.id).first()
            if existing:
                errors.append(f"A payslip for {employee.full_name} has already been issued for {period.period_name}.")

        valid_basic, basic_val, basic_err = validate_numeric(basic_str, "Basic Salary", min_val=0)
        if not valid_basic:
            errors.append(basic_err)

        valid_allow, allow_val, allow_err = validate_numeric(allowances_str, "Total Allowances", min_val=0)
        if not valid_allow:
            errors.append(allow_err)

        valid_ded, ded_val, ded_err = validate_numeric(deductions_str, "Total Deductions", min_val=0)
        if not valid_ded:
            errors.append(ded_err)

        pay_dt = None
        if payment_date_str:
            valid_pdate, pay_dt, pdate_err = validate_date(payment_date_str, "Payment Date")
            if not valid_pdate:
                errors.append(pdate_err)

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'payroll/form.html',
                action='Add',
                record=None,
                form_data=request.form,
                employees=employees,
                periods=periods
            )

        basic_dec = Decimal(str(basic_val))
        allow_dec = Decimal(str(allow_val))
        ded_dec = Decimal(str(ded_val))
        gross_dec = basic_dec + allow_dec
        net_dec = max(Decimal(0), gross_dec - ded_dec)

        new_record = PayrollRecord(
            employee_id=employee.id,
            payroll_period_id=period.id,
            basic_salary=basic_dec,
            total_allowances=allow_dec,
            gross_salary=gross_dec,
            total_deductions=ded_dec,
            net_salary=net_dec,
            payment_status=payment_status,
            payment_date=pay_dt if payment_status == 'Paid' else None,
            payment_method=payment_method
        )
        db.session.add(new_record)
        db.session.flush()

        # Create basic item details breakdown
        db.session.add(PayrollItemDetail(payroll_record_id=new_record.id, component_name='Basic Salary', item_type='Earning', amount=basic_dec))
        if allow_dec > 0:
            db.session.add(PayrollItemDetail(payroll_record_id=new_record.id, component_name='Allowances', item_type='Earning', amount=allow_dec))
        if ded_dec > 0:
            db.session.add(PayrollItemDetail(payroll_record_id=new_record.id, component_name='Statutory Deductions', item_type='Deduction', amount=ded_dec))

        db.session.commit()
        log_audit('CREATE', 'PayrollRecord', new_record.id, f"Generated payslip for {employee.full_name} ({period.period_name}): Net {net_dec}")

        flash(f"Payslip for {employee.full_name} for {period.period_name} was generated successfully!", 'success')
        return redirect(url_for('payroll.detail', id=new_record.id))

    return render_template(
        'payroll/form.html',
        action='Add',
        record=None,
        form_data={'payment_date': date.today().strftime('%Y-%m-%d')},
        employees=employees,
        periods=periods
    )


@payroll_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """UPDATE: Modifies compensation components and payment status."""
    record = PayrollRecord.query.get_or_404(id)
    employees = Employee.query.filter_by(status='Active').all()
    periods = PayrollPeriod.query.order_by(PayrollPeriod.id.desc()).all()

    if request.method == 'POST':
        basic_str = request.form.get('basic_salary', '0').strip()
        allowances_str = request.form.get('total_allowances', '0').strip()
        deductions_str = request.form.get('total_deductions', '0').strip()
        payment_status = request.form.get('payment_status', record.payment_status).strip()
        payment_method = request.form.get('payment_method', record.payment_method).strip()
        payment_date_str = request.form.get('payment_date', '').strip()

        errors = []
        valid_basic, basic_val, basic_err = validate_numeric(basic_str, "Basic Salary", min_val=0)
        if not valid_basic:
            errors.append(basic_err)

        valid_allow, allow_val, allow_err = validate_numeric(allowances_str, "Total Allowances", min_val=0)
        if not valid_allow:
            errors.append(allow_err)

        valid_ded, ded_val, ded_err = validate_numeric(deductions_str, "Total Deductions", min_val=0)
        if not valid_ded:
            errors.append(ded_err)

        pay_dt = None
        if payment_date_str:
            valid_pdate, pay_dt, pdate_err = validate_date(payment_date_str, "Payment Date")
            if not valid_pdate:
                errors.append(pdate_err)

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'payroll/form.html',
                action='Edit',
                record=record,
                form_data=request.form,
                employees=employees,
                periods=periods
            )

        basic_dec = Decimal(str(basic_val))
        allow_dec = Decimal(str(allow_val))
        ded_dec = Decimal(str(ded_val))
        gross_dec = basic_dec + allow_dec
        net_dec = max(Decimal(0), gross_dec - ded_dec)

        record.basic_salary = basic_dec
        record.total_allowances = allow_dec
        record.gross_salary = gross_dec
        record.total_deductions = ded_dec
        record.net_salary = net_dec
        record.payment_status = payment_status
        record.payment_method = payment_method
        if payment_status == 'Paid':
            record.payment_date = pay_dt or date.today()
        else:
            record.payment_date = None

        db.session.commit()
        log_audit('UPDATE', 'PayrollRecord', record.id, f"Updated payslip #{record.id} for {record.employee.full_name}")

        flash(f"Payslip #{record.id} updated successfully!", 'success')
        return redirect(url_for('payroll.detail', id=record.id))

    return render_template(
        'payroll/form.html',
        action='Edit',
        record=record,
        form_data={},
        employees=employees,
        periods=periods
    )


@payroll_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """DELETE: Safely removes a payslip record."""
    record = PayrollRecord.query.get_or_404(id)
    emp_name = record.employee.full_name if record.employee else 'Unknown'
    period_name = record.period.period_name if record.period else 'Period'

    db.session.delete(record)
    db.session.commit()

    log_audit('DELETE', 'PayrollRecord', id, f"Deleted payslip #{id} for {emp_name} ({period_name})")
    flash(f"Payslip #{id} for {emp_name} was deleted successfully.", 'info')
    return redirect(url_for('payroll.list_payroll'))

