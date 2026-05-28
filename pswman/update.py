__all__ = [
    "update_service",
    "move_service",
    "cmd_update_service",
    "cmd_move_service",
]

from .constants import ENCRYPTED_FIELDS, FILENAME, COLUMNS
from .core import _safe_identifier, get_connection, table_exists, get_service_id
from .crypto import encrypt_field
from .lookup import query_service
from .ui import _section, _key_value_add


def update_service(dbfile: str, tablename: str, data: dict[str, str]) -> None:

    safe_table = _safe_identifier(tablename)

    if not table_exists(dbfile, tablename):
        print(f"Table '{tablename}' does not exist.")
        return

    if any(data.get(f) for f in ENCRYPTED_FIELDS):
        data = dict(data)
        for field in ENCRYPTED_FIELDS:
            if data.get(field):
                data[field] = encrypt_field(data[field])

    keys = [k for k in data.keys() if k != "id"]
    columns = ", ".join([f"{_safe_identifier(k)} = ?" for k in keys])
    values = tuple(data[k] for k in keys)

    # pass id as a parameter instead of interpolating it
    sql = f"UPDATE {safe_table} SET {columns} WHERE id = ?"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (*values, data["id"]))
        conn.commit()


def move_service(dbfile: str, old_table: str, new_table: str, query: str) -> None:

    safe_old = _safe_identifier(old_table)
    safe_new = _safe_identifier(new_table)

    if not table_exists(dbfile, old_table):
        print(f"Source table '{old_table}' does not exist.")
        return

    if not table_exists(dbfile, new_table):
        print(f"Destination table '{new_table}' does not exist.")
        return

    sql_mov = f"INSERT INTO {safe_new} SELECT * FROM {safe_old} WHERE LOWER(service) = LOWER(?)"
    sql_del = f"DELETE FROM {safe_old} WHERE LOWER(service) = LOWER(?)"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql_mov, (query,))
        cursor.execute(sql_del, (query,))
        conn.commit()


def cmd_update_service(table: str) -> None:

    data = {key: None for key in COLUMNS}

    _section(f"Input service from table '{table}':")

    print()
    # FIX #8: use `or None` shorthand, consistent with cmd_add_service
    for col in (k for k in data.keys() if k != "id"):
        data[col] = _key_value_add(col) or None

    if not query_service(FILENAME, table, data["service"]):
        print(f"Service '{data['service']}' does not exist in table '{table}'.")
        return

    data["id"] = get_service_id(FILENAME, table, data["service"])

    update_service(FILENAME, table, data)

    print(f"Service '{data['service']}' updated in table '{table}'.")


def cmd_move_service(old_table: str, new_table: str, query: str) -> None:

    services = query_service(FILENAME, old_table, query)

    if not services:
        print(f"Queried service '{query}' not found in table '{old_table}'.")
        return

    if query_service(FILENAME, new_table, query):
        print(f"Service '{query}' already exists in table '{new_table}'.")
        return

    move_service(FILENAME, old_table, new_table, query)

    print(f"'{query}' moved to table '{new_table}'.")
