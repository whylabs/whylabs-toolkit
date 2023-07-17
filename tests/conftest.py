import os

import pytest

from whylabs_toolkit.monitor.manager import MonitorSetup
from whylabs_toolkit.monitor.models import *
from whylabs_toolkit.helpers.config import UserConfig


@pytest.fixture
def monitor_setup() -> MonitorSetup:
    monitor_setup = MonitorSetup(monitor_id="some_long_and_descriptive_id")
    monitor_setup.config = DiffConfig(
        mode=DiffMode.pct,
        threshold=12.0,
        metric=SimpleColumnMetric.median,
        baseline=TrailingWindowBaseline(size=14)
    )
    return monitor_setup

@pytest.fixture
def existing_monitor_setup() -> MonitorSetup:
    monitor_setup = MonitorSetup(
        monitor_id=os.environ["MONITOR_ID"]
    )
    return monitor_setup

@pytest.fixture
def user_config() -> UserConfig:
    config = UserConfig(
        api_key=os.environ["DEV_WHYLABS_API_KEY"],
        org_id=os.environ["DEV_ORG_ID"],
        dataset_id=os.environ["DEV_DATASET_ID"],
        whylabs_host="https://songbird.development.whylabsdev.com"
    )
    return config
