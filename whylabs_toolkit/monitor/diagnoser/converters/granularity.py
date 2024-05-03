from dateutil.relativedelta import relativedelta
from whylabs_toolkit.utils.granularity import Granularity
from isodate import parse_datetime, parse_duration, parse_date


def batches_to_timedelta(time_period: str, batches: int) -> relativedelta:
    if time_period == "PT1H":
        return relativedelta(hours=batches)

    if time_period == "P1W":
        return relativedelta(weeks=batches)

    if time_period == "P1M":
        return relativedelta(months=batches)

    return relativedelta(days=batches)


def calculate_num_batches(interval: str, granularity: str) -> int:
    # Parse the ISO8601 interval string into a start and end datetime
    start, end = interval.split("/")
    start_date = parse_datetime(start) if "T" in start else parse_date(start)
    try:
        end_date = parse_datetime(end) if "T" in start else parse_date(end)
    except ValueError:
        end_date = start_date + parse_duration(end)

    # Calculate the difference based on the granularity
    if granularity == "hourly":
        difference = relativedelta(end_date, start_date).days * 24 + relativedelta(end_date, start_date).hours
    elif granularity == "daily":
        difference = relativedelta(end_date, start_date).days
    elif granularity == "weekly":
        difference = relativedelta(end_date, start_date).weeks
    elif granularity == "monthly":
        difference = relativedelta(end_date, start_date).months
    else:
        raise ValueError(f"Unsupported granularity: {granularity}")

    return difference
