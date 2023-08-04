import logging
import json
from pathlib import Path
from typing import Optional, Union, Any, List

from jsonschema import validate, ValidationError
from whylabs_client.api.notification_settings_api import NotificationSettingsApi
from whylabs_client.api.models_api import ModelsApi

from whylabs_toolkit.monitor.manager.monitor_setup import MonitorSetup
from whylabs_toolkit.monitor.models import *
from whylabs_toolkit.helpers.monitor_helpers import get_model_granularity
from whylabs_toolkit.helpers.config import Config
from whylabs_toolkit.helpers.utils import get_monitor_api, get_notification_api


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitorManager:
    def __init__(
        self,
        setup: MonitorSetup,
        eager: Optional[bool] = None,
        notifications_api: Optional[NotificationSettingsApi] = None,
        monitor_api: Optional[ModelsApi] = None,
        config: Config = Config(),
    ) -> None:
        self._setup = setup
        self.__notifications_api = notifications_api or get_notification_api(config=config)
        self.__monitor_api = monitor_api or get_monitor_api(config=config)
        self.__eager = eager

    def _get_existing_notification_actions(self) -> List[str]:
        actions_dict_list = self.__notifications_api.list_notification_actions(org_id=self._setup.credentials.org_id)
        action_ids = []
        for action in actions_dict_list:
            action_ids.append(action.get("id"))
        return action_ids

    @staticmethod
    def get_notification_request_payload(action: Union[SlackWebhook, EmailRecipient, PagerDuty]) -> str:
        if isinstance(action, SlackWebhook):
            return "slackWebhook"
        elif isinstance(action, EmailRecipient):
            return "email"
        elif isinstance(action, PagerDuty):
            return "pagerDutyKey"
        else:
            raise ValueError(
                f"Can't work with {action} type. Available options are SlackWebhook, PagerDuty and EmailRecipient."
            )

    def _update_notification_actions(self) -> None:
        """
        Updates the notification actions to be passed to WhyLabs based on the actions defined in the MonitorBuilder object.
        """
        if not self._setup.monitor:
            raise ValueError("You must call apply() on your MonitorSetup object!")

        existing_actions = self._get_existing_notification_actions()

        for action in self._setup.monitor.actions:
            if isinstance(action, GlobalAction):
                continue

            if action.id not in existing_actions:
                logger.info(f"Didn't find a {action.type} action under the ID {action.id}, creating one now!")
                payload_key = self.get_notification_request_payload(action=action)
                self.__notifications_api.put_notification_action(
                    org_id=self._setup.credentials.org_id,
                    type=action.type.upper(),
                    action_id=action.id,
                    body={payload_key: action.destination},
                )

        if self._setup.monitor:
            self._setup.monitor.actions = [
                action if isinstance(action, GlobalAction) else GlobalAction(target=action.id)
                for action in self._setup.monitor.actions
            ]

    def _get_current_monitor_config(self) -> Optional[Any]:
        monitor_config = self.__monitor_api.get_monitor_config_v3(
            org_id=self._setup.credentials.org_id, dataset_id=self._setup.credentials.dataset_id
        )
        return monitor_config

    def dump(self) -> Any:
        self._update_notification_actions()

        doc = Document(
            orgId=self._setup.credentials.org_id,
            datasetId=self._setup.credentials.dataset_id,
            granularity=get_model_granularity(
                org_id=self._setup.credentials.org_id, dataset_id=self._setup.credentials.dataset_id  # type: ignore
            ),
            analyzers=[self._setup.analyzer],
            monitors=[self._setup.monitor],
            allowPartialTargetBatches=self.__eager,
        )
        return doc.json(indent=2, exclude_none=True)

    def validate(self) -> bool:
        try:
            Monitor.validate(self._setup.monitor)
            Analyzer.validate(self._setup.analyzer)

            with open(f"{Path(__file__).parent.parent.resolve()}/schema/schema.json", "r") as f:
                schema = json.load(f)
            document = self.dump()
            validate(instance=json.loads(document), schema=schema)
            return True
        except ValidationError as e:
            raise e

    def save(self) -> None:
        if self.validate() is True:
            self.__monitor_api.put_analyzer(
                org_id=self._setup.credentials.org_id,
                dataset_id=self._setup.credentials.dataset_id,
                analyzer_id=self._setup.credentials.analyzer_id,
                body=self._setup.analyzer.dict(exclude_none=True),  # type: ignore
            )
            self.__monitor_api.put_monitor(
                org_id=self._setup.credentials.org_id,
                dataset_id=self._setup.credentials.dataset_id,
                monitor_id=self._setup.credentials.monitor_id,
                body=self._setup.monitor.dict(exclude_none=True),  # type: ignore
            )
        if self.__eager is not None:
            current_config = self._get_current_monitor_config()

            if self.__eager != current_config.get("allowPartialTargetBatches"):  # type: ignore
                current_config["allowPartialTargetBatches"] = self.__eager  # type: ignore
                self.__monitor_api.put_monitor_config_v3(
                    org_id=self._setup.credentials.org_id,
                    dataset_id=self._setup.credentials.dataset_id,
                    body=current_config,
                )
