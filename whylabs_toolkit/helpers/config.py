import os
import logging
from enum import Enum
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigVars(Enum):
    WHYLABS_DEFAULT_ORG_ID = 1
    WHYLABS_DEFAULT_DATASET_ID = 2
    WHYLABS_API_ENDPOINT = "https://api.whylabsapp.com"
    # keeping these three for backwards compatibility, but they should be removed in the future
    ORG_ID = 3
    DATASET_ID = 4
    WHYLABS_API_KEY = 5
    # TODO remove these two and favor only WHYLABS_API_ENDPOINT
    WHYLABS_HOST = WHYLABS_API_ENDPOINT
    WHYLABS_PRIVATE_API_ENDPOINT = 6


class Config:
    def get_whylabs_api_key(self) -> str:
        return Validations.require(ConfigVars.WHYLABS_API_KEY)

    # TODO deprecate this method
    def get_whylabs_host(self) -> str:
        logger.warning("this method will be deprecated in future releases. use get_whylabs_api_endpoint instead")
        whylabs_host = Validations.get(ConfigVars.WHYLABS_HOST)
        if whylabs_host is not None:
            logger.warning("WHYLABS_HOST will be deprecated, use WHYLABS_API_ENDPOINT instead.")
            return whylabs_host
        return self.get_whylabs_api_endpoint()

    def get_whylabs_api_endpoint(self) -> str:
        _private_api_endpoint = Validations.get(ConfigVars.WHYLABS_PRIVATE_API_ENDPOINT)
        if _private_api_endpoint and isinstance(_private_api_endpoint, str):
            logger.warning(
                f"Using private API endpoint: {_private_api_endpoint}. "
                f"WHYLABS_PRIVATE_API_ENDPOINT will be deprecated in the future. "
                f"You should use the WHYLABS_API_ENDPOINT for this purpose."
            )
            return _private_api_endpoint
        return Validations.get_or_default(ConfigVars.WHYLABS_API_ENDPOINT)

    def get_default_org_id(self) -> str:
        org_id = Validations.get(ConfigVars.WHYLABS_DEFAULT_ORG_ID) or Validations.get(ConfigVars.ORG_ID)
        if org_id is None:
            raise TypeError("You need to specify WHYLABS_DEFAULT_ORG_ID")
        return org_id

    def get_default_dataset_id(self) -> str:
        dataset_id = Validations.get(ConfigVars.WHYLABS_DEFAULT_DATASET_ID) or Validations.get(ConfigVars.DATASET_ID)
        if dataset_id is None:
            raise TypeError("You need to specify WHYLABS_DEFAULT_DATASET_ID")
        return dataset_id


class UserConfig(Config):
    def __init__(
        self,
        api_key: str,
        org_id: str,
        dataset_id: str,
        whylabs_api_endpoint: str = ConfigVars.WHYLABS_API_ENDPOINT.value,
    ):
        self.api_key = api_key
        self.whylabs_api_endpoint = whylabs_api_endpoint
        self.whylabs_host = self.whylabs_api_endpoint
        self.org_id = org_id
        self.dataset_id = dataset_id

    def get_whylabs_api_key(self) -> str:
        return self.api_key

    def get_whylabs_api_endpoint(self) -> str:
        return self.whylabs_api_endpoint

    def get_whylabs_host(self) -> str:
        return self.get_whylabs_api_endpoint()

    def get_default_org_id(self) -> str:
        return self.org_id

    def get_default_dataset_id(self) -> str:
        return self.dataset_id


class Validations:
    @staticmethod
    def require(env: ConfigVars) -> str:
        val = os.getenv(env.name)
        if not val:
            raise TypeError(f"Missing {env.name} env variable.")
        return val

    @staticmethod
    def get_or_default(env: ConfigVars) -> str:
        val = os.getenv(env.name, env.value)
        if not val:
            raise TypeError(f"No default value for {env.name}")
        return val

    @staticmethod
    def get(env: ConfigVars) -> Optional[str]:
        return os.getenv(env.name)
