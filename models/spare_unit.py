"""Replacement spare-unit data model."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SpareUnit:
    """Normalized spare-unit identity with optional inventory attributes."""

    serial_number: str
    model_name: str | None = None
    status: str | None = None
    location: str | None = None
    source_fields: dict[str, Any] = field(default_factory=dict)
