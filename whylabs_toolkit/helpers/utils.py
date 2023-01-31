from whylabs_client.api.dataset_profile_api import DatasetProfileApi
from whylabs_client.api.models_api import ModelsApi

from whylabs_toolkit.helpers.client import client


def get_models_api() -> ModelsApi:
    return ModelsApi(api_client=client)


def get_dataset_profile_api() -> DatasetProfileApi:
    return DatasetProfileApi(api_client=client)
