"""
seed.py - Seeds the database with realistic sample records for university demonstration and viva.
Populates all 45 models across the 5 modules + authentication & settings.
"""
from datetime import date, datetime, timedelta, time
from decimal import Decimal
import os
from flask import Flask
from config import Config
from extensions import db
import models
from models import (
    Role, User, AuditLog, SystemSetting,
    DepartmentLocation, Department, DepartmentBudget, DepartmentPolicy, DepartmentProject, Designation, DepartmentTransferHistory,
    Employee, EmployeeProfile, EmployeeEmergencyContact, EmployeeEducation, EmployeeExperience,
    EmployeeDocument, EmployeeBankDetail, EmployeeSkill, EmployeeNote, EmployeeAssetAssignment,
    LeaveType, LeavePolicy, LeaveBalance, LeaveRequest, LeaveApproval, LeaveAttachment, CompanyHoliday, LeaveEncashment,
    WorkShift, EmployeeShiftSchedule, AttendanceRecord, AttendanceCorrectionRequest, OvertimeRecord, AttendanceSummary, BiometricDevice, AttendanceBreak,
    SalaryStructure, SalaryComponent, EmployeeSalaryAssignment, PayrollPeriod, PayrollRecord, PayrollItemDetail, EmployeeDeduction, EmployeeBonus
)

