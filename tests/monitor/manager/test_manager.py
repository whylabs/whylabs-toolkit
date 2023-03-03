import json
import os
from typing import Dict
from unittest import TestCase
from unittest.mock import call, MagicMock

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


class TestNotificationActions(TestCase):
    def setUp(self) -> None:
        self.monitor_builder = MagicMock()
        self.monitor_builder.credentials.org_id = 'test_org'
        
        self.monitor_builder.monitor = MagicMock()
        self.monitor_builder.monitor.actions = [
            SlackWebhook(id='slack1', destination='https://slack.com/webhook'),
            EmailRecipient(id='email1', destination='test@example.com'),
            GlobalAction(target="existing-pagerDuty")
        ]
        
        self.notifications_api = MagicMock()
        self.notifications_api.list_notification_actions.return_value = []
        
        self.models_api = MagicMock()

        self.monitor_manager = MonitorManager(builder = self.monitor_builder, notifications_api=self.notifications_api, models_api=self.models_api)
        

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

        assert GlobalAction(target='existing-pagerDuty') in self.monitor_builder.monitor.actions 

    def test_existing_notification_actions_are_fetched(self) -> None:
        self.monitor_manager._update_notification_actions()

        self.notifications_api.list_notification_actions.assert_called_once_with(
            org_id='test_org'
        )

    def test_error_is_raised_if_monitor_is_none(self) -> None:
        self.monitor_builder.monitor = None

        with self.assertRaises(ValueError):
            self.monitor_manager._update_notification_actions()
