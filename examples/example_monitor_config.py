from whylabs_toolkit.helpers.monitor_config import (delete_monitor,
                                                    get_analyzer_ids,
                                                    get_monitor_config)

delete_monitor(
    org_id="org_id",
    dataset_id="dataset_id",
    monitor_id="monitor_id"
)

# Checking both monitor and analyzers were deleted

monitor_config = get_monitor_config(
    org_id="org_id",
    dataset_id="dataset_id"
)

for monitor in monitor_config["monitors"]:
    assert "monitor_id" not in monitor["id"]
    
analyzers_list = get_analyzer_ids(
    org_id="org_id",
    dataset_id="dataset_id",
    monitor_id="monitor_id"
)
assert not analyzers_list         
