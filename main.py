"""Application entry point."""

from config import load_settings
from utils.logger import get_logger


def main() -> int:
    """Initialize the application without making external API calls."""
    logger = get_logger(__name__)
    try:
        settings = load_settings()
    except ValueError as exc:
        logger.error("Invalid configuration: %s", exc)
        return 2

    logger.info("Repair Center AI initialized with model %s", settings.openai_model)
    logger.info("Configured Airtable tables: %d", len(settings.airtable_tables))
    logger.info("External connections are created only when a service is used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
