from typing import Union

from whylabs_client.api.dataset_profile_api import DatasetProfileApi
from whylabs_client.api.models_api import ModelsApi
from whylabs_client.api.notification_settings_api import NotificationSettingsApi

from whylabs_toolkit.helpers.client import create_client
from whylabs_toolkit.monitor.models import SlackWebhook, EmailRecipient, GlobalAction


def get_models_api() -> ModelsApi:
    return ModelsApi(api_client=create_client())


def get_dataset_profile_api() -> DatasetProfileApi:
    return DatasetProfileApi(api_client=create_client())


def get_notification_api() -> NotificationSettingsApi:
    return NotificationSettingsApi(api_client=create_client())


def get_notification_request_payload(action: Union[SlackWebhook, EmailRecipient]) -> str:
    if isinstance(action, SlackWebhook):
        return "slackWebhook"
    elif isinstance(action, EmailRecipient):
        return "email"
    else:
        raise ValueError(f"Can't work with {action} type. Available options are SlackWebhook and EmailRecipient.")
