import json
import os
from typing import Dict

import pytest
from jsonschema import ValidationError

from whylabs_toolkit.monitor.manager import MonitorManager, MonitorSetup
from whylabs_toolkit.monitor.models import GlobalAction
from tests.helpers.test_monitor_helpers import BaseTestMonitor
from whylabs_toolkit.helpers.monitor_helpers import get_monitor, get_analyzer_ids, get_monitor_config


class TestModelManager(BaseTestMonitor):
    @pytest.fixture
    def manager(self, existing_monitor_setup: MonitorSetup) -> MonitorManager:
        mm = MonitorManager(setup=existing_monitor_setup)
        return mm

    def test_dump(self, manager: MonitorManager) -> None:
        document = manager.dump()
        assert isinstance(json.loads(document), Dict)

    def test_validate(self, manager: MonitorManager) -> None:
        assert manager.validate()

    def test_failing_validation(self, monitor_setup: MonitorSetup) -> None:
        monitor_setup.actions = [GlobalAction(target="some_long_id")]
        monitor_setup.config.mode = "weird_mode" # type: ignore
        monitor_setup.apply()

        manager = MonitorManager(setup=monitor_setup)
        with pytest.raises(ValidationError):
            manager.validate()

    def test_save(self, manager: MonitorManager) -> None:
        manager.save()

        monitor = get_monitor(
            org_id=os.environ["WHYLABS_DEFAULT_ORG_ID"],
            dataset_id=os.environ["WHYLABS_DEFAULT_DATASET_ID"],
            monitor_id=os.environ["WHYLABS_DEFAULT_MONITOR_ID"]
        )

        assert monitor is not None
        assert isinstance(monitor, Dict)
        assert monitor.get("id") == os.environ["WHYLABS_DEFAULT_MONITOR_ID"]

        assert get_analyzer_ids(
            org_id=os.environ["WHYLABS_DEFAULT_ORG_ID"],
            dataset_id=os.environ["WHYLABS_DEFAULT_DATASET_ID"],
            monitor_id=os.environ["WHYLABS_DEFAULT_MONITOR_ID"]
        )
    
    def test_monitor_running_eagerly(self, existing_monitor_setup: MonitorSetup) -> None:
        mm = MonitorManager(setup=existing_monitor_setup, eager=True)
        actual_doc = mm.dump()
        assert json.loads(actual_doc)["allowPartialTargetBatches"] == True
        
        mm.save()
        
        expected_result = get_monitor_config(
            dataset_id=existing_monitor_setup.credentials.dataset_id, 
            org_id=existing_monitor_setup.credentials.org_id
        )
        
        assert expected_result["allowPartialTargetBatches"] == True
    
        new_mm = MonitorManager(setup=existing_monitor_setup, eager=False)
        new_mm.save()
        
        new_expected_result = get_monitor_config(
            dataset_id=existing_monitor_setup.credentials.dataset_id, 
            org_id=existing_monitor_setup.credentials.org_id
        )
        
        assert new_expected_result["allowPartialTargetBatches"] == False
