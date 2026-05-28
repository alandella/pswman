__all__ = [
    "get_services",
    "get_tables",
    "cmd_get_services",
    "cmd_get_tables",
]

from .constants import META_TABLE, FILENAME, COLUMNS
from .core import _safe_identifier, get_connection, table_exists
from .ui import _section, _display_service


def get_services(dbfile: str, tablename: str) -> list[tuple]:

    safe_table = _safe_identifier(tablename)

    if not table_exists(dbfile, tablename):
        print(f"Table '{tablename}' does not exist.")
        return []

    sql = f"SELECT * FROM {safe_table} ORDER BY service COLLATE NOCASE ASC"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()


def get_tables(dbfile: str) -> list[str]:
    # FIX #6: exclude meta table from results — it is an internal implementation detail
    sql = (
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite%' "
        "AND name != ? "
        "ORDER BY name COLLATE NOCASE ASC"
    )

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (META_TABLE,))
        return [row[0] for row in cursor.fetchall()]


def cmd_get_services(table: str) -> None:

    services = get_services(FILENAME, table)

    if not services:
        print(f"No services found in table '{table}'.")
        return

    _section(f"Retrieved services for table '{table}':")

    for service in services:
        _display_service(COLUMNS, service)

    print()


def cmd_get_tables() -> None:

    tables = get_tables(FILENAME)

    if not tables:
        print("No tables found.")
        return

    _section(f"Retrieved tables from database '{FILENAME}':")

    for table in tables:
        print(f"{table}")

    print()
