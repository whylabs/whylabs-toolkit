import os
from enum import Enum


class ConfigVars(Enum):
    ORG_ID = 1
    DATASET_ID = 2
    WHYLABS_API_KEY = 3
    WHYLABS_HOST = "https://api.whylabsapp.com"


class Config:
    @staticmethod
    def get_whylabs_api_key() -> str:
        return Validations.require(ConfigVars.WHYLABS_API_KEY)

    @staticmethod
    def get_whylabs_host() -> str:
        return Validations.get_or_default(ConfigVars.WHYLABS_HOST)

    @staticmethod
    def get_default_org_id() -> str:
        return Validations.require(ConfigVars.ORG_ID)

    @staticmethod
    def get_default_dataset_id() -> str:
        return Validations.require(ConfigVars.DATASET_ID)


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
