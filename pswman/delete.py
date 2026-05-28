__all__ = [
    "delete_service",
    "delete_empty_services",
    "delete_table",
    "delete_all_tables",
    "delete_database",
    "cmd_delete_service",
    "cmd_delete_empty_services",
    "cmd_delete_table",
    "cmd_delete_all_tables",
    "cmd_delete_database",
]

import os

from .constants import FILENAME
from .core import _safe_identifier, get_connection, table_exists
from .get import get_tables
from .lookup import query_service
from .ui import _confirm


def delete_service(dbfile: str, tablename: str, query: str) -> bool:

    safe_table = _safe_identifier(tablename)

    if not table_exists(dbfile, tablename):
        print(f"Table '{tablename}' does not exist.")
        return False

    sql = f"DELETE FROM {safe_table} WHERE LOWER(service) = LOWER(?)"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (query,))
        conn.commit()
        return cursor.rowcount > 0


def delete_empty_services(dbfile: str, tablename: str) -> int:

    safe_table = _safe_identifier(tablename)

    if not table_exists(dbfile, tablename):
        print(f"Table '{tablename}' does not exist.")
        return -1

    sql = f"DELETE FROM {safe_table} WHERE service IS NULL OR TRIM(service) = ''"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        return cursor.rowcount


def delete_table(dbfile: str, tablename: str) -> bool:

    safe_table = _safe_identifier(tablename)

    if not table_exists(dbfile, tablename):
        print(f"Table '{tablename}' does not exist.")
        return False

    sql = f"DROP TABLE {safe_table}"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        return True


def delete_all_tables(dbfile: str) -> bool:

    tables = get_tables(dbfile)

    if not tables:
        print("No tables found in the database.")
        return False

    try:
        for table in tables:
            delete_table(dbfile, table)
        return True

    except Exception as e:
        print(f"Error deleting tables from database '{dbfile}': {e}")
        return False


def delete_database(dbfile: str) -> bool:

    if not os.path.exists(dbfile):
        print(f"Database file '{dbfile}' does not exist.")
        return False

    try:
        os.remove(dbfile)
        print(f"Database file '{dbfile}' has been deleted.")
        return True

    except Exception as e:
        print(f"Error deleting database file '{dbfile}': {e}")
        return False


def cmd_delete_service(table: str, query: str) -> None:

    if not query_service(FILENAME, table, query):
        print(f"Service '{query}' does not exist in table '{table}'.")
        return

    if not _confirm(f"Are you sure you want to delete service '{query}'?"):
        print(f"Service '{query}' deletion aborted.")
        return

    flag = delete_service(FILENAME, table, query)

    if flag:
        print(f"\nService '{query}' deleted from table '{table}'.")
    else:
        print(f"\nFailed to delete service '{query}' from table '{table}'.")


def cmd_delete_empty_services(table: str) -> None:

    if not table_exists(FILENAME, table):
        print(f"Table '{table}' does not exist in database.")
        return

    if not _confirm("Are you sure you want to delete empty services?"):
        print("Empty services deletion aborted.")
        return

    flag = delete_empty_services(FILENAME, table)

    if flag == 0:
        print(f"\nNo empty services deleted from table '{table}'.")
    elif flag == -1:
        print(f"\nFailed to delete empty services from table '{table}'.")
    else:
        print(f"\nDeleted {flag} empty services from table '{table}'.")


def cmd_delete_table(query: str) -> None:

    if not table_exists(FILENAME, query):
        print(f"Table '{query}' does not exist in database.")
        return

    if not _confirm(f"Are you sure you want to delete table '{query}'?"):
        print(f"Table '{query}' deletion aborted.")
        return

    flag = delete_table(FILENAME, query)

    if flag:
        print(f"\nDeleted table '{query}' from database.")
    else:
        print(f"\nFailed to delete table '{query}' from database.")


def cmd_delete_all_tables() -> None:

    if not _confirm("Are you sure you want to delete all tables?"):
        print("All tables deletion aborted.")
        return

    flag = delete_all_tables(FILENAME)

    if flag:
        print("\nDeleted all tables from database.")
    else:
        print("\nFailed to delete all tables from database.")


def cmd_delete_database() -> None:

    if not _confirm(f"Are you sure you want to delete database '{FILENAME}'?"):
        print(f"Database '{FILENAME}' deletion aborted.")
        return

    flag = delete_database(FILENAME)

    if flag:
        print(f"\nDeleted database '{FILENAME}'.")
    else:
        print(f"\nFailed to delete database '{FILENAME}'.")
