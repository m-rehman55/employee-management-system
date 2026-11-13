"""
models/__init__.py - Registers and exports all 47 SQLAlchemy database models.
"""
from extensions import db

# Module 1: Department Management (7 models)
from models.department import (
    DepartmentLocation,
    Department,
    DepartmentBudget,
    DepartmentPolicy,
    DepartmentProject,
    Designation,
    DepartmentTransferHistory,
)

# Module 2: Employee Management (10 models)
from models.employee import (
    Employee,
    EmployeeProfile,
    EmployeeEmergencyContact,
    EmployeeEducation,
    EmployeeExperience,
    EmployeeDocument,
    EmployeeBankDetail,
    EmployeeSkill,
    EmployeeNote,
    EmployeeAssetAssignment,
)

# Module 3: Leave Management (8 models)
from models.leave import (
    LeaveType,
    LeavePolicy,
    LeaveBalance,
    LeaveRequest,
    LeaveApproval,
    LeaveAttachment,
    CompanyHoliday,
    LeaveEncashment,
)

# Module 4: Attendance Management (8 models)
from models.attendance import (
    WorkShift,
    EmployeeShiftSchedule,
    AttendanceRecord,
    AttendanceCorrectionRequest,
    OvertimeRecord,
    AttendanceSummary,
    BiometricDevice,
    AttendanceBreak,
)

# Module 5: Payroll Management (8 models)
from models.payroll import (
    SalaryStructure,
    SalaryComponent,
    EmployeeSalaryAssignment,
    PayrollPeriod,
    PayrollRecord,
    PayrollItemDetail,
    EmployeeDeduction,
    EmployeeBonus,
)

# Module 6: Authentication & System Infrastructure (4 models)
from models.auth import (
    Role,
    User,
    PasswordResetToken,
    PasswordResetRequest,
    AuditLog,
    SystemSetting,
)

__all__ = [
    'db',
    # Department
    'DepartmentLocation',
    'Department',
    'DepartmentBudget',
    'DepartmentPolicy',
    'DepartmentProject',
    'Designation',
    'DepartmentTransferHistory',
    # Employee
    'Employee',
    'EmployeeProfile',
    'EmployeeEmergencyContact',
    'EmployeeEducation',
    'EmployeeExperience',
    'EmployeeDocument',
    'EmployeeBankDetail',
    'EmployeeSkill',
    'EmployeeNote',
    'EmployeeAssetAssignment',
    # Leave
    'LeaveType',
    'LeavePolicy',
    'LeaveBalance',
    'LeaveRequest',
    'LeaveApproval',
    'LeaveAttachment',
    'CompanyHoliday',
    'LeaveEncashment',
    # Attendance
    'WorkShift',
    'EmployeeShiftSchedule',
    'AttendanceRecord',
    'AttendanceCorrectionRequest',
    'OvertimeRecord',
    'AttendanceSummary',
    'BiometricDevice',
    'AttendanceBreak',
    # Payroll
    'SalaryStructure',
    'SalaryComponent',
    'EmployeeSalaryAssignment',
    'PayrollPeriod',
    'PayrollRecord',
    'PayrollItemDetail',
    'EmployeeDeduction',
    'EmployeeBonus',
    # Auth & System
    'Role',
    'User',
    'PasswordResetToken',
    'PasswordResetRequest',
    'AuditLog',
    'SystemSetting',
]

