"""
models/employee.py - Employee Management models (10 models).
Handles employees, personal profiles, emergency contacts, education, experience, documents, bank details, skills, notes, and asset assignments.
"""
from datetime import datetime, date
from extensions import db
from utils.time import utc_now


class Employee(db.Model):
    """Core employee master record."""
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)  # Male, Female, Other
    hire_date = db.Column(db.Date, nullable=False, default=date.today)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    designation_id = db.Column(db.Integer, db.ForeignKey('designations.id'), nullable=True)
    employment_type = db.Column(db.String(30), default='Full-Time')  # Full-Time, Part-Time, Contract, Intern
    status = db.Column(db.String(30), default='Active')  # Active, On Leave, Terminated, Resigned
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    department = db.relationship('Department', foreign_keys=[department_id], back_populates='employees')
    designation = db.relationship('Designation', back_populates='employees')
    profile = db.relationship('EmployeeProfile', uselist=False, back_populates='employee', cascade='all, delete-orphan')
    emergency_contacts = db.relationship('EmployeeEmergencyContact', back_populates='employee', cascade='all, delete-orphan', lazy=True)
    education = db.relationship('EmployeeEducation', back_populates='employee', cascade='all, delete-orphan', lazy=True)
    experience = db.relationship('EmployeeExperience', back_populates='employee', cascade='all, delete-orphan', lazy=True)
    documents = db.relationship('EmployeeDocument', back_populates='employee', cascade='all, delete-orphan', lazy=True)
    bank_details = db.relationship('EmployeeBankDetail', back_populates='employee', cascade='all, delete-orphan', lazy=True)
    skills = db.relationship('EmployeeSkill', back_populates='employee', cascade='all, delete-orphan', lazy=True)
    notes = db.relationship('EmployeeNote', back_populates='employee', cascade='all, delete-orphan', lazy=True)
    assets = db.relationship('EmployeeAssetAssignment', back_populates='employee', cascade='all, delete-orphan', lazy=True)

    # Cross-module relationships
    leave_requests = db.relationship('LeaveRequest', back_populates='employee', cascade='all, delete-orphan', lazy=True)
    leave_balances = db.relationship('LeaveBalance', back_populates='employee', cascade='all, delete-orphan', lazy=True)
    attendance_records = db.relationship('AttendanceRecord', back_populates='employee', cascade='all, delete-orphan', lazy=True)
    payroll_records = db.relationship('PayrollRecord', back_populates='employee', cascade='all, delete-orphan', lazy=True)
    salary_assignment = db.relationship('EmployeeSalaryAssignment', uselist=False, back_populates='employee', cascade='all, delete-orphan')
    user = db.relationship('User', uselist=False, back_populates='employee')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Employee {self.employee_code} - {self.full_name}>"


class EmployeeProfile(db.Model):
    """Deep personal identity, address, and biographical records."""
    __tablename__ = 'employee_profiles'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), unique=True, nullable=False)
    national_id = db.Column(db.String(50), nullable=True)  # CNIC / SSN / Passport
    marital_status = db.Column(db.String(20), default='Single')  # Single, Married, Divorced
    blood_group = db.Column(db.String(10), nullable=True)
    nationality = db.Column(db.String(50), default='Pakistani')
    current_address = db.Column(db.Text, nullable=True)
    permanent_address = db.Column(db.Text, nullable=True)
    personal_email = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    employee = db.relationship('Employee', back_populates='profile')

    def __repr__(self):
        return f"<EmployeeProfile Emp:{self.employee_id} - CNIC:{self.national_id}>"


class EmployeeEmergencyContact(db.Model):
    """Emergency contacts for employee safety and medical alerts."""
    __tablename__ = 'employee_emergency_contacts'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)  # Spouse, Parent, Sibling, Friend
    phone_number = db.Column(db.String(30), nullable=False)
    alternate_phone = db.Column(db.String(30), nullable=True)
    address = db.Column(db.Text, nullable=True)
    is_primary = db.Column(db.Boolean, default=True)

    employee = db.relationship('Employee', back_populates='emergency_contacts')

    def __repr__(self):
        return f"<EmergencyContact {self.contact_name} ({self.relationship})>"


