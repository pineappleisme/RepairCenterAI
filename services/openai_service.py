"""Reusable OpenAI client with no application-specific reasoning logic."""

from __future__ import annotations

import httpx
from openai import OpenAI

from config import Settings, load_settings


class OpenAIService:
    """Thin wrapper around the OpenAI Responses API."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or load_settings()
        self._client: OpenAI | None = None

    def connect(self) -> None:
        """Initialize the SDK client after validating required configuration."""
        if not self._settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        if self._client is None:
            verify_tls = not self._settings.allow_insecure_tls
            http_client = httpx.Client(
                verify=verify_tls,
                transport=httpx.HTTPTransport(retries=5, verify=verify_tls),
            )
            self._client = OpenAI(
                api_key=self._settings.openai_api_key,
                timeout=self._settings.request_timeout_seconds,
                http_client=http_client,
            )

    def chat(self, message: str) -> str:
        """Send a text input to the configured model and return its response."""
        self.connect()
        assert self._client is not None
        response = self._client.responses.create(
            model=self._settings.openai_model,
            input=message,
        )
        return response.output_text

    def close(self) -> None:
        """Release the SDK client's underlying HTTP resources."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> OpenAIService:
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
