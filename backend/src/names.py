"""User-name normalization and validation."""

import re

NAME_PATTERN = re.compile(r"^[a-z0-9-]{3,64}$")


def normalize_name(name: str) -> str:
    """Trim and lowercase a submitted user name without rewriting characters."""
    return name.strip().lower()


def is_valid_name(name: str) -> bool:
    """Return whether a normalized name meets the public identifier rules."""
    return bool(NAME_PATTERN.fullmatch(name))


def validate_name(name: object) -> str:
    """Normalize and validate a name, raising ValueError for invalid input."""
    if not isinstance(name, str):
        raise ValueError("Name must be a string.")
    normalized_name = normalize_name(name)
    if not is_valid_name(normalized_name):
        raise ValueError("Name must be 3-64 characters matching [a-z0-9-]+.")
    return normalized_name
