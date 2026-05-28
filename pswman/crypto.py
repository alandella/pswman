__all__ = [
    "open_session",
    "encrypt_field",
    "decrypt_field",
]

import os
import base64
import getpass
import hmac

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .constants import (
    META_TABLE,
    SALT_SIZE,
    HASH_SIZE,
    KDF_ITERATIONS,
    PASSWORD_HASH_ITERATIONS,
    LEFT_PAD,
)
from .core import get_connection, _safe_identifier


_fernet: Fernet | None = None


def _load_or_create_salt(dbfile: str, meta_table: str = META_TABLE) -> bytes:
    """
    Load the salt from the existing database.
    The salt is not secret and ensures the derived key is unique.
    It is safe to store it in plaintext.
    """
    safe_table = _safe_identifier(meta_table)

    # FIX #1: use meta_table (raw string) as the WHERE value, not safe_table
    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (meta_table,))
        row = cursor.fetchone()

    meta_exists = row is not None

    if not meta_exists:
        sql_create = f"CREATE TABLE {safe_table} (key TEXT PRIMARY KEY, value BLOB NOT NULL)"

        with get_connection(dbfile) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_create)
            conn.commit()

        salt = os.urandom(SALT_SIZE)
        sql_insert = f"INSERT INTO {safe_table} (key, value) VALUES ('salt', ?)"

        with get_connection(dbfile) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_insert, (salt,))
            conn.commit()

        return salt

    else:
        # FIX #2: removed nested get_connection — only one connection open at a time
        sql_salt = f"SELECT value FROM {safe_table} WHERE key='salt'"

        with get_connection(dbfile) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_salt)
            row = cursor.fetchone()

        if row:
            return row[0]
        else:
            salt = os.urandom(SALT_SIZE)
            sql_insert = f"INSERT INTO {safe_table} (key, value) VALUES ('salt', ?)"

            with get_connection(dbfile) as conn:
                cursor = conn.cursor()
                cursor.execute(sql_insert, (salt,))
                conn.commit()

            return salt


def _derive_fernet(master_password: str, salt: bytes) -> Fernet:
    """
    Derive a Fernet key from the master password and salt using PBKDF2-HMAC-SHA256.
    The key is never written to disk — it exists only in memory for the session.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=HASH_SIZE,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return Fernet(key)


def _compute_password_hash(master: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=HASH_SIZE,
        salt=salt,
        iterations=PASSWORD_HASH_ITERATIONS,
    )
    return kdf.derive(master.encode())


def open_session(dbfile: str) -> None:
    """
    Open a new session with the database using the master password.
    On the first run, the user sets the master password and a verification hash is stored.
    On subsequent runs, the password is verified against the stored hash.
    """
    global _fernet

    if not os.path.exists(dbfile):
        print(f"\nDatabase file '{dbfile}' not found.")
        print(f"Run 'init-db' to create the database and set up the master password.")
        return

    salt = _load_or_create_salt(dbfile)

    safe_table = _safe_identifier(META_TABLE)
    sql        = f"SELECT value FROM {safe_table} WHERE key='verification_hash'"

    with get_connection(dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()

    if row is None:
        print("\nNo master password set. Setting up for the first time.")
        print("WARNING: If you forget this password, your data cannot be recovered.\n")

        master  = getpass.getpass("  Setup master password : ")
        confirm = getpass.getpass("Confirm master password : ")

        if master != confirm:
            raise ValueError("Passwords do not match. Session not opened.")

        verification_hash = _compute_password_hash(master, salt)
        sql_insert = f"INSERT INTO {safe_table} (key, value) VALUES ('verification_hash', ?)"

        with get_connection(dbfile) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_insert, (verification_hash,))
            conn.commit()

        print("\nMaster password set successfully.")

    else:
        master = getpass.getpass("\nMaster password : ")

        stored_hash    = row[0]
        candidate_hash = _compute_password_hash(master, salt)

        if not hmac.compare_digest(candidate_hash, stored_hash):
            raise ValueError("Wrong master password. Session not opened.")

    print(f"{chr(10)}{'Deriving session key':.<{LEFT_PAD}}", end="", flush=True)
    _fernet = _derive_fernet(master, salt)

    print("done!\n")


def encrypt_field(plaintext: str) -> str:
    if _fernet is None:
        raise RuntimeError("No active session. Call open_session() first.")
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_field(token: str) -> str:
    """
    Decrypt an encrypted token using the active session key.
    Raises cryptography.fernet.InvalidToken if the master password was wrong.
    """
    if _fernet is None:
        raise RuntimeError("No active session. Call open_session() first.")
    return _fernet.decrypt(token.encode()).decode()
