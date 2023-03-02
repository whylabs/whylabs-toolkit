import json
import os
from typing import Dict

import pytest

from whylabs_toolkit.monitor.manager import MonitorManager, MonitorBuilder
from whylabs_toolkit.monitor.models import *
from tests.helpers.test_monitor_helpers import BaseTestMonitor
from whylabs_toolkit.helpers.monitor_helpers import delete_monitor, get_monitor, get_analyzer_ids


class TestModelManager(BaseTestMonitor):
    @pytest.fixture
    def manager(self, existing_monitor_builder: MonitorBuilder) -> MonitorManager:
        mm = MonitorManager(builder=existing_monitor_builder)
        return mm
    def test_get_granularity(self, manager: MonitorManager) -> None:
        granularity = manager.get_granularity()
        assert granularity == Granularity.monthly

    def test_parse_actions_object(self, existing_monitor_builder: MonitorBuilder) -> None:
        existing_monitor_builder.actions = [
            EmailRecipient(target="email@example.com")
        ]
        
        existing_monitor_builder.build()
        
        mm = MonitorManager(builder=existing_monitor_builder)
        
        mm._parse_monitor_actions()
        if mm._builder.monitor:
            for action in mm._builder.monitor.actions:
                assert action.type == "global"
    
    def test_dump(self, manager: MonitorManager) -> None:
        document = manager.dump()
        assert isinstance(json.loads(document), Dict)

    def test_validate(self, manager: MonitorManager) -> None:
        # TODO add json schema validation
        assert manager.validate() is True
    def test_save(self, manager: MonitorManager) -> None:
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
