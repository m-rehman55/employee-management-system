# Defect Register

| ID | Severity | Status | Finding / evidence |
|---|---|---|---|
| DEF-001 | P1 | Fixed | Added dependency-free CSRF token generation, browser form injection, and server-side validation for state-changing requests. |
| DEF-002 | P1 | Open | No migration framework was found; `create_all()` does not safely evolve production schemas. |
| DEF-003 | P1 | Open | Production persistence depends on SQLite configuration; verify managed persistent storage before deployment. |
| DEF-004 | P2 | Blocked verification | Browser console, responsive layout, print output, and accessibility behavior could not be inspected because Chrome connector was unavailable. |
| DEF-005 | P2 | Fixed/extended | Added overlap, pending-balance, date-window, pending-only edit, and approval balance checks; broader policy/holiday rules remain. |
| DEF-006 | P2 | Open | Payroll input status/payment method values are not constrained against a server-side allow-list. |

No unverified browser-only defects are presented as confirmed defects.

