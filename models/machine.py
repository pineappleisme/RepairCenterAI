"""Repair Center machine data model."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Machine:
    """Normalized machine identity with optional source fields."""

    serial_number: str
    model_name: str | None = None
    project_name: str | None = None
    site_name: str | None = None
    source_fields: dict[str, Any] = field(default_factory=dict)
