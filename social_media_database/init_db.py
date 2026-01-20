#!/usr/bin/env python3
"""Initialize and migrate SQLite database for social_media_database

This script:
- Creates database if it doesn't exist
- Applies migrations in order from migrations/ directory
- Seeds development data using seeds/ scripts when requested
- Writes connection info and visualizer env

Environment:
- SQLITE_DB: Optional path to sqlite file. Defaults to ./myapp.db

Usage:
- python init_db.py                # initialize/migrate only
- python init_db.py --seed         # also seed dev data
- python init_db.py --reset        # delete db and re-init (dangerous)
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

DEFAULT_DB = "myapp.db"


def get_db_path() -> str:
    """Resolve database file path using env SQLITE_DB or default."""
    db_path = os.getenv("SQLITE_DB", DEFAULT_DB)
    return os.path.abspath(db_path)


def ensure_dirs():
    """Ensure support directories exist."""
    for d in ["migrations", "seeds", "helpers", "db_visualizer"]:
        Path(d).mkdir(parents=True, exist_ok=True)


def connect(db_path: str) -> sqlite3.Connection:
    """Create sqlite connection with foreign keys enabled."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_migrations_table(conn: sqlite3.Connection):
    """Create migrations table if not exists."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def get_applied_migrations(conn: sqlite3.Connection) -> set[str]:
    """Return set of applied migration filenames."""
    cur = conn.cursor()
    cur.execute("SELECT filename FROM schema_migrations")
    rows = cur.fetchall()
    return {r[0] for r in rows}


def run_migrations(conn: sqlite3.Connection, migrations_dir: Path) -> list[str]:
    """Execute pending migrations one by one in filename order."""
    init_migrations_table(conn)
    applied = get_applied_migrations(conn)
    executed: list[str] = []

    files = sorted([f for f in migrations_dir.glob("*.py") if f.name[0:3].isdigit()])
    for f in files:
        if f.name in applied:
            continue
        # Execute migration script in isolated namespace
        namespace = {}
        with open(f, "r", encoding="utf-8") as fh:
            code = fh.read()
        try:
            exec(compile(code, str(f), "exec"), namespace)  # noqa: S102 - controlled execution for migration scripts
            if "upgrade" not in namespace or not callable(namespace["upgrade"]):
                raise RuntimeError(f"Migration {f.name} missing upgrade(conn) function")
            namespace["upgrade"](conn)
            conn.execute("INSERT INTO schema_migrations (filename, applied_at) VALUES (?, ?)", (f.name, datetime.utcnow().isoformat()))
            conn.commit()
            executed.append(f.name)
            print(f"✓ Applied migration {f.name}")
        except Exception as e:
            conn.rollback()
            print(f"✗ Migration failed {f.name}: {e}")
            raise
    return executed


def write_connection_info(db_path: str):
    """Write connection helper files."""
    cwd = os.getcwd()
    connection_string = f"sqlite:///{db_path}"
    with open("db_connection.txt", "w", encoding="utf-8") as f:
        f.write("# SQLite connection methods:\n")
        f.write(f"# Python: sqlite3.connect('{db_path}')\n")
        f.write(f"# Connection string: {connection_string}\n")
        f.write(f"# File path: {db_path}\n")

    # Visualizer env
    with open("db_visualizer/sqlite.env", "w", encoding="utf-8") as f:
        f.write(f'export SQLITE_DB="{db_path}"\n')


def seed_data(conn: sqlite3.Connection, seeds_dir: Path):
    """Run seed scripts (ordered by filename). Idempotent inserts are recommended in seed files."""
    files = sorted(seeds_dir.glob("*.py"))
    for f in files:
        namespace = {}
        with open(f, "r", encoding="utf-8") as fh:
            code = fh.read()
        try:
            exec(compile(code, str(f), "exec"), namespace)  # noqa: S102
            if "run" not in namespace or not callable(namespace["run"]):
                print(f"- Skipping seed {f.name}: missing run(conn)")
                continue
            namespace["run"](conn)
            conn.commit()
            print(f"✓ Seeded {f.name}")
        except Exception as e:
            conn.rollback()
            print(f"✗ Seed failed {f.name}: {e}")
            raise


def reset_db(db_path: str):
    """Delete database file if exists."""
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted database {db_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Initialize and migrate SQLite database")
    parser.add_argument("--seed", action="store_true", help="Run seed scripts after migrations")
    parser.add_argument("--reset", action="store_true", help="Delete existing DB and re-initialize")
    return parser.parse_args()


def main():
    print("Starting SQLite initialization...")
    args = parse_args()
    ensure_dirs()
    db_path = get_db_path()

    if args.reset:
        reset_db(db_path)

    # Touch DB if not exists
    db_exists = os.path.exists(db_path)
    if not db_exists:
        Path(db_path).touch()
        print(f"Created new SQLite database at {db_path}")
    else:
        print(f"Using existing database at {db_path}")

    conn = connect(db_path)

    # Apply migrations
    executed = run_migrations(conn, Path("migrations"))
    print(f"Migrations applied: {len(executed)}")

    # Optionally seed
    if args.seed:
        seed_data(conn, Path("seeds"))

    conn.close()
    write_connection_info(db_path)

    print("\nInitialization complete.")
    print(f"- Database: {db_path}")
    print("- To view in visualizer: source db_visualizer/sqlite.env && (cd db_visualizer && npm start)")
    print("- Use ./db_shell.py for interactive SQL")


if __name__ == "__main__":
    main()
