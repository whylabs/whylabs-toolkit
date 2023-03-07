import pytz
from datetime import datetime

import pytest

from whylabs_toolkit.monitor.models import *
from tests.helpers.test_monitor_helpers import BaseTestMonitor


def test_set_fixed_dates_baseline(monitor_setup):
    monitor_setup.set_fixed_dates_baseline(
        start_date=datetime(2023,1,1),
        end_date=datetime(2023,1,2)
    )

    assert monitor_setup.config.baseline == TimeRangeBaseline(
        range=TimeRange(
            start=datetime(2023,1,1, tzinfo=pytz.utc),
            end=datetime(2023,1,2, tzinfo=pytz.utc)
        )
    )

def test_exclude_target_columns(monitor_setup):
    monitor_setup.exclude_target_columns(
        columns=["prediction_temperature"]
    )

    assert monitor_setup._exclude_columns == ["prediction_temperature"]


def test_set_target_columns(monitor_setup):
    monitor_setup.set_target_columns(
        columns=["prediction_temperature"]
    )

    assert monitor_setup._target_columns == ["prediction_temperature"]


def test_setup(monitor_setup):
    assert not monitor_setup.monitor
    assert not monitor_setup.analyzer

    monitor_setup.apply()

    assert isinstance(monitor_setup.monitor, Monitor)
    assert isinstance(monitor_setup.analyzer, Analyzer)


def test_set_target_matrix(monitor_setup):
    monitor_setup.target_matrix = DatasetMatrix()
    monitor_setup.apply()

    assert not isinstance(monitor_setup.target_matrix, ColumnMatrix)


def test_set_and_exclude_columns_keep_state(monitor_setup):
    assert monitor_setup._target_columns == []
    assert monitor_setup._exclude_columns == []

    monitor_setup.exclude_target_columns(columns=["prediction_temperature"])

    assert monitor_setup._target_columns == []
    assert monitor_setup._exclude_columns == ["prediction_temperature"]

    monitor_setup.set_target_columns(columns=["prediction_temperature"])

    assert monitor_setup._target_columns == ["prediction_temperature"]
    assert monitor_setup._exclude_columns == ["prediction_temperature"]

    monitor_setup.apply()

    assert monitor_setup.target_matrix == ColumnMatrix(
        include=["prediction_temperature"], exclude=["prediction_temperature"], segments=[]
    )


class TestExistingMonitor(BaseTestMonitor):
    def test_existing_monitor_monitor_setup_with_id(self, existing_monitor_setup):
        assert isinstance(existing_monitor_setup.config, StddevConfig)


def test_validate_if_columns_exist_before_setting(existing_monitor_setup):
    with pytest.raises(ValueError) as e:
        existing_monitor_setup.exclude_target_columns(columns=["test_exclude_column"])
        assert e.value == f"test_exclude_column is not present on {existing_monitor_setup.credentials.dataset_id}"

    with pytest.raises(ValueError) as e:
        existing_monitor_setup.set_target_columns(columns=["test_set_column"])
        assert e.value == f"test_set_column is not present on {existing_monitor_setup.credentials.dataset_id}"
