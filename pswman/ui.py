from .constants import ENCRYPTED_FIELDS
from .crypto import decrypt_field


def _section(title: str) -> None:
    print(f"{title}")


def _confirm(prompt: str) -> bool:
    """Prompt the user for a yes/no confirmation. Returns True only on 'y'."""
    return input(f"{prompt} (y/n): ").strip().lower() == "y"


def _key_value(label: str, value, width: int = 14, fill: str = "") -> None:
    # FIX #10: only catch formatting errors, not all exceptions
    try:
        print(f"{label.capitalize():{fill}<{width}} {value}")
    except (ValueError, KeyError):
        print(f"{label.capitalize()}: {value}")


def _key_value_add(label: str, width: int = 14, fill: str = "") -> str:
    """Prompt the user for a value with a label, and return the input."""
    # FIX #10: only catch formatting errors, not all exceptions
    try:
        return input(f"{label.capitalize():{fill}<{width}} ").strip()
    except (ValueError, KeyError):
        return input(f"{label.capitalize()}: ").strip()


def _display_service(columns: dict[str, str], service: tuple) -> None:
    """Print a single service row, decrypting all encrypted fields."""
    print()
    for col, value in zip(columns.keys(), service):
        if col == "id":
            continue
        if col in ENCRYPTED_FIELDS and value:
            try:
                value = decrypt_field(value)
            except Exception:
                value = "<decryption error>"
        _key_value(col, value)
