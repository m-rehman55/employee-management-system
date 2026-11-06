"""
utils/validators.py - Server-side validation utilities.
Enforces data integrity independently of client-side browser forms.
"""
import re
from datetime import datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def validate_email(email):
    """Validates email format."""
    if not email or not isinstance(email, str):
        return False, "Email address is required."
    email = email.strip()
    if not EMAIL_REGEX.match(email):
        return False, "Invalid email address format."
    return True, ""

def validate_date(date_str, field_name="Date"):
    """Parses and validates standard ISO YYYY-MM-DD date."""
    if not date_str:
        return False, None, f"{field_name} is required."
    try:
        parsed_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        return True, parsed_date, ""
    except ValueError:
        return False, None, f"{field_name} must follow YYYY-MM-DD format."

def validate_numeric(val, field_name="Value", min_val=0, is_float=True):
    """Validates numeric ranges."""
    if val is None or str(val).strip() == "":
        return False, None, f"{field_name} is required."
    try:
        num = float(val) if is_float else int(val)
        if num < min_val:
            return False, None, f"{field_name} must be at least {min_val}."
        return True, num, ""
    except ValueError:
        return False, None, f"{field_name} must be a valid number."

