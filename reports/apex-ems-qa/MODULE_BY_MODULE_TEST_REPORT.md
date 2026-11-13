# Module-by-Module Test Report

| Module | Verified locally | Result | Notes |
|---|---|---|---|
| Authentication | login success/failure, session, remember cookie, logout, external `next` rejection | Pass | Demo credentials absent from login HTML |
| Dashboard/theme | dashboard access, theme toggle, external referrer rejection | Pass | System preference is default; cookie is explicit override |
| Departments | CRUD and validation | Pass | Covered by automated suite |
| Employees | CRUD and validation | Pass | Employee write access denied; self-only profile read added |
| Leave | CRUD, employee submission, approval decision, balance movement | Pass | Pending/Approved/Rejected path covered |
| Attendance | duplicate/date/time validation, CRUD | Pass | Employee records filtered to own data |
| Payroll | duplicate period, calculations, CRUD | Pass | Employee records filtered to own data |
| Database | metadata/table verification and persistence tests | Pass | 45 tables; persistence test included |
| Browser UI | visual, mobile, console, keyboard, print | Blocked | Chrome connector unavailable |

The automated suite result was `21 passed in 9.16s` using `venv\\Scripts\\python.exe -m pytest -q`.

