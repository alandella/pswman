__all__ = [
    "query_service",
    "query_table",
    "cmd_lookup_service",
    "cmd_lookup_table",
]

from .constants import FILENAME, COLUMNS
from .core import _safe_identifier, get_connection, table_exists
from .get import get_tables
from .ui import _section, _display_service


def query_service(dbfile: str, tablename: str, query: str) -> list[tuple] | None:

    safe_table = _safe_identifier(tablename)

    if not table_exists(dbfile, tablename):
        print(f"Table '{tablename}' does not exist.")
        return None

    sql = f"SELECT * FROM {safe_table} WHERE LOWER(service) = LOWER(?)"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (query,))
        return cursor.fetchall()


def query_table(dbfile: str, query: str) -> list[tuple]:

    if not table_exists(dbfile, query):
        print(f"Table '{query}' does not exist.")
        return []

    safe_table = _safe_identifier(query)
    sql = f"SELECT * FROM {safe_table}"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()


def cmd_lookup_service(query: str, table: str = None) -> None:

    if table is None:
        tables = get_tables(FILENAME)
    else:
        tables = [table]

    # collect results first, then report — avoids noisy per-table "not found" messages
    found_in = []
    results_map = {}

    for tab in tables:
        services = query_service(FILENAME, tab, query)
        if services:
            found_in.append(tab)
            results_map[tab] = services

    if not found_in:
        print(f"\nQueried service '{query}' not found in any table.")
        return

    for tab in found_in:
        _section(f"Retrieved service '{query}' from table '{tab}':")
        for service in results_map[tab]:
            _display_service(COLUMNS, service)
        print()


def cmd_lookup_table(query: str) -> None:

    result = query_table(FILENAME, query)

    if not result:
        print(f"Queried table '{query}' not found.")
        return

    print(f"\nRetrieved table '{query}' from database.")
