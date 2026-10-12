"""Opt-in integration check for OpenAI credentials and connectivity."""

from openai import APIConnectionError, AuthenticationError, RateLimitError

from config import load_settings
from services.openai_service import OpenAIService

from dotenv import load_dotenv

_PROMPT = "Reply ONLY:\nOpenAI API connection successful."

load_dotenv()


def main() -> int:
    """Call the configured model once and report the result."""
    settings = load_settings()
    service = OpenAIService(settings)
    try:
        response = service.chat(_PROMPT)
        print("API Connected: Yes")
        print(f"Model: {settings.openai_model}")
        print(f"Response: {response}")
        return 0
    except AuthenticationError:
        print("API Connected: No")
        print("Authentication Error: check OPENAI_API_KEY and account access.")
        return 1
    except RateLimitError:
        print("API Connected: No")
        print("Rate Limit: the account or project has reached its request limit.")
        return 1
    except APIConnectionError:
        print("API Connected: No")
        print("Network Error: could not reach the OpenAI API.")
        return 1
    except Exception as exc:
        print("API Connected: No")
        print(f"Unexpected Exception: {type(exc).__name__}: {exc}")
        return 1
    finally:
        service.close()


if __name__ == "__main__":
    raise SystemExit(main())
