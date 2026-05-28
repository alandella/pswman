__all__ = [
    "get_connection",
    "check_empty",
    "validate",
    "get_service_id",
    "table_exists",
]

import os
import sqlite3

from .constants import LEFT_PAD


def _safe_identifier(name: str) -> str:
    if not name.isidentifier():
        raise ValueError(f"Unsafe SQL identifier: '{name}'")
    return name


def get_connection(dbfile: str) -> sqlite3.Connection:
    # FIX #3: removed manual file creation — SQLite creates the file itself on connect()
    directory = os.path.dirname(dbfile)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return sqlite3.connect(dbfile)


def check_empty(dbfile: str) -> bool:
    sql = (
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite%'"
    )

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        return not bool(cursor.fetchone())


def validate(dbfile: str) -> None:
    print(f"{'Validating database':.<{LEFT_PAD}}", end="")

    if not os.path.exists(dbfile):
        print(f"Database file '{dbfile}' not found.")
        return
    elif not dbfile.endswith(".db"):
        raise ValueError(f"Unsafe DB file name: {dbfile}")

    try:
        with get_connection(dbfile) as conn:
            conn.execute("PRAGMA schema_version;")
    except sqlite3.DatabaseError as e:
        raise ValueError(f"Invalid SQLite database: {dbfile} ({e})")

    print("done!")
    print(f"Database '{dbfile}' is validated.")


def get_service_id(dbfile: str, tablename: str, servicename: str) -> int | None:
    # FIX #4: return None instead of crashing when service is not found
    safe_table = _safe_identifier(tablename)
    sql = f"SELECT id FROM {safe_table} WHERE LOWER(service) = LOWER(?)"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (servicename,))
        row = cursor.fetchone()
        return row[0] if row else None


def table_exists(dbfile: str, tablename: str) -> bool:
    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite%'"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()

        # check for exact match first
        cursor.execute(sql + " AND name=?", (tablename,))

        if cursor.fetchone():
            return True
        else:
            cursor.execute(sql)
            all_tables = [row[0] for row in cursor.fetchall()]

        # fallback: case-insensitive comparison
        return any(t.lower() == tablename.lower() for t in all_tables)

    # TODO: implement fuzzy matches (typos allowed)
