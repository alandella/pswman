__all__ = [
    "export_table",
    "export_database",
    "create_database_from_excel",
    "export_database_to_excel",
    "cmd_export_table",
    "cmd_export_database",
    "cmd_export_database_to_excel",
]

import os
import csv
import errno

import openpyxl
import pandas as pd

from .constants import LEFT_PAD, FILENAME
from .core import _safe_identifier, get_connection, table_exists
from .get import get_tables
from .ui import _confirm


def export_table(dbfile: str, tablename: str, filename: str) -> bool:

    safe_table = _safe_identifier(tablename)

    if not table_exists(dbfile, tablename):
        print(f"Table '{tablename}' does not exist.")
        return False

    try:
        sql = f"SELECT * FROM {safe_table}"

        with get_connection(dbfile) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            headers = [desc[0].capitalize() for desc in cursor.description]

            with open(filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([f"Table: {tablename}"])
                writer.writerow(headers)
                writer.writerows(rows)

            return True

    except Exception as e:
        print(f"Error during export: {e}")
        return False


def export_database(dbfile: str, filename: str) -> bool:

    tables = get_tables(dbfile)

    if not tables:
        print("No tables found in the database.")
        return False

    try:
        for table in tables:
            safe_table = _safe_identifier(table)
            sql = f"SELECT * FROM {safe_table}"

            with get_connection(dbfile) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                headers = [desc[0].capitalize() for desc in cursor.description]

                with open(filename, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([f"Table: {table}"])
                    writer.writerow(headers)
                    writer.writerows(rows)
                    writer.writerow([])

        return True

    except Exception as e:
        print(f"Error during export: {e}")
        return False


def create_database_from_excel(xlsxfile: str, dbfile: str, columns: dict[str, str]) -> None:

    if not os.path.exists(xlsxfile):
        raise FileNotFoundError(f"The file '{xlsxfile}' does not exist.")
    elif os.path.exists(dbfile):
        raise FileExistsError(f"The database file '{dbfile}' already exists.")

    try:
        xls = pd.ExcelFile(xlsxfile)

        for sheet in xls.sheet_names:

            table_name = sheet.replace(" ", "_").lower()
            _safe_identifier(table_name)

            print(f"{'Importing ' + sheet:.<{LEFT_PAD}}", end="")

            df = pd.read_excel(xls, sheet_name=sheet)

            columns_sql = ", ".join([f"{_safe_identifier(col)} {coltype}" for col, coltype in columns.items()])
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"

            with get_connection(dbfile) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                conn.commit()
                df.to_sql(table_name, conn, if_exists="replace", index=False)

            print(f"to table '{table_name}'.")

        print(f"\nAll sheets from '{xlsxfile}' imported to '{dbfile}'.")

    except Exception as e:
        print(f"Error during reading '{xlsxfile}': {e}")
        return


def export_database_to_excel(dbfile: str, filename: str) -> bool:

    tables = get_tables(dbfile)

    if not tables:
        print("No tables found in the database.")
        return False

    try:
        wb = openpyxl.Workbook()
        wb.remove(wb.active)  # remove default "Sheet"

        for table in tables:
            safe_table = _safe_identifier(table)
            ws = wb.create_sheet(title=table[:31])

            sql = f"SELECT * FROM {safe_table}"

            with get_connection(dbfile) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                headers = [desc[0].capitalize() for desc in cursor.description]

            ws.append(headers)
            for row in rows:
                ws.append(list(row))

        try:
            wb.save(filename)
        except PermissionError as e:
            if e.errno == errno.EACCES:
                print(f"Cannot write to '{filename}'. File in use or lacking access.")
                print("Close the file if open in Excel and try again.")
                return False
            else:
                raise

        print(f"Exported {len(tables)} tables to '{filename}'")
        return True

    except Exception as e:
        print(f"Error exporting database: {e}")
        return False


def cmd_export_table(table: str, filename: str = None) -> None:

    if filename is None:
        filename = f"{table}_export.csv"
    else:
        if not filename.endswith(".csv"):
            raise ValueError("Unsafe export file name.")

    if not table_exists(FILENAME, table):
        print(f"Table '{table}' does not exist in database.")
        return

    flag = export_table(FILENAME, table, filename)

    if flag:
        print(f"\nExported table '{table}' to '{filename}'.")
    else:
        print(f"\nFailed to export table '{table}' from database.")


def cmd_export_database(filename: str = None) -> None:

    if filename is None:
        filename = f"{os.path.splitext(FILENAME)[0]}_export.csv"
    else:
        if not filename.endswith(".csv"):
            raise ValueError("Unsafe export file name.")

    flag = export_database(FILENAME, filename)

    if flag:
        print(f"\nExported database to '{filename}'.")
    else:
        print("\nFailed to export database.")


def cmd_export_database_to_excel(filename: str = None) -> None:

    if filename is None:
        filename = f"{os.path.splitext(FILENAME)[0]}_export.xlsx"
    else:
        if not filename.endswith(".xlsx"):
            raise ValueError("Unsafe export file name.")

    if os.path.exists(filename):
        if not _confirm(f"File '{filename}' already exists. Overwrite?"):
            if _confirm("Do you want to rename the file?"):
                newname = input("Enter new file name (must end with .xlsx): ").strip()
                if not newname.endswith(".xlsx"):
                    print("Invalid file name. Export aborted.")
                    return
                filename = newname
            else:
                print("Export aborted. File not overwritten.")
                return

    flag = export_database_to_excel(FILENAME, filename)

    if flag:
        print(f"\nExported database to '{filename}'.")
    else:
        print("\nFailed to export database.")
