import argparse
# from pathlib import Path

import pswman as db


# PRINT FUNCTIONS


def print_logo() -> None:
    pass
    # # dependency to external logo file
    # logo_path = Path(__file__).parent / "logo.txt"

    # # check if file is missing
    # if not logo_path.exists():
    #     print("[pswman] Warning: logo.txt not found, skipping banner.")
    #     return

    # # error handling for file read issues
    # try:
    #     with open(logo_path, "r") as f:
    #         print(f.read())
    # except OSError as e:
    #     print(f"[pswman] Warning: could not read logo.txt: {e}")


class PswmanParser(argparse.ArgumentParser):
    """Custom parser that prints the banner before help."""

    def print_help(self, file=None):
        print_logo()
        super().print_help(file)


# MAIN


def main() -> None:

    parser = PswmanParser(
        prog="psw_manager",
        usage="%(prog)s [command] [options]",
        description="Simple Password Manager",
        epilog="Use 'psw_manager [command] -h, --help' for more information on a command.",
    )

    arg_list = [
        {
            "flags": ("-v", "--validate"),
            "kwargs": {
                "action": "store_true",
                "help": "validate database before running a command",
            },
        },
    ]

    for arg in arg_list:
        parser.add_argument(*arg["flags"], **arg["kwargs"])

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="<command>",
    )

    cmd_list = {
        "init-db": {
            "exec": lambda: db.initialize(args.filename, db.TABLES, db.COLUMNS),
            "help": "initialize the database",
            "validate": False,
            "session": False,
            "args": [
                (
                    "filename",
                    {
                        "help": "Full path of the database file to create",
                        "nargs": "?",
                        "default": db.FILENAME,
                    },
                ),
            ],
        },
        "add-svc": {
            "exec": lambda: db.cmd_add_service(args.table_name),
            "help": "add a new service to a table",
            "validate": True,
            "session": True,
            "args": [
                ("table_name", {"help": "Name of the table to add service"}),
            ],
        },
        "add-tbl": {
            "exec": lambda: db.cmd_add_table(args.table_name),
            "help": "add a new table to the database",
            "validate": True,
            "session": True,
            "args": [
                ("table_name", {"help": "Name of the table to add"}),
            ],
        },
        "get-svc": {
            "exec": lambda: db.cmd_get_services(args.table_name),
            "help": "get all services from a table",
            "validate": True,
            "session": True,
            "args": [
                ("table_name", {"help": "Name of the table to retrieve"}),
            ],
        },
        "get-tbl": {
            "exec": lambda: db.cmd_get_tables(),
            "help": "get all tables from the database",
            "validate": True,
            "session": True,
            "args": [],
        },
        "lkp-svc": {
            "exec": lambda: db.cmd_lookup_service(args.service_name, args.table_name),
            "help": "lookup a service in a table",
            "validate": True,
            "session": True,
            "args": [
                ("service_name", {"help": "Name of the service to lookup"}),
                (
                    "table_name",
                    {
                        "help": "Name of the table to lookup",
                        "nargs": "?",
                        "default": None,
                    },
                ),
            ],
        },
        "lkp-tbl": {
            "exec": lambda: db.cmd_lookup_table(args.table_name),
            "help": "lookup a table in the database",
            "validate": True,
            "session": True,
            "args": [
                ("table_name", {"help": "Name of the table to lookup"}),
            ],
        },
        "upd-svc": {
            "exec": lambda: db.cmd_update_service(args.table_name),
            "help": "update a service in a table",
            "validate": True,
            "session": True,
            "args": [
                ("table_name", {"help": "Name of the table to update"}),
            ],
        },
        "mov-svc": {
            "exec": lambda: db.cmd_move_service(
                args.old_table, args.new_table, args.service_name
            ),
            "help": "move a service to a different table",
            "validate": True,
            "session": True,
            "args": [
                ("old_table", {"help": "Name of the source table to move service"}),
                (
                    "new_table",
                    {"help": "Name of the destination table to move service"},
                ),
                ("service_name", {"help": "Name of the service to move"}),
            ],
        },
        "rnm-svc": {
            "exec": lambda: db.cmd_rename_service(
                args.table_name, args.old_name, args.new_name
            ),
            "help": "rename a service in a table",
            "validate": True,
            "session": True,
            "args": [
                ("table_name", {"help": "Name of the table to rename service"}),
                ("old_name", {"help": "Current name of the service"}),
                ("new_name", {"help": "New name of the service"}),
            ],
        },
        "rnm-tbl": {
            "exec": lambda: db.cmd_rename_table(args.old_name, args.new_name),
            "help": "rename a table in the database",
            "validate": True,
            "session": True,
            "args": [
                ("old_name", {"help": "Current name of the table"}),
                ("new_name", {"help": "New name of the table"}),
            ],
        },
        "del-svc": {
            "exec": lambda: db.cmd_delete_service(args.table_name, args.service_name),
            "help": "delete a service from a table",
            "validate": True,
            "session": True,
            "args": [
                ("table_name", {"help": "Name of the table to delete service"}),
                ("service_name", {"help": "Name of the service to delete"}),
            ],
        },
        "del-tbl": {
            "exec": lambda: db.cmd_delete_table(args.table_name),
            "help": "delete a table from the database",
            "validate": True,
            "session": True,
            "args": [
                ("table_name", {"help": "Name of the table to delete"}),
            ],
        },
        "del-esv": {
            "exec": lambda: db.cmd_delete_empty_services(args.table_name),
            "help": "delete empty services from a table",
            "validate": True,
            "session": True,
            "args": [
                ("table_name", {"help": "Name of the table to delete empty services"}),
            ],
        },
        "del-all": {
            "exec": lambda: db.cmd_delete_all_tables(),
            "help": "delete all tables from the database",
            "validate": True,
            "session": True,
            "args": [],
        },
        "del-db": {
            "exec": lambda: db.cmd_delete_database(),
            "help": "delete the entire database",
            "validate": False,
            "session": True,
            "args": [],
        },
        "exp-tbl": {
            "exec": lambda: db.cmd_export_table(args.table_name, args.filename),
            "help": "export a table from the database to csv",
            "validate": True,
            "session": True,
            "args": [
                ("table_name", {"help": "Name of the table to export"}),
                (
                    "filename",
                    {
                        "help": "Optional export file name (defaults to '<table_name>_export.csv')",
                        "nargs": "?",
                        "default": None,
                    },
                ),
            ],
        },
        "exp-db": {
            "exec": lambda: db.cmd_export_database(args.filename),
            "help": "export the entire database to csv",
            "validate": True,
            "session": True,
            "args": [
                (
                    "filename",
                    {
                        "help": "Optional export file name (defaults to '<db_name>_export.csv')",
                        "nargs": "?",
                        "default": None,
                    },
                ),
            ],
        },
        "xls-2db": {
            "exec": lambda: db.create_database_from_excel(
                args.xlsxfile, args.filename, db.COLUMNS
            ),
            "help": "create a database from an Excel file",
            "validate": False,
            "session": True,
            "args": [
                (
                    "xlsxfile",
                    {"help": "Name of the Excel file", "nargs": "?", "default": None},
                ),
                (
                    "filename",
                    {
                        "help": "Name of the database file to create (does not have defaults!)",
                        "nargs": "?",
                        "default": None,
                    },
                ),
            ],
        },
        "db-2xls": {
            "exec": lambda: db.cmd_export_database_to_excel(args.filename),
            "help": "export the entire database to an Excel file",
            "validate": True,
            "session": True,
            "args": [
                (
                    "filename",
                    {
                        "help": "Name of the export file to create (defaults to '<db_name>_export.xlsx')",
                        "nargs": "?",
                        "default": None,
                    },
                ),
            ],
        },
    }

    for cmd_name, cmd_cfg in cmd_list.items():
        sp = subparsers.add_parser(
            cmd_name, help=cmd_cfg["help"], description=cmd_cfg["help"]
        )
        for arg in cmd_cfg["args"]:
            sp.add_argument(arg[0], **arg[1])

    args = parser.parse_args()

    # FIX #9: show help when no command is given instead of silently doing nothing
    if args.command is None:
        parser.print_help()
        return

    # only validate when the command explicitly allows it
    if args.validate and args.command in cmd_list:
        if cmd_list[args.command].get("validate", True):
            db.validate(db.FILENAME)

    if args.command in cmd_list:
        if cmd_list[args.command].get("session", True):
            try:
                db.open_session(db.FILENAME)
            except ValueError as e:
                print(f"\nError: {e}")
                return
            except KeyboardInterrupt:
                print("\nSession cancelled.")
                return

        cmd_list[args.command]["exec"]()


if __name__ == "__main__":
    main()
