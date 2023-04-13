import json
import os
from typing import Dict
from unittest import TestCase
from unittest.mock import call, MagicMock

import pytest
from jsonschema import ValidationError

from whylabs_toolkit.monitor.manager import MonitorManager, MonitorSetup
from whylabs_toolkit.monitor.models import *
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
        monitor_setup.actions = [EmailRecipient(id="some_long_id", destination="someemail@email.com")]
        monitor_setup.config.mode = "weird_mode" # type: ignore
        monitor_setup.apply()

        manager = MonitorManager(setup=monitor_setup)
        with pytest.raises(ValidationError):
            manager.validate()

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
    
    def test_monitor_running_eagerly(self, existing_monitor_setup: MonitorSetup):
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
        
    
        

class TestNotificationActions(TestCase):
    def setUp(self) -> None:
        self.monitor_setup = MagicMock()
        self.monitor_setup.credentials.org_id = 'test_org'
        
        self.monitor_setup.monitor = MagicMock()
        self.monitor_setup.monitor.actions = [
            SlackWebhook(id='slack1', destination='https://slack.com/webhook'),
            EmailRecipient(id='email1', destination='test@example.com'),
            GlobalAction(target="existing-pagerDuty")
        ]
        
        self.notifications_api = MagicMock()
        self.notifications_api.list_notification_actions.return_value = []
        
        self.monitor_api = MagicMock()

        self.monitor_manager = MonitorManager(
            setup = self.monitor_setup,
            notifications_api=self.notifications_api,
            monitor_api=self.monitor_api
        )
        

    def test_notification_actions_are_updated(self) -> None:
        self.monitor_manager._update_notification_actions()

        expected_calls = [
            call(
                org_id='test_org',
                type='EMAIL',
                action_id='email1',
                body={'email': 'test@example.com'}
            ),
            call(
                org_id='test_org',
                type='SLACK',
                action_id='slack1',
                body={'slackWebhook': 'https://slack.com/webhook'}
            )
        ]

        for call_args in expected_calls:
            assert call_args in self.notifications_api.put_notification_action.call_args_list 

    def test_global_actions_are_made(self) -> None:
        self.monitor_manager._update_notification_actions()

        assert GlobalAction(target='existing-pagerDuty') in self.monitor_setup.monitor.actions

    def test_existing_notification_actions_are_fetched(self) -> None:
        self.monitor_manager._update_notification_actions()

        self.notifications_api.list_notification_actions.assert_called_once_with(
            org_id='test_org'
        )

    def test_error_is_raised_if_monitor_is_none(self) -> None:
        self.monitor_setup.monitor = None

        with self.assertRaises(ValueError):
            self.monitor_manager._update_notification_actions()
