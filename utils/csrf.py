"""Small dependency-free CSRF protection for server-rendered forms."""
import secrets
from flask import session, request, abort


def csrf_token():
    token = session.get('_csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['_csrf_token'] = token
    return token


def validate_csrf_request():
    supplied = request.form.get('_csrf_token') or request.headers.get('X-CSRF-Token')
    expected = session.get('_csrf_token')
    if not expected or not supplied or not secrets.compare_digest(supplied, expected):
        abort(400, description='Invalid or missing form security token.')
