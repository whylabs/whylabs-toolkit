import os

import pytest

from whylabs_toolkit.monitor.manager import MonitorSetup
from whylabs_toolkit.monitor.models import *


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
