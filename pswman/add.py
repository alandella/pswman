__all__ = [
    "add_service",
    "add_table",
    "initialize",
    "cmd_add_service",
    "cmd_add_table",
]

import os

from .constants import ENCRYPTED_FIELDS, LEFT_PAD, FILENAME, COLUMNS
from .core import _safe_identifier, get_connection, table_exists, check_empty
from .crypto import encrypt_field
from .lookup import query_service
from .ui import _key_value_add


def add_service(dbfile: str, tablename: str, data: dict[str, str]) -> bool:
    """
    removed input() call — table creation decision is now handled in main.py
    """
    safe_table = _safe_identifier(tablename)

    if query_service(dbfile, tablename, data["service"]):
        print(f"Service '{data['service']}' already exists in table '{tablename}'.")
        print("Use 'upd-svc' to modify existing services.")
        return False

    if any(data.get(f) for f in ENCRYPTED_FIELDS):
        data = dict(data)
        for field in ENCRYPTED_FIELDS:
            if data.get(field):
                data[field] = encrypt_field(data[field])

    keys = [k for k in data.keys() if k not in ("id", "created_at")]
    columns = ", ".join(_safe_identifier(k) for k in keys)
    pholder = ", ".join(["?"] * len(keys))
    values = tuple(data[k] for k in keys)

    sql = f"INSERT INTO {safe_table} ({columns}) VALUES ({pholder})"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()

    return True


def add_table(dbfile: str, tablename: str, columns: dict[str, str]) -> bool:

    safe_table = _safe_identifier(tablename)

    if table_exists(dbfile, tablename):
        print(f"Table '{tablename}' already exists.")
        return False

    columns_sql = ", ".join([f"{_safe_identifier(col)} {coltype}" for col, coltype in columns.items()])
    sql = f"CREATE TABLE IF NOT EXISTS {safe_table} ({columns_sql})"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)

    return True


def initialize(dbfile: str, tables: list[str], columns: dict[str, str]) -> None:

    # FIX #5: extension check moved to top — always enforced, not just when DB exists
    if not dbfile.endswith(".db"):
        raise ValueError("Unsafe DB file name.")

    if not os.path.exists(dbfile):

        print(f"\nDatabase file '{dbfile}' not found.")
        answer = input("Create it in the current directory? (y/n): ").strip().lower()

        if answer != "y":
            custom = input("Enter a custom path (must end with '.db'), or press Enter to abort: ").strip()

            if not custom:
                print("Initialization aborted.")
                return

            if not custom.endswith(".db"):
                print("Invalid file name: must end with '.db'. Initialization aborted.")
                return

            dbfile = custom

        for table in tables:
            add_table(dbfile, table, columns)

        print(f"Created '{dbfile}' and tables.")

    else:

        print(f"{'Checking database':.<{LEFT_PAD}}", end="")
        print("done!")

        print(f"{'Checking names':.<{LEFT_PAD}}", end="")

        if not all(col.isidentifier() for col in columns.keys()):
            raise ValueError("Unsafe DB column name.")

        if not all(tbl.isidentifier() for tbl in tables):
            raise ValueError("Unsafe DB table name.")

        print("done!")

        print(f"{'Finalizing checks':.<{LEFT_PAD}}", end="")

        if not os.access(dbfile, os.W_OK):
            raise PermissionError(f"File '{dbfile}' is not writable.")

        if check_empty(dbfile):
            for table in tables:
                add_table(dbfile, table, columns)
            print("done!\nAll tables added.")
        else:
            print("done!\nDatabase already has tables.")


def cmd_add_service(table: str) -> None:

    if not table:
        print("Table name cannot be empty.")
        return

    if not table_exists(FILENAME, table):
        print(f"Table '{table}' does not exist. Use 'add-tbl' to create it first.")
        return

    data = {key: None for key in COLUMNS}

    for col in (k for k in data.keys() if k not in ("id", "created_at")):
        data[col] = _key_value_add(col) or None

    flag = add_service(FILENAME, table, data)

    if flag:
        print(f"\nService '{data['service']}' added to table '{table}'.")
    else:
        print(f"\nFailed to add service '{data['service']}' to table '{table}'.")


def cmd_add_table(table: str) -> None:

    if not table:
        print("Table name cannot be empty.")
        return

    flag = add_table(FILENAME, table, COLUMNS)

    if flag:
        print(f"Table '{table}' added to database.")
    else:
        print(f"Failed to add table '{table}'.")