class EmployeeEducation(db.Model):
    """Academic credentials, degrees, and institutions."""
    __tablename__ = 'employee_education'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    degree_title = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(150), nullable=False)
    field_of_study = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    grade_or_gpa = db.Column(db.String(20), nullable=True)

    employee = db.relationship('Employee', back_populates='education')

    def __repr__(self):
        return f"<Education {self.degree_title} - {self.institution}>"


class EmployeeExperience(db.Model):
    """Previous professional employment history."""
    __tablename__ = 'employee_experience'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    responsibilities = db.Column(db.Text, nullable=True)
    leaving_reason = db.Column(db.String(255), nullable=True)

    employee = db.relationship('Employee', back_populates='experience')

    def __repr__(self):
        return f"<Experience {self.job_title} at {self.company_name}>"


class EmployeeDocument(db.Model):
    """Uploaded identification proofs, resume, and contract metadata."""
    __tablename__ = 'employee_documents'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # Resume, CNIC, Degree, Contract
    document_name = db.Column(db.String(150), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=utc_now)
    verification_status = db.Column(db.String(30), default='Verified')  # Pending, Verified, Rejected

    employee = db.relationship('Employee', back_populates='documents')

    def __repr__(self):
        return f"<Document {self.document_type}: {self.document_name}>"


class EmployeeBankDetail(db.Model):
    """Direct deposit bank account details for payroll disbursals."""
    __tablename__ = 'employee_bank_details'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    branch_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50), nullable=False)
    account_holder_name = db.Column(db.String(100), nullable=False)
    swift_ifsc_code = db.Column(db.String(30), nullable=True)
    is_primary = db.Column(db.Boolean, default=True)

    employee = db.relationship('Employee', back_populates='bank_details')

    def __repr__(self):
        return f"<BankDetail {self.bank_name} - {self.account_number}>"


class EmployeeSkill(db.Model):
    """Technical and professional competencies."""
    __tablename__ = 'employee_skills'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    proficiency_level = db.Column(db.String(30), default='Intermediate')  # Beginner, Intermediate, Expert
    years_experience = db.Column(db.Numeric(4, 1), default=1.0)
    is_certified = db.Column(db.Boolean, default=False)

    employee = db.relationship('Employee', back_populates='skills')

    def __repr__(self):
        return f"<Skill {self.skill_name} ({self.proficiency_level})>"


class EmployeeNote(db.Model):
    """Confidential administrative and performance evaluation notes."""
    __tablename__ = 'employee_notes'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    note_title = db.Column(db.String(150), nullable=False)
    note_content = db.Column(db.Text, nullable=False)
    note_type = db.Column(db.String(50), default='General')  # General, Performance, Commendation, Disciplinary
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    employee = db.relationship('Employee', back_populates='notes')

    def __repr__(self):
        return f"<EmployeeNote {self.note_title} ({self.note_type})>"


class EmployeeAssetAssignment(db.Model):
    """Company equipment (laptop, badge, phone) assigned to employee."""
    __tablename__ = 'employee_asset_assignments'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    asset_name = db.Column(db.String(100), nullable=False)
    asset_tag = db.Column(db.String(50), unique=True, nullable=False)
    serial_number = db.Column(db.String(100), nullable=True)
    issued_date = db.Column(db.Date, default=date.today)
    return_date = db.Column(db.Date, nullable=True)
    condition_notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='Issued')  # Issued, Returned, Damaged, Lost

    employee = db.relationship('Employee', back_populates='assets')

    def __repr__(self):
        return f"<AssetAssignment {self.asset_name} ({self.asset_tag})>"

