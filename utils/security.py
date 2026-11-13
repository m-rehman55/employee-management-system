"""Small security helpers shared by authentication and navigation routes."""

from urllib.parse import urlsplit

from flask import request


def safe_local_url(candidate, fallback):
    """Return a same-host URL, otherwise return the supplied fallback."""
    if not candidate:
        return fallback

    parsed = urlsplit(candidate)
    if parsed.scheme or parsed.netloc:
        if parsed.netloc != request.host:
            return fallback
        path = parsed.path or "/"
        return f"{path}?{parsed.query}" if parsed.query else path

    if candidate.startswith("/") and not candidate.startswith("//"):
        return candidate
    return fallback
