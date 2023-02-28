import os
import pytz
from datetime import datetime

import pytest

from whylabs_toolkit.monitor.manager import MonitorBuilder
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
        columns=["test_exclude_column"]
    )

    assert builder._exclude_columns == ["test_exclude_column"]


def test_set_target_columns(builder):
    builder.exclude_target_columns(
        columns=["test_add_column"]
    )

    assert builder._target_columns == ["test_add_column"]


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

    builder.exclude_target_columns(columns=["test_exclude_column"])

    assert builder._target_columns == []
    assert builder._exclude_columns == ["test_exclude_column"]

    builder.set_target_columns(columns=["test_add_column"])

    assert builder._target_columns == ["test_add_column"]
    assert builder._exclude_columns == ["test_exclude_column"]

    builder.build()

    assert builder.target_matrix == ColumnMatrix(
        include=["test_add_column"], exclude=["test_exclude_column"], segments=[]
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
