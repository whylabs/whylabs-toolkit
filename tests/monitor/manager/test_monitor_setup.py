import os

from datetime import datetime, timezone

import pytest

from whylabs_toolkit.monitor.models import *
from tests.helpers.test_monitor_helpers import BaseTestMonitor
from whylabs_toolkit.monitor.manager.credentials import MonitorCredentials
from whylabs_toolkit.monitor import MonitorSetup
from whylabs_toolkit.helpers.config import UserConfig


def test_set_fixed_dates_baseline(monitor_setup: MonitorSetup) -> None:
    monitor_setup.set_fixed_dates_baseline(
        start_date=datetime(2023,1,1),
        end_date=datetime(2023,1,2)
    )

    assert monitor_setup.config.baseline == TimeRangeBaseline(
        range=TimeRange(
            start=datetime(2023,1,1, tzinfo=timezone.utc),
            end=datetime(2023,1,2, tzinfo=timezone.utc)
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
    monitor_setup.target_matrix = ColumnMatrix(include=["some_specific_column"], segments=[])
    monitor_setup.apply()

    assert isinstance(monitor_setup.target_matrix, ColumnMatrix)
    assert monitor_setup.analyzer.targetMatrix == ColumnMatrix(include=["some_specific_column"], segments=[])


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
    def test_existing_monitor_monitor_setup_with_id(self, existing_monitor_setup) -> None:
        assert isinstance(existing_monitor_setup.config, StddevConfig)

    def test_create_monitor_from_existing_monitor_id(self, existing_monitor_setup) -> None:
        assert existing_monitor_setup.monitor.id == os.environ["MONITOR_ID"]

        new_credentials = MonitorCredentials(monitor_id="new_monitor_id")

        existing_monitor_setup.credentials = new_credentials
        existing_monitor_setup.apply()

        assert existing_monitor_setup.monitor.id == "new_monitor_id"
        assert existing_monitor_setup.analyzer.id == "new_monitor_id-analyzer"

def test_validate_if_columns_exist_before_setting(existing_monitor_setup: MonitorSetup) -> None:
    with pytest.raises(ValueError) as e:
        existing_monitor_setup.exclude_target_columns(columns=["test_exclude_column"])
        assert e.value == f"test_exclude_column is not present on {existing_monitor_setup.credentials.dataset_id}"

    with pytest.raises(ValueError) as e:
        existing_monitor_setup.set_target_columns(columns=["test_set_column"])
        assert e.value == f"test_set_column is not present on {existing_monitor_setup.credentials.dataset_id}"


def test_setup_with_passed_in_credentials(user_config: UserConfig) -> None:
    monitor_setup = MonitorSetup(
        monitor_id="different_id",
        config=user_config
    )
    
    assert monitor_setup.credentials.org_id == user_config.org_id


def test_setup_with_group_of_columns(monitor_setup) -> None:
    monitor_setup.set_target_columns(columns=["group:discrete"])
    monitor_setup.exclude_target_columns(columns=["group:output", "other_feature"])
    monitor_setup.apply()

def test_setup_with_wrong_group_column_type(monitor_setup) -> None:
    with pytest.raises(ValueError):
        monitor_setup.set_target_columns(columns=["group:inputs"])


def test_dataset_matrix_is_auto_setup_if_model_metrics(monitor_setup):
    monitor_setup.config = FixedThresholdsConfig(
        metric=DatasetMetric.classification_accuracy,
        lower=0.75
    )
    monitor_setup.apply()
    
    assert monitor_setup.target_matrix == DatasetMatrix(segments=[])
    assert monitor_setup.analyzer.targetMatrix == DatasetMatrix(segments=[])
    
    monitor_setup.config = FixedThresholdsConfig(
        metric=SimpleColumnMetric.count_bool,
        lower=0.75
    )
    monitor_setup.apply()
    
    assert isinstance(
        monitor_setup.target_matrix,
        ColumnMatrix
    )
    
    assert isinstance(
        monitor_setup.analyzer.targetMatrix,
        ColumnMatrix
    )

def test_apply_wont_change_monitor_columns(monitor_setup):
    monitor_setup.set_target_columns(columns=["prediction_temperature", "temperature"])
    monitor_setup.apply()
    
    assert monitor_setup.analyzer.targetMatrix != ColumnMatrix(include=["*"] , exclude=[], segments=[])


def test_apply_wont_erase_existing_preconfig(monitor_setup):
    monitor_setup.config = FixedThresholdsConfig(
        metric=DatasetMetric.classification_accuracy,
        lower=0.75
    )
    
    monitor_setup.target_matrix = DatasetMatrix(segments=[Segment(tags=[SegmentTag(key="segment_a", value="value_a")])])
    
    monitor_setup.apply()
    assert monitor_setup.analyzer.targetMatrix == DatasetMatrix(segments=[Segment(tags=[SegmentTag(key="segment_a", value="value_a")])])
