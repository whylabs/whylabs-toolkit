import os

from whylabs_toolkit.helpers.config import Config
from whylabs_toolkit.helpers.models import get_models_api


def test_setup_with_private_endpoint():
    os.environ["WHYLABS_PRIVATE_API_ENDPOINT"] = "http://private.com"
    
    api_endpoint = Config().get_whylabs_host()
    
    assert api_endpoint == "http://private.com"
    
    models_api = get_models_api()
    
    assert models_api.api_client.configuration.host == "http://private.com"
