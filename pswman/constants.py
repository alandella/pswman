# padding for left-alignment in the CLI output
__all__ = [
    "LEFT_PAD",
    "FILENAME",
    "SALT_SIZE",
    "HASH_SIZE",
    "KDF_ITERATIONS",
    "PASSWORD_HASH_ITERATIONS",
    "META_TABLE",
    "TABLES",
    "COLUMNS",
    "ENCRYPTED_FIELDS",
]

LEFT_PAD = 30

# Database filename
FILENAME = "passwords.db"

# Size of the salt in bytes
SALT_SIZE = 16

# size of the derived key (hash) in bytes
HASH_SIZE = 32

# PBKDF2 iteration count per OWASP 2023 recommendation
KDF_ITERATIONS = 600_000

# Number of iterations for hashing the master password (for key derivation)
PASSWORD_HASH_ITERATIONS = 100_000

# name of the table to store metadata (e.g., password hash, salt)
META_TABLE = "meta"

# sample names for credential tables
TABLES = [
    "cred_type1",
    "cred_type2",
    "cred_type3",
    "cred_type4",
]

# column definitions for the credential tables
COLUMNS = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "service": "TEXT NOT NULL",
    "email": "TEXT NOT NULL",
    "password": "TEXT NOT NULL",
    "user_name": "TEXT",
    "account_name": "TEXT",
    "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
}

# fields that should be encrypted in the database
ENCRYPTED_FIELDS = {"service", "email", "password", "user_name", "account_name"}
