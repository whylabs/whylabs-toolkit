from enum import Enum


class Granularity(str, Enum):
    """Supported granularity."""

    hourly = "hourly"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
