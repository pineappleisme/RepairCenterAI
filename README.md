# RepairCenterAI

## Project Overview

RepairCenterAI is the foundation for an internal Sungrow Repair Center assistant. It separates configuration, logging, data models, and external-service clients so future chat, spare-unit matching, desktop, and Teams interfaces can use the same application services.

The current implementation provides reusable Airtable and OpenAI clients plus opt-in integration checks. It does not implement repair workflows, matching rules, a GUI, or a bot. Starting the application does not make network requests.

## Requirements

- Python 3.11 or newer
- An OpenAI API key for the OpenAI integration check
- An Airtable personal access token and base ID for Airtable integration checks

## Installation

From this directory, create and activate a virtual environment, then install dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set credentials in `.env`. Keep `.env` out of source control; `.env.example` contains names and safe defaults only.

## Environment Variables

| Variable | Purpose | Default |
| --- | --- | --- |
| `OPENAI_API_KEY` | OpenAI API credential | None |
| `OPENAI_MODEL` | Model used by the OpenAI service | `gpt-4o-mini` |
| `AIRTABLE_TOKEN` | Airtable personal access token | None |
| `AIRTABLE_BASE_ID` | Airtable base identifier | None |
| `AIRTABLE_TABLES` | Comma-separated names checked by the Airtable script | The three Repair Center tables |
| `REQUEST_TIMEOUT_SECONDS` | HTTP timeout for external requests | `30` |
| `ALLOW_INSECURE_TLS` | Temporarily disable TLS certificate verification for local diagnostics only | `false` |

The Airtable metadata endpoint used by `AirtableService.get_tables()` may require the token's `schema.bases:read` scope. Record reads require appropriate base access and record-read permissions.

`ALLOW_INSECURE_TLS` defaults to `false`. Set it to `true` only for a temporary local connectivity test when the network's trusted CA has not been configured; do not use it for shared or production deployments.

## Running

Initialize the application (no external API calls):

```powershell
python main.py
```

Run the opt-in integration checks from the project root:

```powershell
python -m tests.test_openai
python -m tests.test_airtable
```

The OpenAI check sends the requested exact-response prompt. The Airtable check reads at most one record from each configured table and reports its status, record count, and field names. These checks use real credentials and incur normal API usage; they are not run automatically by application startup.

## Architecture

- `config.py` loads environment-backed immutable settings.
- `services/` owns external API transport and reusable operations.
- `models/` contains typed domain data containers without workflow logic.
- `utils/logger.py` configures console and rotating-independent file logging.
- `prompts/` keeps prompt text outside service code.
- `tests/` contains explicit integration-check entry points.

## Future Development Plan

The structure is ready to grow into separate application/use-case modules for site configuration search, current spare-unit search, replacement-rule matching, and AI chat. Desktop UI and Microsoft Teams adapters should call those same use cases rather than embedding business logic in either interface. None of those future features is implemented here.
