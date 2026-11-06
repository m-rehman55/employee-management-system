"""
verify_models.py - Programmatically audits and verifies the 40+ SQLAlchemy models.
Outputs total count, table names, columns, and foreign keys.
"""
from flask import Flask
from config import TestConfig
from extensions import db
import models  # Imports all 45 models

def run_verification():
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    db.init_app(app)

    with app.app_context():
        # Create all tables in memory to verify schema validity
        db.create_all()

        tables = db.metadata.tables
        print(f"==================================================")
        print(f"DATABASE VERIFICATION REPORT")
        print(f"Total SQLAlchemy Tables in Metadata: {len(tables)}")
        print(f"Minimum Required: 40")
        print(f"Status: {'PASSED (Requirement Exceeded)' if len(tables) >= 40 else 'FAILED'}")
        print(f"==================================================")
        
        # Categorized audit
        categories = {
            "Department Management": [
                'department_locations', 'departments', 'department_budgets',
                'department_policies', 'department_projects', 'designations', 'department_transfers'
            ],
            "Employee Management": [
                'employees', 'employee_profiles', 'employee_emergency_contacts',
                'employee_education', 'employee_experience', 'employee_documents',
                'employee_bank_details', 'employee_skills', 'employee_notes', 'employee_asset_assignments'
            ],
            "Leave Management": [
                'leave_types', 'leave_policies', 'leave_balances',
                'leave_requests', 'leave_approvals', 'leave_attachments',
                'company_holidays', 'leave_encashments'
            ],
            "Attendance Management": [
                'work_shifts', 'employee_shift_schedules', 'attendance_records',
                'attendance_corrections', 'overtime_records', 'attendance_summaries',
                'biometric_devices', 'attendance_breaks'
            ],
            "Payroll Management": [
                'salary_structures', 'salary_components', 'employee_salary_assignments',
                'payroll_periods', 'payroll_records', 'payroll_item_details',
                'employee_deductions', 'employee_bonuses'
            ],
            "Auth & System Infrastructure": [
                'roles', 'users', 'audit_logs', 'system_settings'
            ]
        }

        total_checked = 0
        for category, table_list in categories.items():
            print(f"\n--- {category} ({len(table_list)} tables) ---")
            for t_name in table_list:
                table = tables.get(t_name)
                if table is not None:
                    total_checked += 1
                    cols = [c.name for c in table.columns]
                    fks = [f"{fk.parent.name}->{fk.target_fullname}" for fk in table.foreign_keys]
                    print(f" [OK] Table: {t_name:<28} | Columns: {len(cols):<2} | FKs: {len(fks)}")
                else:
                    print(f" [MISSING] Table: {t_name}")

        print(f"\n==================================================")
        print(f"Summary: Verified {total_checked} tables across all 5 modules + Auth/Audit.")
        print(f"==================================================")
        assert len(tables) >= 40, f"Expected at least 40 tables, found {len(tables)}"

if __name__ == '__main__':
    run_verification()

