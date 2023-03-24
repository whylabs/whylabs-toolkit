import os

from whylabs_toolkit.helpers.config import UserConfig
from whylabs_toolkit.helpers.utils import get_dataset_profile_api, get_models_api, get_notification_api


def test_get_apis_with_different_config(user_config: UserConfig) -> None:
    dataset_api = get_dataset_profile_api(config = user_config)
    assert dataset_api.api_client.configuration.api_key["ApiKeyAuth"] == user_config.api_key
    
    models_api = get_models_api(config = user_config)
    assert models_api.api_client.configuration.api_key["ApiKeyAuth"] == user_config.api_key
    
    notifications_api = get_notification_api(config = user_config)
    assert notifications_api.api_client.configuration.api_key["ApiKeyAuth"] == user_config.api_key
