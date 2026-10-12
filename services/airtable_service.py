"""Reusable, business-logic-free Airtable REST client."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx

from config import Settings, load_settings

_AIRTABLE_API_URL = "https://api.airtable.com/v0/"


class AirtableService:
    """Small Airtable client for schema and record queries."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or load_settings()
        self._client: httpx.Client | None = None

    def connect(self) -> None:
        """Initialize the HTTP client after validating required configuration."""
        if not self._settings.airtable_token:
            raise ValueError("AIRTABLE_TOKEN is required")
        if not self._settings.airtable_base_id:
            raise ValueError("AIRTABLE_BASE_ID is required")
        if self._client is None:
            verify_tls = not self._settings.allow_insecure_tls
            self._client = httpx.Client(
                base_url=_AIRTABLE_API_URL,
                headers={"Authorization": f"Bearer {self._settings.airtable_token}"},
                timeout=self._settings.request_timeout_seconds,
                verify=verify_tls,
                transport=httpx.HTTPTransport(retries=5, verify=verify_tls),
            )

    def get_tables(self) -> list[dict[str, Any]]:
        """Return Airtable table definitions from the base metadata endpoint."""
        base_id = quote(self._required_base_id(), safe="")
        response = self._request("GET", f"meta/bases/{base_id}/tables")
        payload = response.json()
        tables = payload.get("tables")
        if not isinstance(tables, list):
            raise ValueError("Airtable returned an invalid tables response")
        return tables

    def get_first_record(self, table_name: str) -> dict[str, Any] | None:
        """Return the first record from a table, or None when it is empty."""
        records = self._get_records(table_name, {"pageSize": 1})
        return records[0] if records else None

    def search_by_serial_number(
        self,
        table_name: str,
        serial_number: str,
        field_name: str = "Serial Number",
    ) -> list[dict[str, Any]]:
        """Return records whose specified field exactly matches a serial number."""
        return self._search_by_field(table_name, field_name, serial_number)

    def search_by_project(
        self,
        table_name: str,
        project: str,
        field_name: str = "Project",
    ) -> list[dict[str, Any]]:
        """Return records whose specified field exactly matches a project value."""
        return self._search_by_field(table_name, field_name, project)

    def close(self) -> None:
        """Release the underlying HTTP connection pool."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> AirtableService:
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _get_records(
        self, table_name: str, params: dict[str, str | int]
    ) -> list[dict[str, Any]]:
        table_path = quote(table_name, safe="")
        response = self._request(
            "GET",
            f"{self._required_base_id()}/{table_path}",
            params=params,
        )
        payload = response.json()
        records = payload.get("records")
        if not isinstance(records, list):
            raise ValueError("Airtable returned an invalid records response")
        return records

    def _search_by_field(
        self, table_name: str, field_name: str, value: str
    ) -> list[dict[str, Any]]:
        if not field_name.strip():
            raise ValueError("field_name must not be empty")
        escaped_field = field_name.replace("\\", "\\\\").replace("}", "\\}")
        escaped_value = value.replace("\\", "\\\\").replace('"', '\\"')
        formula = f'{{{escaped_field}}} = "{escaped_value}"'
        return self._get_records(table_name, {"filterByFormula": formula})

    def _required_base_id(self) -> str:
        self.connect()
        assert self._settings.airtable_base_id is not None
        return self._settings.airtable_base_id

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str | int] | None = None,
    ) -> httpx.Response:
        self.connect()
        assert self._client is not None
        response = self._client.request(method, path, params=params)
        response.raise_for_status()
        return response
