# Employee Management System (EMS) — Flask Web Application

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/m-rehman55/employee-management-system)

**Course:** Web Engineering (CSE601330)  
**Scope:** Weeks 5–8 (Flask, Jinja2, SQLAlchemy, Sessions, Cookies)  
**Program:** BS Artificial Intelligence / BS Data Science  
**Target Marks:** 90–100 / 100  
**GitHub Repository:** [https://github.com/m-rehman55/employee-management-system](https://github.com/m-rehman55/employee-management-system)  

---

## 1. Project Overview & Purpose

The **Employee Management System (EMS)** is an enterprise-grade, beginner-friendly web application engineered using the **Python Flask framework**, **Flask-SQLAlchemy ORM**, **SQLite**, **Jinja2 templating**, and **Bootstrap 5**.

The system strictly adheres to the approved university project scope, providing comprehensive management capabilities across **exactly five functional core modules**:
1. **Employee Management:** Complete lifecycle management, personal profiles, emergency contacts, academic qualifications, employment histories, banking credentials, skills inventory, and corporate asset tracking.
2. **Department Management:** Organizational branch locations, hierarchical structure, operational policies, project assignments, job designations, and fiscal budget monitoring.
3. **Leave Management:** Custom leave classification (Annual, Sick, Casual, Unpaid), annual entitlement balance ledgers, online request submission, supervisor approval audit trails, medical certificates, and leave encashment workflows.
4. **Attendance Management:** Daily biometric clock-in/clock-out tracking, multi-shift scheduling, work-hour calculation, break logs, overtime tracking, missed punch corrections, and monthly aggregates.
5. **Payroll Management:** Graded salary structures, earnings/deductions component catalog, individual employee packages, wage cycle generation, automated tax/PF deductions, itemized printable payslips, and payment auditing.

Supporting infrastructure includes **Flask session authentication**, **secure cookie demonstration**, **tamper-evident audit logging**, **server-side validation**, and the **Post/Redirect/Get (PRG) pattern**.

---

## 2. Technologies Used

- **Backend:** Python 3.12+ / Flask 3.0.3
- **ORM & Database:** SQLAlchemy 2.0+ / Flask-SQLAlchemy 3.1.1 with SQLite
- **Authentication & Security:** Werkzeug 3.0.3 (`generate_password_hash`, `check_password_hash`), Flask Session Management
- **Frontend & Templating:** HTML5, CSS3, Bootstrap 5.3.3, Bootstrap Icons 1.11.3, Jinja2
- **Testing & Verification:** Pytest 8.2.2

---

## 3. Python Version Requirements

- **Python Version:** Python 3.10, 3.11, 3.12, or 3.13 (Tested on Python 3.12.10 on Windows)
- **Pip:** Package installer for Python 3

---

## 4. Installation & Setup Instructions

Follow these step-by-step terminal commands to set up the project locally:

### Step 1: Open Terminal in Project Directory
```powershell
cd "d:\Desktop\WEB DEVELOPMENT"
```

### Step 2: Create Python Virtual Environment
```powershell
python -m venv venv
```

### Step 3: Activate Virtual Environment
- **On Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **On Windows (Command Prompt):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **On macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Initialize & Seed Database
Run the automated seed script to create all 45 tables and populate realistic enterprise demo data:
```powershell
python seed.py
```

### Step 6: Verify Database Models (Optional Programmatic Audit)
Verify that all 45 models exist in the SQLAlchemy schema:
```powershell
python verify_models.py
```

### Step 7: Run the Application
```powershell
python app.py
```
Open your web browser and navigate to: **`http://127.0.0.1:5000`**

---

## 5. Development Credentials for Viva & Testing

The system is pre-configured with three role-based accounts for testing:

| Role | Username | Password | Purpose |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Full administrative control, all 5 modules, settings, and logs |
| **HR Manager** | `hr_manager` | `manager123` | Employee lifecycle, leave approvals, attendance, payroll |
| **Employee** | `employee` | `user123` | Employee portal self-service |

---

## 6. Project Folder Structure

```
d:\Desktop\WEB DEVELOPMENT\
├── app.py                      # Main entry point & Flask Application Factory
├── config.py                   # App configurations (Secret keys, DB URI, Session/Cookie settings)
├── extensions.py               # Shared SQLAlchemy db instance (prevents circular imports)
├── requirements.txt            # Python dependencies (Flask, Flask-SQLAlchemy, pytest)
├── seed.py                     # Database initialization and sample data seeder
├── verify_models.py            # Automated audit script verifying 45 models in SQLite
├── models/                     # 45 genuine SQLAlchemy database models
│   ├── __init__.py             # Exports db and registers all 45 models
│   ├── department.py           # 7 Department Management models
│   ├── employee.py             # 10 Employee Management models
│   ├── leave.py                # 8 Leave Management models
│   ├── attendance.py           # 8 Attendance Management models
│   ├── payroll.py              # 8 Payroll Management models
│   └── auth.py                 # 4 Authentication, Audit & System models
├── routes/                     # Modular Flask Blueprints (Views & CRUD Controllers)
│   ├── __init__.py
│   ├── auth_routes.py          # /login, /logout, session & cookie handlers
│   ├── dashboard_routes.py     # / and /dashboard (real-time calculated statistics)
│   ├── employee_routes.py      # /employees CRUD endpoints & profile views
│   ├── department_routes.py    # /departments CRUD endpoints & member views
│   ├── leave_routes.py         # /leaves CRUD endpoints & approval trails
│   ├── attendance_routes.py    # /attendance CRUD endpoints & punch logs
│   └── payroll_routes.py       # /payroll CRUD endpoints & printable payslips
├── utils/                      # Helper modules
│   ├── __init__.py
│   ├── decorators.py           # @login_required, @role_required session decorators
│   ├── audit.py                # log_audit helper for compliance logging
│   └── validators.py           # Server-side validation routines (email, date, numeric)
├── templates/                  # Jinja2 template hierarchy
│   ├── base.html               # Shared master layout, sidebar, navbar, flash alerts
│   ├── auth/
│   │   └── login.html          # Professional login interface with viva credentials card
│   ├── dashboard/
│   │   └── index.html          # Executive dashboard with dynamic database metrics
│   ├── employees/
│   │   ├── list.html           # Directory table with search and department filtering
│   │   ├── detail.html         # Comprehensive profile (personal, contacts, assets, skills)
│   │   └── form.html           # Add / Edit form with server-side validation error handling
│   ├── departments/
│   │   ├── list.html           # Department listing with metrics and manager assignment
│   │   ├── detail.html         # Department detail (staff list, projects, policies, budget)
│   │   └── form.html           # Add / Edit department form
│   ├── leaves/
│   │   ├── list.html           # Leave applications table with status filter
│   │   ├── detail.html         # Application details, remaining balance, approval history
│   │   └── form.html           # Add / Edit leave request with auto-day calculation
│   ├── attendance/
│   │   ├── list.html           # Daily attendance logs with date picker filter
│   │   ├── detail.html         # Punch in/out hours, break records, and notes
│   │   └── form.html           # Add / Edit attendance record
│   └── payroll/
│       ├── list.html           # Payslip listing with wage cycle and payment status filter
│       ├── detail.html         # Official printable salary payslip view
│       └── form.html           # Add / Edit payslip with gross and net wage calculation
├── static/
│   ├── css/
│   │   └── style.css           # Modern custom styles, cards, badges, and dark theme
│   └── js/
│       └── main.js            # Auto-dismissing alerts, delete confirmation popups
└── tests/
    ├── __init__.py
    ├── test_system.py          # Authentication, CRUD, validation, security and error tests
    └── test_persistence.py     # Verifies SQLite file persistence across app restarts
```

---

## 7. Explanation of the 45 Database Models

Every model is an actual database table with primary keys, foreign keys, relationships, and business integrity constraints strictly supporting the 5 approved modules:

### Module 1: Department Management (7 Models)
1. **`Department`** (`departments`): Core organizational unit record (`id`, `code`, `name`, `description`, `manager_id`, `location_id`, `budget`, `is_active`, `created_at`).
2. **`DepartmentLocation`** (`department_locations`): Physical branch locations and office buildings housing departments.
3. **`DepartmentBudget`** (`department_budgets`): Fiscal year budget allocations, expenditures, and remaining funds.
4. **`DepartmentPolicy`** (`department_policies`): Department-specific standard operating procedures and guidelines.
5. **`DepartmentProject`** (`department_projects`): Internal operational initiatives assigned to departments.
6. **`Designation`** (`designations`): Job positions and compensation pay bands linked to departments.
7. **`DepartmentTransferHistory`** (`department_transfers`): Audit log of employee reassignments between departments.

### Module 2: Employee Management (10 Models)
8. **`Employee`** (`employees`): Central employee profile master record (`id`, `employee_code`, `first_name`, `last_name`, `email`, `phone`, `date_of_birth`, `gender`, `hire_date`, `department_id`, `designation_id`, `employment_type`, `status`).
9. **`EmployeeProfile`** (`employee_profiles`): Extended biographical data, national ID (CNIC), blood group, and residential addresses.
10. **`EmployeeEmergencyContact`** (`employee_emergency_contacts`): Emergency contacts for employee medical/safety alerts.
11. **`EmployeeEducation`** (`employee_education`): Academic degrees, institutions, graduation years, and GPAs.
12. **`EmployeeExperience`** (`employee_experience`): Prior professional employment background, titles, and tenures.
13. **`EmployeeDocument`** (`employee_documents`): Uploaded contract agreements, certifications, and verification status.
14. **`EmployeeBankDetail`** (`employee_bank_details`): Direct deposit banking credentials for salary disbursals.
15. **`EmployeeSkill`** (`employee_skills`): Technical competencies, proficiency ratings, and certifications.
16. **`EmployeeNote`** (`employee_notes`): Confidential HR performance and appraisal remarks.
17. **`EmployeeAssetAssignment`** (`employee_asset_assignments`): Company hardware (laptops, badges) assigned to employees.

### Module 3: Leave Management (8 Models)
18. **`LeaveType`** (`leave_types`): Categories of leave (Annual, Sick, Casual, Maternity, Unpaid).
19. **`LeavePolicy`** (`leave_policies`): Accrual caps, carryover limits, and minimum service requirements.
20. **`LeaveBalance`** (`leave_balances`): Annual allocated, used, and remaining balance ledger per employee.
21. **`LeaveRequest`** (`leave_requests`): Formal leave applications (`id`, `employee_id`, `leave_type_id`, `start_date`, `end_date`, `total_days`, `reason`, `status`).
22. **`LeaveApproval`** (`leave_approvals`): Multi-tier supervisor approval and rejection decision trail.
23. **`LeaveAttachment`** (`leave_attachments`): Medical certificates or proof files supporting leave requests.
24. **`CompanyHoliday`** (`company_holidays`): Public holidays and company off-days schedule.
25. **`LeaveEncashment`** (`leave_encashments`): Conversion of accumulated unused leaves into cash payouts.

### Module 4: Attendance Management (8 Models)
26. **`WorkShift`** (`work_shifts`): Configured work shift timetables (start time, end time, grace periods).
27. **`EmployeeShiftSchedule`** (`employee_shift_schedules`): Shift assignments over calendar spans.
28. **`AttendanceRecord`** (`attendance_records`): Daily check-in/out timestamps and worked hours calculations.
29. **`AttendanceCorrectionRequest`** (`attendance_corrections`): Workflow for employees to rectify missed punches.
30. **`OvertimeRecord`** (`overtime_records`): Approved extra working hours tracking and multipliers.
31. **`AttendanceSummary`** (`attendance_summaries`): Monthly aggregated attendance metrics feeding into payroll.
32. **`BiometricDevice`** (`biometric_devices`): Physical punch hardware terminals and turnstiles.
33. **`AttendanceBreak`** (`attendance_breaks`): Mid-shift pauses tracking (lunch, tea, rest).

### Module 5: Payroll Management (8 Models)
34. **`SalaryStructure`** (`salary_structures`): Standardized pay grade templates and salary bands.
35. **`SalaryComponent`** (`salary_components`): Master catalog of earnings (Basic, HRA) and deductions (PF, Tax).
36. **`EmployeeSalaryAssignment`** (`employee_salary_assignments`): Individual employee salary package allocation.
37. **`PayrollPeriod`** (`payroll_periods`): Monthly wage processing cycles (e.g., November 2026).
38. **`PayrollRecord`** (`payroll_records`): Master payslip records (`basic_salary`, `total_allowances`, `gross_salary`, `total_deductions`, `net_salary`, `payment_status`).
39. **`PayrollItemDetail`** (`payroll_item_details`): Line-item earnings and deductions breakdown on payslips.
40. **`EmployeeDeduction`** (`employee_deductions`): Recurring statutory, tax, or loan deductions.
41. **`EmployeeBonus`** (`employee_bonuses`): Performance bonuses, annual awards, and festival incentives.

### Supporting Infrastructure & Auth Models (4 Models)
42. **`User`** (`users`): Authentication credentials, password hashing, and login state.
43. **`Role`** (`roles`): Role-based access control (Admin, HR Manager, Employee).
44. **`AuditLog`** (`audit_logs`): Tamper-evident audit trail for all CRUD operations and logins.
45. **`SystemSetting`** (`system_settings`): Enterprise global configuration parameters (Company name, currency).

---

## 8. Automated Testing & Verification

Execute the complete automated test suite:
```powershell
.\venv\Scripts\python.exe -m pytest -v
```
All **13 automated tests** execute with 100% pass rate:
- `test_forty_models_requirement`: Programmatically verifies 45 tables in SQLAlchemy metadata.
- `test_unauthenticated_access_redirect`: Validates session security and login redirects.
- `test_login_invalid_credentials`: Validates server-side auth validation.
- `test_login_success_and_cookie_demonstration`: Verifies session creation and cookie storage.
- `test_logout`: Verifies session teardown.
- `test_department_crud`: Full Create, Read, Update, Delete test for Department Management.
- `test_employee_crud`: Full Create, Read, Update, Delete test for Employee Management.
- `test_employee_validation_duplicate_code`: Verifies uniqueness constraints on employee codes.
- `test_leave_crud`: Full Create, Read, Update, Delete test for Leave Management.
- `test_attendance_crud`: Full Create, Read, Update, Delete test for Attendance Management.
- `test_payroll_crud`: Full Create, Read, Update, Delete test for Payroll Management.
- `test_404_error_handler`: Verifies custom 404 page handler.
- `test_database_persistence_across_restarts`: Verifies physical SQLite disk persistence across application restarts.