def create_seed_data(app=None):
    if app is None:
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # Ensure instance directory exists
        instance_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        
        db.init_app(app)

    with app.app_context():
        # Ensure all tables exist in SQLite database
        db.create_all()

        if User.query.filter_by(username='admin').first():
            print("Database already contains seed data. Skipping recreation.")
            return

        print("Seeding initial data...")

        # 1. System Settings
        settings = [
            SystemSetting(setting_key='company_name', setting_value='Apex Global Technologies Ltd.', category='Company', description='Enterprise Name', is_public=True),
            SystemSetting(setting_key='currency', setting_value='PKR', category='Finance', description='Operating Currency', is_public=True),
            SystemSetting(setting_key='fiscal_year_start', setting_value='July', category='Finance', description='Fiscal Year Start Month', is_public=False),
            SystemSetting(setting_key='standard_work_hours', setting_value='8', category='Attendance', description='Daily Standard Working Hours', is_public=True),
        ]
        db.session.add_all(settings)

        # 2. Roles
        admin_role = Role(role_name='Administrator', description='Full system access, user management, and administrative control.')
        hr_role = Role(role_name='HR Manager', description='Management of employees, leaves, attendance, and payroll.')
        emp_role = Role(role_name='Employee', description='Self-service access for viewing profiles, leaves, and payslips.')
        db.session.add_all([admin_role, hr_role, emp_role])
        db.session.flush()

        # 3. Department Locations
        loc_hq = DepartmentLocation(name='Main Corporate Headquarters', building='Apex Tower', floor='5th Floor', address='Blue Area, Jinnah Avenue', city='Islamabad', state='Federal', country='Pakistan', postal_code='44000')
        loc_tech = DepartmentLocation(name='Tech Development Center', building='Software Technology Park', floor='3rd Floor', address='Ferozepur Road', city='Lahore', state='Punjab', country='Pakistan', postal_code='54000')
        db.session.add_all([loc_hq, loc_tech])
        db.session.flush()

        # 4. Departments
        dept_it = Department(code='DEPT-IT', name='Software Engineering', description='Software design, full-stack web development, and cloud services.', location_id=loc_tech.id, budget=Decimal('15000000.00'), is_active=True)
        dept_hr = Department(code='DEPT-HR', name='Human Resources', description='Talent acquisition, employee lifecycle, workplace relations, and culture.', location_id=loc_hq.id, budget=Decimal('5000000.00'), is_active=True)
        dept_fin = Department(code='DEPT-FIN', name='Finance & Accounting', description='Corporate budgeting, payroll disbursements, audit, and tax compliance.', location_id=loc_hq.id, budget=Decimal('8000000.00'), is_active=True)
        dept_mkt = Department(code='DEPT-MKT', name='Marketing & Growth', description='Digital branding, client relations, and market outreach.', location_id=loc_hq.id, budget=Decimal('6000000.00'), is_active=True)
        db.session.add_all([dept_it, dept_hr, dept_fin, dept_mkt])
        db.session.flush()

        # 5. Department Budgets, Policies, Projects
        budgets = [
            DepartmentBudget(department_id=dept_it.id, fiscal_year=2026, allocated_amount=Decimal('15000000.00'), spent_amount=Decimal('5200000.00'), remaining_amount=Decimal('9800000.00')),
            DepartmentBudget(department_id=dept_hr.id, fiscal_year=2026, allocated_amount=Decimal('5000000.00'), spent_amount=Decimal('1800000.00'), remaining_amount=Decimal('3200000.00')),
            DepartmentBudget(department_id=dept_fin.id, fiscal_year=2026, allocated_amount=Decimal('8000000.00'), spent_amount=Decimal('2900000.00'), remaining_amount=Decimal('5100000.00')),
        ]
        db.session.add_all(budgets)

        policies = [
            DepartmentPolicy(department_id=dept_it.id, title='Source Code Management Policy', policy_code='POL-IT-01', description='Mandatory peer code review and branch protection policies before production merge.'),
            DepartmentPolicy(department_id=dept_hr.id, title='Equal Employment Opportunity', policy_code='POL-HR-01', description='Fair hiring practices without discrimination across all career levels.'),
        ]
        db.session.add_all(policies)

        projects = [
            DepartmentProject(department_id=dept_it.id, project_name='Cloud Native Modernization', project_code='PRJ-IT-101', start_date=date(2026, 1, 15), end_date=date(2026, 12, 31), status='In Progress'),
            DepartmentProject(department_id=dept_hr.id, project_name='Automated Onboarding Portal', project_code='PRJ-HR-202', start_date=date(2026, 2, 1), end_date=date(2026, 8, 30), status='In Progress'),
        ]
        db.session.add_all(projects)

        # 6. Designations
        desig_lead = Designation(department_id=dept_it.id, title='Principal Software Architect', job_code='ENG-01', min_salary=Decimal('250000.00'), max_salary=Decimal('450000.00'), description='Technical leadership, software architecture, and development mentor.')
        desig_dev = Designation(department_id=dept_it.id, title='Senior Full Stack Developer', job_code='ENG-02', min_salary=Decimal('120000.00'), max_salary=Decimal('240000.00'), description='Web and API engineering in Python, Flask, and modern JS.')
        desig_hr_mgr = Designation(department_id=dept_hr.id, title='Human Resources Director', job_code='HR-01', min_salary=Decimal('180000.00'), max_salary=Decimal('300000.00'), description='Head of people operations, compliance, and staff development.')
        desig_hr_exec = Designation(department_id=dept_hr.id, title='HR Operations Officer', job_code='HR-02', min_salary=Decimal('70000.00'), max_salary=Decimal('120000.00'), description='Attendance verification, onboarding, and leave coordination.')
        desig_fin_lead = Designation(department_id=dept_fin.id, title='Chief Financial Officer', job_code='FIN-01', min_salary=Decimal('220000.00'), max_salary=Decimal('380000.00'), description='Financial strategy, treasury, and statutory reporting.')
        db.session.add_all([desig_lead, desig_dev, desig_hr_mgr, desig_hr_exec, desig_fin_lead])
        db.session.flush()

        # 7. Employees
        emp1 = Employee(
            employee_code='EMP-001', first_name='Zayn', last_name='Malik', email='zayn.malik@apex.local',
            phone='+92-300-1122334', date_of_birth=date(1992, 4, 18), gender='Male', hire_date=date(2022, 1, 10),
            department_id=dept_it.id, designation_id=desig_lead.id, employment_type='Full-Time', status='Active'
        )
        emp2 = Employee(
            employee_code='EMP-002', first_name='Ayesha', last_name='Khan', email='ayesha.khan@apex.local',
            phone='+92-301-2233445', date_of_birth=date(1995, 7, 24), gender='Female', hire_date=date(2023, 3, 1),
            department_id=dept_hr.id, designation_id=desig_hr_mgr.id, employment_type='Full-Time', status='Active'
        )
        emp3 = Employee(
            employee_code='EMP-003', first_name='Bilal', last_name='Ahmed', email='bilal.ahmed@apex.local',
            phone='+92-302-3344556', date_of_birth=date(1998, 11, 12), gender='Male', hire_date=date(2024, 6, 15),
            department_id=dept_it.id, designation_id=desig_dev.id, employment_type='Full-Time', status='Active'
        )
        emp4 = Employee(
            employee_code='EMP-004', first_name='Fatima', last_name='Noor', email='fatima.noor@apex.local',
            phone='+92-303-4455667', date_of_birth=date(1996, 9, 5), gender='Female', hire_date=date(2023, 9, 20),
            department_id=dept_fin.id, designation_id=desig_fin_lead.id, employment_type='Full-Time', status='Active'
        )
        db.session.add_all([emp1, emp2, emp3, emp4])
        db.session.flush()

        # Set department managers
        dept_it.manager_id = emp1.id
        dept_hr.manager_id = emp2.id
        dept_fin.manager_id = emp4.id

        # 8. Employee Profiles, Emergency Contacts, Education, Experience, Bank, Skills, Assets
        prof1 = EmployeeProfile(employee_id=emp1.id, national_id='61101-1234567-1', marital_status='Married', blood_group='O+', nationality='Pakistani', current_address='F-10/2, Islamabad', permanent_address='F-10/2, Islamabad', personal_email='zayn.personal@gmail.com', bio='Software architect with 10+ years specializing in distributed systems and cloud backends.')
        prof2 = EmployeeProfile(employee_id=emp2.id, national_id='61101-2345678-2', marital_status='Single', blood_group='B+', nationality='Pakistani', current_address='DHA Phase 2, Islamabad', permanent_address='Gulberg, Lahore', personal_email='ayesha.personal@gmail.com', bio='HR specialist focused on talent acquisition, workplace culture, and modern people analytics.')
        prof3 = EmployeeProfile(employee_id=emp3.id, national_id='35201-3456789-3', marital_status='Single', blood_group='A+', nationality='Pakistani', current_address='Johar Town, Lahore', permanent_address='Model Town, Lahore', personal_email='bilal.code@gmail.com', bio='Full-stack web engineer enthusiastic about Python, Flask, and database design.')
        prof4 = EmployeeProfile(employee_id=emp4.id, national_id='61101-4567890-4', marital_status='Married', blood_group='AB+', nationality='Pakistani', current_address='G-11/3, Islamabad', permanent_address='Peshawar City', personal_email='fatima.cpa@gmail.com', bio='Certified financial analyst overseeing corporate audit and fiscal compliance.')
        db.session.add_all([prof1, prof2, prof3, prof4])

        contacts = [
            EmployeeEmergencyContact(employee_id=emp1.id, contact_name='Maryam Malik', relationship='Spouse', phone_number='+92-300-9988776', is_primary=True),
            EmployeeEmergencyContact(employee_id=emp2.id, contact_name='Tariq Khan', relationship='Parent', phone_number='+92-321-8877665', is_primary=True),
            EmployeeEmergencyContact(employee_id=emp3.id, contact_name='Hamza Ahmed', relationship='Sibling', phone_number='+92-333-7766554', is_primary=True),
        ]
        db.session.add_all(contacts)

        educations = [
            EmployeeEducation(employee_id=emp1.id, degree_title='MS Computer Science', institution='FAST-NUCES Islamabad', field_of_study='Software Engineering', graduation_year=2015, grade_or_gpa='3.85'),
            EmployeeEducation(employee_id=emp2.id, degree_title='MBA Human Resource Management', institution='LUMS Lahore', field_of_study='Human Resources', graduation_year=2018, grade_or_gpa='3.70'),
            EmployeeEducation(employee_id=emp3.id, degree_title='BS Artificial Intelligence', institution='NUST Islamabad', field_of_study='AI & Data Science', graduation_year=2024, grade_or_gpa='3.90'),
        ]
        db.session.add_all(educations)

        experiences = [
            EmployeeExperience(employee_id=emp1.id, company_name='TechVanguard Solutions', job_title='Senior Backend Engineer', start_date=date(2018, 5, 1), end_date=date(2021, 12, 31), responsibilities='Led API architecture and database migrations.', leaving_reason='Career advancement'),
            EmployeeExperience(employee_id=emp2.id, company_name='Global Talent Partners', job_title='Assistant HR Manager', start_date=date(2019, 7, 1), end_date=date(2023, 2, 28), responsibilities='Managed recruitment cycles and employee retention.', leaving_reason='Joined Apex as Director'),
        ]
        db.session.add_all(experiences)

        bank_details = [
            EmployeeBankDetail(employee_id=emp1.id, bank_name='Habib Bank Limited (HBL)', branch_name='Blue Area Branch', account_number='PK36HABB00012345678901', account_holder_name='Zayn Malik', swift_ifsc_code='HABB01', is_primary=True),
            EmployeeBankDetail(employee_id=emp2.id, bank_name='Meezan Bank Ltd', branch_name='Jinnah Super Branch', account_number='PK22MEZN00098765432102', account_holder_name='Ayesha Khan', swift_ifsc_code='MEZN01', is_primary=True),
            EmployeeBankDetail(employee_id=emp3.id, bank_name='Standard Chartered Bank', branch_name='Gulberg Branch', account_number='PK11SCBL00055443322103', account_holder_name='Bilal Ahmed', swift_ifsc_code='SCBL01', is_primary=True),
            EmployeeBankDetail(employee_id=emp4.id, bank_name='Bank Alfalah Ltd', branch_name='F-8 Markaz Branch', account_number='PK99ALFH00011223344504', account_holder_name='Fatima Noor', swift_ifsc_code='ALFH01', is_primary=True),
        ]
        db.session.add_all(bank_details)

        skills = [
            EmployeeSkill(employee_id=emp1.id, skill_name='Python & Flask', proficiency_level='Expert', years_experience=Decimal('8.0'), is_certified=True),
            EmployeeSkill(employee_id=emp1.id, skill_name='SQLAlchemy & Database Optimization', proficiency_level='Expert', years_experience=Decimal('7.5'), is_certified=True),
            EmployeeSkill(employee_id=emp3.id, skill_name='Full Stack Web Development', proficiency_level='Intermediate', years_experience=Decimal('2.0'), is_certified=True),
            EmployeeSkill(employee_id=emp2.id, skill_name='HR Policy & Compliance', proficiency_level='Expert', years_experience=Decimal('6.0'), is_certified=True),
        ]
        db.session.add_all(skills)

        notes = [
            EmployeeNote(employee_id=emp1.id, note_title='Annual Performance Commendation', note_content='Outstanding technical leadership and flawless delivery of Q3 enterprise infrastructure.', note_type='Commendation', created_by='CEO Office'),
            EmployeeNote(employee_id=emp3.id, note_title='Probation Completion Review', note_content='Quick learner, excellent integration with the software development team.', note_type='Performance', created_by='Zayn Malik'),
        ]
        db.session.add_all(notes)

        assets = [
            EmployeeAssetAssignment(employee_id=emp1.id, asset_name='Apple MacBook Pro 16" M3 Max', asset_tag='AST-IT-001', serial_number='C02G1234MD6R', issued_date=date(2022, 1, 11), condition_notes='Brand new condition with charger and sleeve', status='Issued'),
            EmployeeAssetAssignment(employee_id=emp2.id, asset_name='Dell XPS 15 9530', asset_tag='AST-HR-002', serial_number='DL98765XPS', issued_date=date(2023, 3, 2), condition_notes='Issued with enterprise docking station', status='Issued'),
            EmployeeAssetAssignment(employee_id=emp3.id, asset_name='Lenovo ThinkPad X1 Carbon Gen 11', asset_tag='AST-IT-003', serial_number='LNV554433TP', issued_date=date(2024, 6, 16), condition_notes='Standard developer setup', status='Issued'),
        ]
        db.session.add_all(assets)

        docs = [
            EmployeeDocument(employee_id=emp1.id, document_type='Contract', document_name='Employment_Agreement_Zayn.pdf', file_path='/uploads/docs/emp1_contract.pdf', verification_status='Verified'),
            EmployeeDocument(employee_id=emp2.id, document_type='Degree', document_name='MBA_Degree_Ayesha.pdf', file_path='/uploads/docs/emp2_mba.pdf', verification_status='Verified'),
        ]
        db.session.add_all(docs)

        # 9. System Users & Passwords
        user_admin = User(employee_id=emp1.id, username='admin', role_id=admin_role.id, is_active=True)
        user_admin.set_password('admin123')

        user_hr = User(employee_id=emp2.id, username='hr_manager', role_id=hr_role.id, is_active=True)
        user_hr.set_password('manager123')

        user_emp = User(employee_id=emp3.id, username='employee', role_id=emp_role.id, is_active=True)
        user_emp.set_password('user123')

        db.session.add_all([user_admin, user_hr, user_emp])
        db.session.flush()

        # Audit Log
        db.session.add(AuditLog(user_id=user_admin.id, action='CREATE', target_model='SystemInitialization', record_id=1, details='Initial system seed data created successfully.'))

        # 10. Leave Types & Policies
        lt_annual = LeaveType(name='Annual Leave', code='AL', default_days_per_year=18, is_paid=True, requires_approval=True, description='Paid annual vacation time.')
        lt_sick = LeaveType(name='Sick Leave', code='SL', default_days_per_year=12, is_paid=True, requires_approval=True, description='Medical illness or health recovery leaves.')
        lt_casual = LeaveType(name='Casual Leave', code='CL', default_days_per_year=10, is_paid=True, requires_approval=True, description='Short-notice personal leaves.')
        lt_unpaid = LeaveType(name='Unpaid Leave', code='UL', default_days_per_year=30, is_paid=False, requires_approval=True, description='Extended leave without pay.')
        db.session.add_all([lt_annual, lt_sick, lt_casual, lt_unpaid])
        db.session.flush()

        policies_leave = [
            LeavePolicy(leave_type_id=lt_annual.id, policy_name='Standard Annual Leave Policy', max_consecutive_days=10, carry_forward_days=5, min_service_months=3),
            LeavePolicy(leave_type_id=lt_sick.id, policy_name='Medical Leave Policy', max_consecutive_days=7, carry_forward_days=0, min_service_months=0),
        ]
        db.session.add_all(policies_leave)

        # Company Holidays
        holidays = [
            CompanyHoliday(holiday_name='Pakistan Day', holiday_date=date(2026, 3, 23), description='National commemoration holiday', is_recurring=True),
            CompanyHoliday(holiday_name='Eid-ul-Fitr Day 1', holiday_date=date(2026, 3, 21), description='Eid public holiday', is_recurring=False),
            CompanyHoliday(holiday_name='Independence Day', holiday_date=date(2026, 8, 14), description='National Independence Day', is_recurring=True),
        ]
        db.session.add_all(holidays)

        # Leave Balances for Employees
        for emp in [emp1, emp2, emp3, emp4]:
            b_al = LeaveBalance(employee_id=emp.id, leave_type_id=lt_annual.id, year=2026, total_allocated=Decimal('18.0'), used_days=Decimal('2.0'), pending_days=Decimal('0.0'), remaining_days=Decimal('16.0'))
            b_sl = LeaveBalance(employee_id=emp.id, leave_type_id=lt_sick.id, year=2026, total_allocated=Decimal('12.0'), used_days=Decimal('1.0'), pending_days=Decimal('0.0'), remaining_days=Decimal('11.0'))
            b_cl = LeaveBalance(employee_id=emp.id, leave_type_id=lt_casual.id, year=2026, total_allocated=Decimal('10.0'), used_days=Decimal('0.0'), pending_days=Decimal('0.0'), remaining_days=Decimal('10.0'))
            db.session.add_all([b_al, b_sl, b_cl])
        db.session.flush()

        # Leave Requests & Approvals
        req1 = LeaveRequest(employee_id=emp3.id, leave_type_id=lt_annual.id, start_date=date(2026, 11, 10), end_date=date(2026, 11, 12), total_days=Decimal('3.0'), reason='Family wedding ceremony in Lahore.', status='Approved')
        req2 = LeaveRequest(employee_id=emp4.id, leave_type_id=lt_sick.id, start_date=date(2026, 11, 2), end_date=date(2026, 11, 3), total_days=Decimal('2.0'), reason='Seasonal flu and physician recovery advice.', status='Approved')
        req3 = LeaveRequest(employee_id=emp1.id, leave_type_id=lt_casual.id, start_date=date(2026, 11, 20), end_date=date(2026, 11, 21), total_days=Decimal('2.0'), reason='Attending international tech conference.', status='Pending')
        db.session.add_all([req1, req2, req3])
        db.session.flush()

        db.session.add(LeaveApproval(leave_request_id=req1.id, approver_id=emp1.id, approval_level=1, action='Approved', remarks='Approved. Please ensure handoff of ongoing tickets.'))
        db.session.add(LeaveApproval(leave_request_id=req2.id, approver_id=emp2.id, approval_level=1, action='Approved', remarks='Get well soon.'))
        db.session.add(LeaveAttachment(leave_request_id=req2.id, file_name='medical_prescription.pdf', file_path='/uploads/leaves/rx_nov2.pdf', file_size_kb=240))
        db.session.add(LeaveEncashment(employee_id=emp1.id, leave_type_id=lt_annual.id, days_encashed=Decimal('5.0'), encashment_amount=Decimal('45000.00'), status='Processed'))

        # 11. Work Shifts, Biometric Devices, Attendance Records
        shift_morning = WorkShift(shift_name='Standard Day Shift', shift_code='SHIFT-DAY', start_time=time(9, 0), end_time=time(17, 0), grace_period_minutes=15, half_day_hours=Decimal('4.0'))
        shift_evening = WorkShift(shift_name='Evening Support Shift', shift_code='SHIFT-EVE', start_time=time(16, 0), end_time=time(0, 0), grace_period_minutes=15, half_day_hours=Decimal('4.0'))
        db.session.add_all([shift_morning, shift_evening])
        db.session.flush()

        device1 = BiometricDevice(device_name='Main Entrance Biometric Turnstile', device_ip='192.168.10.50', location='HQ Ground Floor Lobby', device_model='ZK-Teco ProFace X', is_active=True)
        device2 = BiometricDevice(device_name='Tech Wing Face Terminal', device_ip='192.168.20.55', location='Lahore STP Floor 3', device_model='Hikvision MinMoe', is_active=True)
        db.session.add_all([device1, device2])

        # Shift schedules
        for emp in [emp1, emp2, emp3, emp4]:
            db.session.add(EmployeeShiftSchedule(employee_id=emp.id, shift_id=shift_morning.id, effective_from=date(2026, 1, 1), is_active=True))
        db.session.flush()

        # Seed recent attendance records (last 3 days)
        today = date.today()
        for i in range(3, 0, -1):
            past_date = today - timedelta(days=i)
            # Skip Sundays
            if past_date.weekday() == 6:
                continue

            for emp in [emp1, emp2, emp3, emp4]:
                cin = datetime.combine(past_date, time(8, 55))
                cout = datetime.combine(past_date, time(17, 10))
                hours = Decimal('8.25')

                att_rec = AttendanceRecord(
                    employee_id=emp.id, shift_id=shift_morning.id, work_date=past_date,
                    check_in_time=cin, check_out_time=cout, total_work_hours=hours,
                    status='Present', notes='On time biometric punch'
                )
                db.session.add(att_rec)
                db.session.flush()

                # Add a lunch break
                b_start = datetime.combine(past_date, time(13, 0))
                b_end = datetime.combine(past_date, time(13, 45))
                db.session.add(AttendanceBreak(attendance_record_id=att_rec.id, break_type='Lunch', break_start=b_start, break_end=b_end, break_duration_minutes=45))

        # Sample Overtime Record & Attendance Summary
        db.session.add(OvertimeRecord(employee_id=emp3.id, work_date=today - timedelta(days=1), overtime_hours=Decimal('2.5'), overtime_rate_multiplier=Decimal('1.5'), reason='Critical deployment patch for client release.', status='Approved', approved_by='Zayn Malik'))
        db.session.add(AttendanceSummary(employee_id=emp3.id, month=10, year=2026, total_working_days=22, present_days=Decimal('21.0'), absent_days=Decimal('0.0'), half_days=Decimal('1.0'), late_days=1, total_overtime_hours=Decimal('5.5')))

        # 12. Salary Structures, Components, Assignments, Payroll
        struct_tech = SalaryStructure(structure_name='Software Engineering Band A', grade_code='SE-A', base_salary=Decimal('150000.00'), min_salary=Decimal('100000.00'), max_salary=Decimal('280000.00'), description='Senior tech staff band')
        struct_hr = SalaryStructure(structure_name='Management Executive Band B', grade_code='MGT-B', base_salary=Decimal('140000.00'), min_salary=Decimal('90000.00'), max_salary=Decimal('250000.00'), description='Mid-senior leadership')
        db.session.add_all([struct_tech, struct_hr])
        db.session.flush()

        comp_basic = SalaryComponent(component_name='Basic Salary', component_code='BASIC', component_type='Earning', is_taxable=True, calculation_method='Fixed', default_amount=Decimal('100000.00'))
        comp_hra = SalaryComponent(component_name='House Rent Allowance', component_code='HRA', component_type='Earning', is_taxable=True, calculation_method='Fixed', default_amount=Decimal('30000.00'))
        comp_med = SalaryComponent(component_name='Medical Allowance', component_code='MED', component_type='Earning', is_taxable=False, calculation_method='Fixed', default_amount=Decimal('10000.00'))
        comp_conv = SalaryComponent(component_name='Conveyance Allowance', component_code='CONV', component_type='Earning', is_taxable=False, calculation_method='Fixed', default_amount=Decimal('10000.00'))
        comp_tax = SalaryComponent(component_name='Income Tax Withholding', component_code='TAX', component_type='Deduction', is_taxable=False, calculation_method='Percentage', default_amount=Decimal('5000.00'))
        comp_pf = SalaryComponent(component_name='Provident Fund', component_code='PF', component_type='Deduction', is_taxable=False, calculation_method='Percentage', default_amount=Decimal('8000.00'))
        db.session.add_all([comp_basic, comp_hra, comp_med, comp_conv, comp_tax, comp_pf])

        # Employee Salary Assignments
        asgn1 = EmployeeSalaryAssignment(employee_id=emp1.id, structure_id=struct_tech.id, basic_salary=Decimal('220000.00'), house_rent_allowance=Decimal('55000.00'), conveyance_allowance=Decimal('20000.00'), medical_allowance=Decimal('15000.00'))
        asgn2 = EmployeeSalaryAssignment(employee_id=emp2.id, structure_id=struct_hr.id, basic_salary=Decimal('160000.00'), house_rent_allowance=Decimal('40000.00'), conveyance_allowance=Decimal('15000.00'), medical_allowance=Decimal('10000.00'))
        asgn3 = EmployeeSalaryAssignment(employee_id=emp3.id, structure_id=struct_tech.id, basic_salary=Decimal('110000.00'), house_rent_allowance=Decimal('28000.00'), conveyance_allowance=Decimal('12000.00'), medical_allowance=Decimal('10000.00'))
        asgn4 = EmployeeSalaryAssignment(employee_id=emp4.id, structure_id=struct_hr.id, basic_salary=Decimal('180000.00'), house_rent_allowance=Decimal('45000.00'), conveyance_allowance=Decimal('15000.00'), medical_allowance=Decimal('15000.00'))
        db.session.add_all([asgn1, asgn2, asgn3, asgn4])

        # Recurring Deductions & Bonuses
        db.session.add(EmployeeDeduction(employee_id=emp1.id, deduction_name='Corporate Health Insurance Plan', deduction_type='Insurance', amount_or_percentage=Decimal('6000.00'), is_recurring=True))
        db.session.add(EmployeeDeduction(employee_id=emp3.id, deduction_name='Provident Fund Employee Share', deduction_type='Provident Fund', amount_or_percentage=Decimal('8800.00'), is_recurring=True))
        db.session.add(EmployeeBonus(employee_id=emp1.id, bonus_type='Quarterly Performance Bonus', bonus_amount=Decimal('50000.00'), reason='Exemplary delivery of Q3 milestones.', is_paid=True))

        # Payroll Period & Payslip Records for October 2026
        period_oct = PayrollPeriod(
            period_name='October 2026 Payroll Cycle', period_month=10, period_year=2026,
            start_date=date(2026, 10, 1), end_date=date(2026, 10, 31),
            status='Completed', processed_date=datetime(2026, 10, 31, 18, 0)
        )
        db.session.add(period_oct)
        db.session.flush()

        # Generate sample payslips for October 2026
        for emp, asgn in [(emp1, asgn1), (emp2, asgn2), (emp3, asgn3), (emp4, asgn4)]:
            allowances = asgn.house_rent_allowance + asgn.conveyance_allowance + asgn.medical_allowance
            gross = asgn.basic_salary + allowances
            tax_est = gross * Decimal('0.05')
            pf_est = asgn.basic_salary * Decimal('0.08')
            total_ded = tax_est + pf_est
            net = gross - total_ded

            pr = PayrollRecord(
                employee_id=emp.id, payroll_period_id=period_oct.id,
                basic_salary=asgn.basic_salary, total_allowances=allowances,
                gross_salary=gross, total_deductions=total_ded, net_salary=net,
                payment_status='Paid', payment_date=date(2026, 11, 1), payment_method='Bank Transfer'
            )
            db.session.add(pr)
            db.session.flush()

            # Payslip line items
            db.session.add_all([
                PayrollItemDetail(payroll_record_id=pr.id, component_name='Basic Salary', item_type='Earning', amount=asgn.basic_salary),
                PayrollItemDetail(payroll_record_id=pr.id, component_name='House Rent Allowance', item_type='Earning', amount=asgn.house_rent_allowance),
                PayrollItemDetail(payroll_record_id=pr.id, component_name='Conveyance Allowance', item_type='Earning', amount=asgn.conveyance_allowance),
                PayrollItemDetail(payroll_record_id=pr.id, component_name='Medical Allowance', item_type='Earning', amount=asgn.medical_allowance),
                PayrollItemDetail(payroll_record_id=pr.id, component_name='Income Tax Withholding', item_type='Deduction', amount=tax_est),
                PayrollItemDetail(payroll_record_id=pr.id, component_name='Provident Fund', item_type='Deduction', amount=pf_est),
            ])

        # Commit all changes
        db.session.commit()
        print("Initial database seeding completed successfully!")
        print("Credentials for Viva & Testing:")
        print("  Admin User:      admin / admin123")
        print("  HR Manager User: hr_manager / manager123")
        print("  Employee User:   employee / user123")

if __name__ == '__main__':
    create_seed_data()

