"""Runtime configuration."""

from dataclasses import dataclass
from os import environ
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    """Configuration read once when an application is created."""

    seed_file: Path
    port: int
    log_level: str
    log_file: Path
    static_dir: Path | None


def load_settings() -> Settings:
    """Read environment-backed application configuration."""
    seed_value = environ.get("SEED_FILE", "src/seed.yml")
    log_value = environ.get("LOG_FILE", "logs/app.jsonl")
    static_value = environ.get("STATIC_DIR")
    return Settings(
        seed_file=_resolve_from_backend(seed_value),
        port=int(environ.get("PORT", "5000")),
        log_level=environ.get("LOG_LEVEL", "INFO").upper(),
        log_file=_resolve_from_backend(log_value),
        static_dir=Path(static_value).resolve() if static_value else None,
    )


def _resolve_from_backend(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (BACKEND_DIR / path).resolve()
