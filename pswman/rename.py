__all__ = [
    "rename_service",
    "rename_table",
    "cmd_rename_service",
    "cmd_rename_table",
]

from .constants import FILENAME
from .core import _safe_identifier, get_connection, table_exists
from .lookup import query_service


def rename_service(dbfile: str, tablename: str, old_name: str, new_name: str) -> None:

    safe_table = _safe_identifier(tablename)

    if not table_exists(dbfile, tablename):
        print(f"Table '{tablename}' does not exist.")
        return

    sql = f"UPDATE {safe_table} SET service = ? WHERE LOWER(service) = LOWER(?)"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (new_name, old_name))
        conn.commit()


def rename_table(dbfile: str, old_name: str, new_name: str) -> None:

    safe_old = _safe_identifier(old_name)
    safe_new = _safe_identifier(new_name)

    if not table_exists(dbfile, old_name):
        print(f"Table '{old_name}' does not exist.")
        return

    sql = f"ALTER TABLE {safe_old} RENAME TO {safe_new}"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()


def cmd_rename_service(table: str, old_name: str, new_name: str) -> None:

    if not query_service(FILENAME, table, old_name):
        print(f"Service '{old_name}' does not exist in table '{table}'.")
        return

    if query_service(FILENAME, table, new_name):
        print(f"Service '{new_name}' already exists in table '{table}'.")
        return

    rename_service(FILENAME, table, old_name, new_name)

    print(f"Service '{old_name}' renamed to '{new_name}' in table '{table}'.")


def cmd_rename_table(old_name: str, new_name: str) -> None:

    if not table_exists(FILENAME, old_name):
        print(f"Table '{old_name}' does not exist in database.")
        return

    if table_exists(FILENAME, new_name):
        print(f"Table '{new_name}' already exists in database.")
        return

    rename_table(FILENAME, old_name, new_name)

    print(f"Table '{old_name}' renamed to '{new_name}'.")
