"""Application configuration loaded from environment variables and .env."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_DEFAULT_TABLES = (
    "PV Site Usage",
    "ESS Site Usage",
    "Current Spare Units",
)


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable application settings; credentials are optional until needed."""

    openai_api_key: str | None
    openai_model: str
    airtable_token: str | None
    airtable_base_id: str | None
    airtable_tables: tuple[str, ...]
    request_timeout_seconds: float
    allow_insecure_tls: bool


def load_settings(env_file: str | Path | None = None) -> Settings:
    """Load settings from the process environment, supplemented by a .env file."""
    load_dotenv(dotenv_path=env_file, override=False)

    configured_tables = os.getenv("AIRTABLE_TABLES")
    tables = (
        tuple(table.strip() for table in configured_tables.split(",") if table.strip())
        if configured_tables
        else _DEFAULT_TABLES
    )

    try:
        timeout = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    except ValueError as exc:
        raise ValueError("REQUEST_TIMEOUT_SECONDS must be a number") from exc
    if timeout <= 0:
        raise ValueError("REQUEST_TIMEOUT_SECONDS must be greater than zero")

    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
        airtable_token=os.getenv("AIRTABLE_TOKEN") or None,
        airtable_base_id=os.getenv("AIRTABLE_BASE_ID") or None,
        airtable_tables=tables,
        request_timeout_seconds=timeout,
        allow_insecure_tls=os.getenv("ALLOW_INSECURE_TLS", "false").strip().lower()
        in {"1", "true", "yes", "on"},
    )
