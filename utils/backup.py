"""Consistent local SQLite backup helper."""
from datetime import datetime
from pathlib import Path
import sqlite3
from flask import current_app
from extensions import db


def sqlite_database_path():
    engine = db.engine
    if engine.url.get_backend_name() != 'sqlite' or not engine.url.database:
        raise RuntimeError('The built-in backup currently supports SQLite deployments only.')
    return Path(engine.url.database)


def create_sqlite_backup():
    """Create a timestamped SQLite backup without mutating the source database."""
    source_path = sqlite_database_path()
    backup_dir = source_path.parent / 'backups'
    backup_dir.mkdir(parents=True, exist_ok=True)
    filename = f"ems-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db"
    destination = backup_dir / filename

    source = sqlite3.connect(str(source_path))
    target = sqlite3.connect(str(destination))
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    return destination
