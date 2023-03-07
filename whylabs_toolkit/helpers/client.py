from whylabs_client import ApiClient, Configuration

from .config import Config


def create_client(config: Config = Config()) -> ApiClient:
    client_config = Configuration(host=config.get_whylabs_host())
    client_config.api_key = {"ApiKeyAuth": config.get_whylabs_api_key()}
    client_config.discard_unknown_keys = True
    return ApiClient(client_config)
