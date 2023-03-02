from typing import Union, Dict

from whylabs_client.api.dataset_profile_api import DatasetProfileApi
from whylabs_client.api.models_api import ModelsApi
from whylabs_client.api.notification_settings_api import NotificationSettingsApi

from whylabs_toolkit.helpers.client import create_client
from whylabs_toolkit.monitor.models import SlackWebhook, EmailRecipient


def get_models_api() -> ModelsApi:
    return ModelsApi(api_client=create_client())


def get_dataset_profile_api() -> DatasetProfileApi:
    return DatasetProfileApi(api_client=create_client())


def get_notification_api() -> NotificationSettingsApi:
    return NotificationSettingsApi(api_client=create_client())



def get_notification_request_payload(action: Union[SlackWebhook, EmailRecipient]) -> Dict[str, str]:
    if isinstance(action, SlackWebhook):
        return "slackWebhook"
    elif isinstance(action, EmailRecipient):
        return "email"
