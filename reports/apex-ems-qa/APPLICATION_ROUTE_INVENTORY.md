# Application Route Inventory

Generated from `app.url_map` on 2026-11-13. 31 application rules were registered, excluding `/static/<path:filename>`.

| Area | Routes | Methods | Access expectation |
|---|---|---|---|
| Auth | `/login`, `/logout` | GET/POST | Public login; logout session action |
| Dashboard | `/`, `/dashboard`, `/toggle-theme` | GET | Authenticated |
| Employees | `/employees/`, `/<id>`, `/add`, `/<id>/edit`, `/<id>/delete` | GET; GET/POST; POST | Read authenticated; writes Admin/HR; Employee self-only read |
| Departments | `/departments/`, `/<id>`, `/add`, `/<id>/edit`, `/<id>/delete` | GET; GET/POST; POST | Read authenticated; writes Admin/HR |
| Leave | `/leaves/`, `/<id>`, `/add`, `/<id>/edit`, `/<id>/decision`, `/<id>/delete` | GET; GET/POST; POST | Employee self-service; approval/destructive actions Admin/HR |
| Attendance | `/attendance/`, `/<id>`, `/add`, `/<id>/edit`, `/<id>/delete` | GET; GET/POST; POST | Employee self-only read; writes Admin/HR |
| Payroll | `/payroll/`, `/<id>`, `/add`, `/<id>/edit`, `/<id>/delete` | GET; GET/POST; POST | Employee self-only read; writes Admin/HR |

Notes: Flask automatically adds `HEAD` and `OPTIONS`. All protected routes use `login_required`; write routes use `role_required` except employee leave submission. Static serving is framework-managed.

