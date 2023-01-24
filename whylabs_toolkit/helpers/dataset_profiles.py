# from whylabs_client.api.
from datetime import datetime
from typing import Optional, Union

from whylabs_client.api.dataset_profile_api import DeleteDatasetProfilesResponse

from whylabs_toolkit.helpers.utils import get_dataset_profile_api

date_or_millis = Union[datetime, int]


# TODO test and make sure it's working


def delete_all_profiles_for_period(
    start: date_or_millis,
    end: date_or_millis,
    dataset_id: str,
    org_id: Optional[str],
) -> None:
    api = get_dataset_profile_api()

    profile_start_timestamp = start if isinstance(start, int) else int(start.timestamp() * 1000.0)
    profile_end_timestamp = end if isinstance(end, int) else int(end.timestamp() * 1000.0)

    result: DeleteDatasetProfilesResponse = api.delete_dataset_profiles(
        org_id=org_id,
        dataset_id=dataset_id,
        profile_start_timestamp=profile_start_timestamp,
        profile_end_timestamp=profile_end_timestamp,
    )

    print(result)
