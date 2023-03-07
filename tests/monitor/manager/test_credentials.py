import os

import pytest

from whylabs_toolkit.monitor.manager import MonitorCredentials


@pytest.fixture
def credentials() -> MonitorCredentials:
    return MonitorCredentials(
        monitor_id="test_id"
    )

def test_credentials_org_id_match_env_var(credentials):
    expected_org_id = os.environ["ORG_ID"]
    assert expected_org_id == credentials.org_id

def test_analyzer_id_derived_from_monitor_id(credentials):
    assert credentials.analyzer_id == f"{credentials.monitor_id}-analyzer"

def test_gets_dataset_id_from_env_var_if_not_passed(credentials):
    expected_dataset_id = os.environ["DATASET_ID"]
    assert expected_dataset_id == credentials.dataset_id
