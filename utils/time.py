"""Timezone-safe timestamps stored as naive UTC for the existing SQLite schema."""

from datetime import datetime, timezone


def utc_now():
    """Return the current UTC time without deprecated datetime.utcnow()."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
