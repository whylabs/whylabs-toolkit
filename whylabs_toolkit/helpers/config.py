import os
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigVars(Enum):
    ORG_ID = 1
    DATASET_ID = 2
    WHYLABS_API_KEY = 3
    WHYLABS_HOST = "https://api.whylabsapp.com"
    WHYLABS_PRIVATE_API_ENDPOINT = 5


class Config:
    def get_whylabs_api_key(self) -> str:
        return Validations.require(ConfigVars.WHYLABS_API_KEY)

    def get_whylabs_host(self) -> str:
        _private_api_endpoint = Validations.get_or_default(ConfigVars.WHYLABS_PRIVATE_API_ENDPOINT)
        if _private_api_endpoint and isinstance(_private_api_endpoint, str):
            logger.debug(f"Using private API endpoint: {_private_api_endpoint}")
            return _private_api_endpoint
        return Validations.get_or_default(ConfigVars.WHYLABS_HOST)

    def get_default_org_id(self) -> str:
        return Validations.require(ConfigVars.ORG_ID)

    def get_default_dataset_id(self) -> str:
        return Validations.require(ConfigVars.DATASET_ID)


class UserConfig(Config):
    def __init__(self, api_key: str, org_id: str, dataset_id: str, whylabs_host: str = ConfigVars.WHYLABS_HOST.value):
        self.api_key = api_key
        self.whylabs_host = whylabs_host
        self.org_id = org_id
        self.dataset_id = dataset_id

    def get_whylabs_api_key(self) -> str:
        return self.api_key

    def get_whylabs_host(self) -> str:
        return self.whylabs_host

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
