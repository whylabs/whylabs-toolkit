import os
import pytz
from datetime import datetime

import pytest

from whylabs_toolkit.monitor.models import *
from tests.helpers.test_monitor_helpers import TestDeleteMonitor
from whylabs_toolkit.helpers.monitor_helpers import delete_monitor


def test_set_fixed_dates_baseline(builder):
    builder.set_fixed_dates_baseline(
        start_date=datetime(2023,1,1),
        end_date=datetime(2023,1,2)
    )

    assert builder.config.baseline == TimeRangeBaseline(
        range=TimeRange(
            start=datetime(2023,1,1, tzinfo=pytz.utc),
            end=datetime(2023,1,2, tzinfo=pytz.utc)
        )
    )

def test_exclude_target_columns(builder):
    builder.exclude_target_columns(
        columns=["prediction_temperature"]
    )

    assert builder._exclude_columns == ["prediction_temperature"]


def test_set_target_columns(builder):
    builder.set_target_columns(
        columns=["prediction_temperature"]
    )

    assert builder._target_columns == ["prediction_temperature"]


def test_build(builder):
    assert not builder.monitor
    assert not builder.analyzer

    builder.build()

    assert isinstance(builder.monitor, Monitor)
    assert isinstance(builder.analyzer, Analyzer)


def test_set_target_matrix(builder):
    builder.target_matrix = DatasetMatrix()
    builder.build()

    assert not isinstance(builder.target_matrix, ColumnMatrix)


def test_set_and_exclude_columns_keep_state(builder):
    assert builder._target_columns == []
    assert builder._exclude_columns == []

    builder.exclude_target_columns(columns=["prediction_temperature"])

    assert builder._target_columns == []
    assert builder._exclude_columns == ["prediction_temperature"]

    builder.set_target_columns(columns=["prediction_temperature"])

    assert builder._target_columns == ["prediction_temperature"]
    assert builder._exclude_columns == ["prediction_temperature"]

    builder.build()

    assert builder.target_matrix == ColumnMatrix(
        include=["prediction_temperature"], exclude=["prediction_temperature"], segments=[]
    )


class TestExistingMonitor:
    @classmethod
    def setup_class(cls):
        TestDeleteMonitor.setup_class()

    @classmethod
    def teardown_class(cls):
        delete_monitor(
            org_id=os.environ["ORG_ID"],
            dataset_id=os.environ["DATASET_ID"],
            monitor_id=os.environ["MONITOR_ID"]
        )

    def test_existing_monitor_builder_with_id(self, existing_monitor_builder):
        assert isinstance(existing_monitor_builder.config, StddevConfig)


def test_validate_if_columns_exist_before_setting(existing_monitor_builder):
    with pytest.raises(ValueError) as e:
        existing_monitor_builder.exclude_target_columns(columns=["test_exclude_column"])
        assert e.value == f"test_exclude_column is not present on {existing_monitor_builder.credentials.dataset_id}"

    with pytest.raises(ValueError) as e:
        existing_monitor_builder.set_target_columns(columns=["test_set_column"])
        assert e.value == f"test_set_column is not present on {existing_monitor_builder.credentials.dataset_id}"
