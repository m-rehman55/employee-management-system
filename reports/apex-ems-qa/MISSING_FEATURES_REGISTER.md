# Missing Features Register

| ID | Priority | Missing capability | Recommendation |
|---|---|---|---|
| MF-001 | P1 | CSRF protection and security regression tests | Add before external exposure |
| MF-002 | P1 | Database migrations/backups/restore procedure | Add before schema changes or production rollout |
| MF-003 | P1 | Persistent production database | Use managed PostgreSQL/MySQL rather than ephemeral SQLite |
| MF-004 | P2 | Leave attachments, holidays, encashments, correction approvals and overtime UI | Implement only when required by business scope |
| MF-005 | P2 | Pagination/export/search scalability | Add for larger employee, attendance and payroll datasets |
| MF-006 | Partial | Admin-reviewed password reset/change-password added; lockout/rate limiting and MFA remain | Keep reset-link handoff inside approved Administrator channels |
| MF-007 | P2 | Browser-based visual/accessibility acceptance suite | Add Playwright/Chrome checks when browser access is available |

The database has tables for several future capabilities, but a table existing does not mean the corresponding workflow is implemented.

