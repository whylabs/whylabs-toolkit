from whylabs_client.api.dataset_profile_api import DatasetProfileApi
from whylabs_client.api.models_api import ModelsApi
from whylabs_client.api.notification_settings_api import NotificationSettingsApi

from whylabs_toolkit.helpers.client import create_client


def get_models_api() -> ModelsApi:
    return ModelsApi(api_client=create_client())


def get_dataset_profile_api() -> DatasetProfileApi:
    return DatasetProfileApi(api_client=create_client())


def get_notification_api() -> NotificationSettingsApi:
    return NotificationSettingsApi(api_client=create_client())
