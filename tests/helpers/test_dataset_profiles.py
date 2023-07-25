import os
from datetime import datetime

import whylogs as why

from whylabs_toolkit.helpers.dataset_profiles import delete_all_profiles_for_period


def test_delete_profile_for_datetime_range():
    # Create and Upload profiles
    
    # Delete them
    
    # Assert response.status_code == 200
        
    result = delete_all_profiles_for_period(
        start=datetime(2023,7,5), 
        end=datetime(2023,7,6), 
        dataset_id = os.environ["DATASET_ID"], 
        org_id=os.environ["ORG_ID"]
    )
    assert result.status_code == 200


def test_delete_profiles_for_milliseconds_range():
    pass


def test_delete_profiles_raises_if_other_format_is_passed():
    pass
