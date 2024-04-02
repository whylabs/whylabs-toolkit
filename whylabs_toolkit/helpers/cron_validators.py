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
        minute=cron_slots[0],
        hour=cron_slots[1],
        day_of_month=cron_slots[2],
        month=cron_slots[3],
        day_of_week=cron_slots[4],
    )


def _is_not_less_granular_than_1_hour(split_cron: SplitCron) -> bool:
    """Check if the cron expression is less granular than 1 hour."""
    if split_cron.minute == "*":
        return False

    for item in ["-", ","]:
        if item in split_cron.minute:
            return False

    if split_cron.minute.startswith("*/"):
        try:
            divisor = int(split_cron.minute.split("/")[1])
            if divisor < 60:
                return False
        except ValueError:
            pass

    return True


def validate_cron_expression(cron: str) -> bool:
    split_cron = split_cron_expression(cron)
    return _is_not_less_granular_than_1_hour(split_cron=split_cron)
