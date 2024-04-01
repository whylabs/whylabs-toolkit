from dataclasses import dataclass


@dataclass
class SplitCron:
    day_of_week: str
    month: str
    day_of_month: str
    hour: str
    minute: str


def split_cron_expression(cron: str) -> SplitCron:
    """Split the cron expression into its components."""
    cron_slots = cron.split(" ")
    if len(cron_slots) != 5:
        raise ValueError("CronSchedule must have 5 fields.")
    return SplitCron(
        day_of_week=cron_slots[0],
        month=cron_slots[1],
        day_of_month=cron_slots[2],
        hour=cron_slots[3],
        minute=cron_slots[4],
    )


def _is_not_less_granular_than_1_hour(split_cron: SplitCron) -> bool:
    """Check if the cron expression is less granular than 1 hour."""
    # Specific days checks
    if split_cron.minute != "*" and split_cron.minute != "0":
        return True
    if split_cron.hour != "*" and split_cron.hour != "0":
        return True
    if split_cron.day_of_month != "*" and split_cron.day_of_month != "1":
        return True
    if split_cron.month != "*" and split_cron.month != "1":
        return True
    if split_cron.day_of_week != "*" and split_cron.day_of_week != "1":
        return True

    # Check range
    for field in (split_cron.day_of_week, split_cron.month, split_cron.day_of_month, split_cron.hour):
        for item in field.split(","):
            if "-" in item:
                start, end = map(int, item.split("-"))
                if end - start > 0:
                    return False
    return False


def validate_cron_expression(cron: str) -> bool:
    split_cron = split_cron_expression(cron)
    return _is_not_less_granular_than_1_hour(split_cron=split_cron)
