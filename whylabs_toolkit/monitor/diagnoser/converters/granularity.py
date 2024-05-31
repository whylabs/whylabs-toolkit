from math import floor
from isodate import parse_datetime, parse_duration, parse_date


def calculate_num_batches(interval: str, granularity: str) -> int:
    # Parse the ISO8601 interval string into a start and end datetime
    start, end = interval.split("/")
    start_date = parse_datetime(start) if "T" in start else parse_date(start)
    try:
        end_date = parse_datetime(end) if "T" in start else parse_date(end)
    except ValueError:
        end_date = start_date + parse_duration(end)

    # Calculate the (somewhat approximate) difference based on the granularity
    # Truncates to whole batches, ignores leap seconds
    if granularity == "hourly":
        difference = (end_date - start_date).total_seconds() / 3600
    elif granularity == "daily":
        difference = (end_date - start_date).total_seconds() / (3600 * 24)
    elif granularity == "weekly":
        difference = (end_date - start_date).total_seconds() / (3600 * 24 * 7)
    elif granularity == "monthly":
        difference = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
    else:
        raise ValueError(f"Unsupported granularity: {granularity}")

    diff_as_int: int = floor(difference)
    return diff_as_int
