from enum import Enum
import os


class ConfigVars(Enum):
    WHYLABS_API_KEY = ""
    WHYLABS_HOST = "https://api.whylabsapp.com"
    ORG_ID = ""


class Config:
    def get_whylabs_api_key(self) -> str:
        return Validations.require(ConfigVars.WHYLABS_API_KEY)

    def get_whylabs_host(self) -> str:
        return Validations.get_or_default(ConfigVars.WHYLABS_HOST)

    def get_default_org_id(self) -> str:
        return Validations.require(ConfigVars.ORG_ID)


class Validations:
    @staticmethod
    def require(env: ConfigVars) -> str:
        val = os.getenv(env.name)
        if val is None or val == "":
            raise TypeError(f"Missing {ConfigVars.WHYLABS_API_KEY.name} env variable.")
        return val

    @staticmethod
    def get_or_default(env: ConfigVars) -> str:
        val = os.getenv(env.name, env.value)
        if not val:
            raise TypeError(f"No default value for {env.name}")
        return val
