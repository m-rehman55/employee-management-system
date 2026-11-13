# Apex EMS Master Audit Report

Date: 2026-11-13  |  Scope: local Flask application in this workspace

## Executive result

The application is functional for the tested local workflows and the automated suite is green (`21 passed`). The schema contains 47 registered SQLAlchemy tables. Authentication, admin-reviewed password reset, CSRF, role checks, leave approval, safe redirects, employee self-service privacy, soft deactivation, and SQLite backup were reviewed and improved.

Release is **conditional**, not fully production-ready. Browser-level acceptance, responsive screenshots, console/network inspection, migrations, SMTP configuration, and production database persistence remain open or unverified.

## Architecture inventory

- Flask application factory in `app.py`, SQLAlchemy extension in `extensions.py`, SQLite configuration in `config.py`.
- Blueprints: authentication, dashboard, employees, departments, leaves, attendance, payroll.
- Server-rendered Jinja templates with Bootstrap/Icon assets and project CSS/JS.
- 47 SQLAlchemy tables: department (7), employee (10), leave (8), attendance (8), payroll (8), auth/system (6 including password reset tokens and admin requests).
- Local database: `instance/ems.db`; no migration framework was found.

## Completed fixes in this audit cycle

- Removed hard-coded testing credentials from the login UI.
- Added system-preference theme behavior with explicit light/dark override cookies and dark-mode contrast rules.
- Restricted Employee views to their own employee, attendance, payroll, and leave records.
- Added server-side 403 protection for cross-employee detail access.
- Added leave submission and HR/Admin decision workflow with balance updates.
- Added safe same-host redirect handling and a 403 error page.
- Added expiring password reset/change-password flow, CSRF protection, employee soft deactivation/restore, and admin SQLite backups.
- Replaced deprecated ORM access/time calls in application paths.

## Blocking evidence gaps

- Chrome/browser connector was unavailable in this run; no screenshot, browser console, Lighthouse, or real-user session is claimed.
- No real users were available; usability evidence is simulated through automated requests and source inspection.

## Priority actions before production

1. Add Alembic/Flask-Migrate and a repeatable production migration process.
2. Move production data to a managed persistent database; SQLite on ephemeral hosting is not a durable deployment design.
3. Keep password-reset handoff inside approved Administrator channels.
4. Run the full browser/responsive/accessibility pass with Chrome connected.
5. Add payroll value allow-lists and broader leave policy/holiday rules.

