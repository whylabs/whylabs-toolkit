import os
import json
import logging
from typing import Any


import requests

from whylabs_toolkit.helpers.utils import get_models_api
from whylabs_toolkit.helpers.client import client
from whylabs_client.exceptions import ApiValueError

BASE_ENDPOINT = "https://api.whylabsapp.com"
logger = logging.getLogger(__name__)


# TODO create deactivate_monitor

# TODO Set up a monitor/alert on a text feature that triggers alerts based on an
# x% increase or y change in std dev for the total volume (counts?) received for that particular feature?


def get_monitor_config(org_id: str, dataset_id: str) -> Any:
    # TODO change to commented section once whylabs_client is updated
    # api = get_models_api(org_id=org_id)
    # monitor_config = api.get_monitor_config_v3(org_id=org_id, dataset_id=dataset_id)
    get_monitor_config_url = f"v0/organizations/{org_id}/models/{dataset_id}/monitor-config/v3"
    req_url = os.path.join(BASE_ENDPOINT, get_monitor_config_url)
    resp = requests.get(
        url=req_url,
        headers={"accept": "application/json", "X-API-Key": client.configuration.api_key["ApiKeyAuth"]},
    )
    return json.loads(resp.content)


def get_analyzer_ids(org_id: str, dataset_id: str, monitor_id: str) -> Any:
    monitor_config = get_monitor_config(org_id=org_id, dataset_id=dataset_id)
    for item in monitor_config["monitors"]:
        if item["id"] == monitor_id:
            resp = item["analyzerIds"]
    return resp


def delete_monitor(org_id: str, dataset_id: str, monitor_id: str) -> None:
    api = get_models_api()
    try:
        resp_monitor = api.delete_monitor(org_id=org_id, dataset_id=dataset_id, monitor_id=monitor_id)
        logger.debug(f"Deleted monitor with Resp:{resp_monitor}")
        analyzer_ids = get_analyzer_ids(org_id=org_id, dataset_id=dataset_id, monitor_id=monitor_id)
        for analyzer_id in analyzer_ids:
            resp_analyzer = api.delete_analyzer(org_id=org_id, dataset_id=dataset_id, analyzer_id=analyzer_id)
            logger.debug(f"Deleted analyzer with Resp:{resp_analyzer}")
    except ApiValueError as e:
        raise e


if __name__ == "__main__":
    print(
        get_monitor_config(
            org_id="org-fjx9Rz",
            dataset_id="model-7",
        )
    )
