import os

import pytest

from whylabs_toolkit.monitor.manager import MonitorBuilder
from whylabs_toolkit.monitor.models import *


@pytest.fixture
def builder() -> MonitorBuilder:
    builder = MonitorBuilder(monitor_id="some_long_and_descriptive_id")
    builder.config = DiffConfig(
        mode=DiffMode.pct,
        threshold=12.0,
        metric=SimpleColumnMetric.median,
        baseline=TrailingWindowBaseline(size=14)
    )
    return builder

@pytest.fixture
def existing_monitor_builder() -> MonitorBuilder:
    builder = MonitorBuilder(
        monitor_id=os.environ["MONITOR_ID"]
    )
    return builder
