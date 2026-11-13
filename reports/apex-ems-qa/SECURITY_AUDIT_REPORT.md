# Security Audit Report

## Passed or improved

- Passwords use the model password hashing path rather than being rendered in the login page.
- Protected routes use authentication and role decorators.
- Employee self-service records are filtered server-side; cross-record detail requests return 403.
- Login `next` and theme referrer redirects are restricted to safe same-host/local paths.
- Destructive routes use POST.
- A 403 handler is present.

## Open risks

- CSRF protection is implemented for state-changing requests; browser forms receive a session token and the server rejects missing/invalid tokens.
- Login rate limiting, account lockout, MFA, password reset and rotation are not implemented.
- Production secret/database configuration needs deployment-specific hardening review.
- Default seed behavior must not expose or reuse development credentials in production.

Security status: **needs hardening before production**.

