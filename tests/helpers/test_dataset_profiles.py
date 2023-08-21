import os
from datetime import datetime
from unittest.mock import patch, Mock

import pytest

from whylabs_toolkit.helpers.dataset_profiles import (
    delete_all_profiles_for_period,
    validate_timestamp_in_millis,
    process_date_input
)

def test_validate_timestamp_in_millis() -> None:
    assert validate_timestamp_in_millis(1627233600000) == True
    assert validate_timestamp_in_millis(-1231214) == False
    assert validate_timestamp_in_millis("some_string") == False
    assert validate_timestamp_in_millis(None) == False
    assert validate_timestamp_in_millis(3.1415) == False

def test_process_date_input() -> None:
    input_milliseconds = 1627233600000
    assert process_date_input(input_milliseconds) == input_milliseconds
    
    input_datetime = datetime(2023, 7, 25)
    expected_milliseconds = int(input_datetime.timestamp() * 1000.0)
    assert process_date_input(input_datetime) == expected_milliseconds
    
    with pytest.raises(ValueError):
        process_date_input("invalid")
        
    with pytest.raises(ValueError):
        process_date_input(-12498127412)
    

## -- Note:
# After calling delete_dataset_profiles, it will schedule the deletion,
# that currently happens hourly, so there is no trivial way to check that on
# unit tests. For that matter, we will only make the assertion of a successful call, 
# and the actual deletion logic is tested and maintained by Songbird only

def test_delete_profile_for_datetime_range():
    result = delete_all_profiles_for_period(
        start=datetime(2023,7,5), 
        end=datetime(2023,7,6), 
        dataset_id = os.environ["DATASET_ID"], 
        org_id=os.environ["ORG_ID"]
    )
    
    assert result.get("id") == f"{os.environ['ORG_ID']}/{os.environ['DATASET_ID']}"


def test_delete_profiles_for_milliseconds_range():
    result = delete_all_profiles_for_period(
        start=int(datetime(2023,7,5).timestamp()*1000.0), 
        end=int(datetime(2023,7,6).timestamp()*1000.0), 
        dataset_id = os.environ["DATASET_ID"], 
        org_id=os.environ["ORG_ID"]
    )
    
    assert result.get("id") == f"{os.environ['ORG_ID']}/{os.environ['DATASET_ID']}"


def test_delete_profiles_raises_if_other_format_is_passed():
    with pytest.raises(ValueError):
        delete_all_profiles_for_period(
            start=-123123123123, 
            end=int(datetime(2023,7,6).timestamp()*1000.0), 
            dataset_id = os.environ["DATASET_ID"], 
            org_id=os.environ["ORG_ID"]
        )
    with pytest.raises(ValueError):
        delete_all_profiles_for_period(
            start="string_example", 
            end=int(datetime(2023,7,6).timestamp()*1000.0), 
            dataset_id = os.environ["DATASET_ID"], 
            org_id=os.environ["ORG_ID"]
        )

@patch('whylabs_toolkit.helpers.dataset_profiles.get_dataset_profile_api')
def test_delete_profiles_calls_delete_analyzer_results(mock_get_api):
    mock_call = Mock()
    mock_get_api.return_value = mock_call
    mock_call.delete_dataset_profiles = Mock()
    mock_call.delete_analyzer_results = Mock()
    
    
    
    delete_all_profiles_for_period(
        start=int(datetime(2023,7,5).timestamp()*1000.0), 
        end=int(datetime(2023,7,6).timestamp()*1000.0), 
        dataset_id = os.environ["DATASET_ID"], 
        org_id=os.environ["ORG_ID"]
    )
    
    mock_call.delete_dataset_profiles.assert_called_with(
        org_id=os.environ["ORG_ID"], 
        dataset_id=os.environ["DATASET_ID"], 
        profile_start_timestamp=int(datetime(2023,7,5).timestamp()*1000.0), 
        profile_end_timestamp=int(datetime(2023,7,6).timestamp()*1000.0)
    )
    
    mock_call.delete_analyzer_results.assert_called_with(
        org_id=os.environ["ORG_ID"], 
        dataset_id=os.environ["DATASET_ID"], 
        start_timestamp=int(datetime(2023,7,5).timestamp()*1000.0), 
        end_timestamp=int(datetime(2023,7,6).timestamp()*1000.0)
    )