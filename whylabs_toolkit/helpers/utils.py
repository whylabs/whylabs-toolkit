from typing import Optional

from whylabs_toolkit.helpers.client import client
from whylabs_toolkit.helpers.config import Config
from whylabs_client.api.models_api import ModelsApi
from whylabs_client.api.dataset_profile_api import DatasetProfileApi


def get_models_api(org_id: Optional[str] = None) -> ModelsApi:
    org_id = org_id or Config().get_default_org_id()
    return ModelsApi(api_client=client)


def get_dataset_profile_api(org_id: Optional[str] = None) -> DatasetProfileApi:
    org_id = org_id or Config().get_default_org_id()
    return DatasetProfileApi(api_client=client)
