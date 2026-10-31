"""Database backup and export utilities."""

from __future__ import annotations

import shutil
from pathlib import Path


def backup_database(db_path: str | Path, backup_dir: str | Path) -> Path:
    """Safely create a copy of the SQLite database file."""
    src = Path(db_path).expanduser()
    dest_dir = Path(backup_dir).expanduser()
    dest_dir.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        raise FileNotFoundError(f"Database file not found: {src}")
    dest_file = dest_dir / f"nexus_backup_{src.name}"
    shutil.copy2(src, dest_file)
    return dest_file