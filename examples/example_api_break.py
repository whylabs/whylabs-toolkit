from whylabs_client.api.models_api import ModelsApi
from whylabs_client import ApiClient, Configuration
from whylabs_toolkit.monitor.models import *


client = ApiClient()
client_config = Configuration(host="host")
client_config.api_key = {"ApiKeyAuth": "api_key"}
client_config.discard_unknown_keys = True

api = ModelsApi(api_client=client)

monitor = Monitor(
    id = "monitor_id",
    disabled=False,
    displayName="monitor_id",
    tags=[],
    analyzerIds=["analyzer_id"],
    schedule=ImmediateSchedule(type="immediate"),
    mode=EveryAnomalyMode(type='EVERY_ANOMALY'),
    actions=[]
)

api.put_monitor(
    org_id="org_id",
    dataset_id="dataset_id",
    monitor_id="monitor_id",
    body=monitor.dict()
)