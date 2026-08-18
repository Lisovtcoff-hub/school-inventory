from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return a timezone-naive UTC timestamp for existing database columns."""
    return datetime.now(UTC).replace(tzinfo=None)
