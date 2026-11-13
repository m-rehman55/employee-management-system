# Fix and Regression Log

| Fix | Verification |
|---|---|
| Removed login credential panel and demo credential text | Login exposure test passed |
| Added OS-aware light/dark theme with explicit override | Theme tests passed; browser visual check pending |
| Safe local redirect handling | External `next` and referrer tests passed |
| Employee self-only employee/attendance/payroll/leave reads | Route filters and 403 guards reviewed; automated suite green |
| Leave submit/approve/reject flow and balance updates | Leave CRUD/decision test passed |
| Role-based write/delete enforcement | Employee mutation test passed |
| ORM/time deprecation cleanup | Compile and full test suite passed |
| Mobile/reduced-motion CSS improvements | Source reviewed; browser viewport check pending |
| Password reset/change-password flow with expiring single-use tokens | Automated reset test passed; SMTP delivery requires deployment configuration |
| Employee soft deactivation/restore | Automated lifecycle test passed; historical records are preserved |
| SQLite admin backup action | Implemented; needs production persistent-database backup strategy |
| CSRF protection for state-changing requests | Compile and full test suite passed |

No database reset, user-data deletion, deployment, push, merge, or external message was performed.

