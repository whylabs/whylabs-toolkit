from whylabs_client.api.dataset_profile_api import DatasetProfileApi
from whylabs_client.api.models_api import ModelsApi
from whylabs_client.api.notification_settings_api import NotificationSettingsApi
from whylabs_client.api.monitor_api import MonitorApi

from whylabs_toolkit.helpers.client import create_client
from whylabs_toolkit.helpers.config import Config


def get_models_api(config: Config = Config()) -> ModelsApi:
    return ModelsApi(api_client=create_client(config=config))


def get_dataset_profile_api(config: Config = Config()) -> DatasetProfileApi:
    return DatasetProfileApi(api_client=create_client(config=config))


def get_notification_api(config: Config = Config()) -> NotificationSettingsApi:
    return NotificationSettingsApi(api_client=create_client(config=config))


def get_monitor_api(config: Config = Config()) -> MonitorApi:
    return MonitorApi(api_client=create_client(config=config))
