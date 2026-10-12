"""Opt-in integration check for the configured Airtable base."""

from urllib.parse import quote

import httpx

from config import load_settings

_AIRTABLE_API_URL = "https://api.airtable.com/v0/"


def _report_table(client: httpx.Client, base_id: str, table_name: str) -> bool:
    """Read at most one record and report status, count, and field names."""
    status: int | str = "Unavailable"
    record_count = 0
    field_names: list[str] = []
    error_message: str | None = None

    try:
        response = client.get(
            f"{quote(base_id, safe='')}/{quote(table_name, safe='')}",
            params={"pageSize": 1},
        )
        status = response.status_code
        response.raise_for_status()
        payload = response.json()
        records = payload.get("records", [])
        if not isinstance(records, list):
            raise ValueError("Airtable returned an invalid records response")
        record_count = len(records)
        if records and isinstance(records[0], dict):
            fields = records[0].get("fields", {})
            if isinstance(fields, dict):
                field_names = list(fields.keys())
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        messages = {
            401: "401 Authentication Error: check AIRTABLE_TOKEN.",
            403: "403 Permission Error: verify token scopes and base access.",
            404: "404 Not Found: verify the base ID and table name.",
        }
        error_message = messages.get(
            status,
            f"HTTP Error: request returned status {status}.",
        )
    except httpx.TimeoutException:
        error_message = "Timeout: Airtable did not respond before the configured timeout."
    except httpx.NetworkError:
        error_message = "Connection Error: could not establish a connection to Airtable."
    except Exception as exc:
        error_message = f"Unexpected Exception: {type(exc).__name__}: {exc}"

    print(f"Table: {table_name}")
    print(f"HTTP Status: {status}")
    print(f"Record Count: {record_count}")
    print(f"Field Names: {field_names}")
    if error_message:
        print(error_message)
    return error_message is None


def main() -> int:
    """Check each configured table with a single-record request."""
    settings = load_settings()
    if not settings.airtable_token or not settings.airtable_base_id:
        print("Configuration Error: AIRTABLE_TOKEN and AIRTABLE_BASE_ID are required.")
        return 2

    headers = {"Authorization": f"Bearer {settings.airtable_token}"}
    verify_tls = not settings.allow_insecure_tls
    try:
        with httpx.Client(
            base_url=_AIRTABLE_API_URL,
            headers=headers,
            timeout=settings.request_timeout_seconds,
            verify=verify_tls,
            transport=httpx.HTTPTransport(retries=5, verify=verify_tls),
        ) as client:
            results = [
                _report_table(client, settings.airtable_base_id, table_name)
                for table_name in settings.airtable_tables
            ]
    except httpx.TimeoutException:
        print("Timeout: Airtable did not respond before the configured timeout.")
        return 1
    except httpx.NetworkError:
        print("Connection Error: could not establish a connection to Airtable.")
        return 1

    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
