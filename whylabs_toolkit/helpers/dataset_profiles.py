import logging
from datetime import datetime
from typing import Optional, Union

from whylabs_client.api.dataset_profile_api import DeleteDatasetProfilesResponse, DeleteAnalyzerResultsResponse

from whylabs_toolkit.helpers.utils import get_dataset_profile_api
from whylabs_toolkit.helpers.config import Config

date_or_millis = Union[datetime, int]
logger = logging.getLogger(__name__)


def validate_timestamp_in_millis(epoch_milliseconds: int) -> bool:
    if not isinstance(epoch_milliseconds, int):
        return False
    try:
        epoch_seconds = epoch_milliseconds / 1000
        dt = datetime.fromtimestamp(epoch_seconds)
        return dt >= datetime(1970, 1, 1)
    except (ValueError, OverflowError):
        return False


def process_date_input(date_input: date_or_millis) -> int:
    if isinstance(date_input, int):
        try:
            assert validate_timestamp_in_millis(epoch_milliseconds=date_input)
            return date_input
        except AssertionError:
            raise ValueError("You must provide a valid date input")
    elif isinstance(date_input, datetime):
        return int(date_input.timestamp() * 1000.0)
    else:
        raise ValueError(f"The date object {date_input} input must be a datetime or an integer Epoch!")


def delete_all_profiles_for_period(
    start: date_or_millis,
    end: date_or_millis,
    config: Config = Config(),
    org_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
) -> DeleteDatasetProfilesResponse:
    api = get_dataset_profile_api()

    profile_start_timestamp = process_date_input(date_input=start)
    profile_end_timestamp = process_date_input(date_input=end)

    org_id = org_id or config.get_default_org_id()
    dataset_id = dataset_id or config.get_default_dataset_id()

    result_profiles: DeleteDatasetProfilesResponse = api.delete_dataset_profiles(
        org_id=org_id,
        dataset_id=dataset_id,
        profile_start_timestamp=profile_start_timestamp,
        profile_end_timestamp=profile_end_timestamp,
    )
    logger.info(f"Scheduled deletion for profiles on {dataset_id} for {org_id}")

    api.delete_analyzer_results(
        org_id=org_id,
        dataset_id=dataset_id,
        start_timestamp=profile_start_timestamp,
        end_timestamp=profile_end_timestamp,
    )

    logger.info("Deleted analyzer results for the same timestamps as the profiles")
    logger.info(f"NOTE: Profile deletion happens every full hour on WhyLabs")

    return result_profiles
