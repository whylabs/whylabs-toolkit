import json
import os
from typing import Dict

import pytest

from whylabs_toolkit.monitor.manager import MonitorManager
from whylabs_toolkit.monitor.models import *
from tests.helpers.test_monitor_helpers import TestDeleteMonitor
from whylabs_toolkit.helpers.monitor_helpers import delete_monitor, get_monitor, get_analyzer_ids


class TestModelManager:
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
    @pytest.fixture
    def manager(self, existing_monitor_builder) -> MonitorManager:
        mm = MonitorManager(builder=existing_monitor_builder)
        return mm
    def test_get_granularity(self, manager):
        granularity = manager.get_granularity()
        assert granularity == Granularity.monthly

    def test_dump(self, manager):
        document = manager.dump()
        assert isinstance(json.loads(document), Dict)

    def test_validate(self, manager):
        # TODO add json schema validation
        assert manager.validate() is True
    def test_save(self, manager):
        manager.save()

        monitor = get_monitor(
            org_id=os.environ["ORG_ID"],
            dataset_id=os.environ["DATASET_ID"],
            monitor_id=os.environ["MONITOR_ID"]
        )

        assert monitor is not None
        assert isinstance(monitor, Dict)
        assert monitor.get("id") == os.environ["MONITOR_ID"]

        assert get_analyzer_ids(
            org_id=os.environ["ORG_ID"],
            dataset_id=os.environ["DATASET_ID"],
            monitor_id=os.environ["MONITOR_ID"]
        )
