import os

import pytest
from whylabs_client.exceptions import NotFoundException

from whylabs_toolkit.helpers.monitor_helpers import (
    delete_monitor,
    get_analyzer_ids,
    get_monitor_config
)
from whylabs_toolkit.helpers.utils import get_models_api


ORG_ID = os.environ["ORG_ID"]
DATASET_ID = os.environ["DATASET_ID"]
MONITOR_ID = os.environ["MONITOR_ID"]
ANALYZER_ID = os.environ["ANALYZER_ID"]
MONITOR_BODY = {
    "id": MONITOR_ID, "analyzerIds": [ANALYZER_ID], 
    "schedule": {"type": "immediate"}, 
    "mode": {"type": "DIGEST"}, "disabled": False, "actions": [], 
    "metadata": {
        "schemaVersion": 1, 
        "author": "system", 
        "updatedTimestamp": 1671824015981, 
        "version": 1
        }
}
ANALYZER_BODY = {
    "config": {
        "baseline": {
            "size": 7, "type": "TrailingWindow"
        }, 
        "metric": "inferred_data_type", "operator": "eq", "type": "comparison"
    }, 
    "id": ANALYZER_ID, 
    "schedule": {"type": "fixed", "cadence": "monthly"}, 
    "targetMatrix": {"include": ["*"], "segments": [], "type": "column"}, 
    "metadata": {
        "schemaVersion": 1, 
        "author": "system", 
        "updatedTimestamp": 1671824015105, 
        "version": 1
    }
}

class TestDeleteMonitor:
    @classmethod
    def setup_class(cls) -> None:
        api = get_models_api()
        api.put_monitor(
            org_id=ORG_ID,
            dataset_id=DATASET_ID,
            monitor_id=MONITOR_ID,
            body=MONITOR_BODY
        )
        
        api.put_analyzer(
            org_id=ORG_ID,
            dataset_id=DATASET_ID,
            analyzer_id=MONITOR_ID,
            body=ANALYZER_BODY
        )

    def test_delete_monitor(self) -> None:
        delete_monitor(
            org_id=ORG_ID,
            dataset_id=DATASET_ID,
            monitor_id=MONITOR_ID
        )

        # Checking both monitor and analyzers were deleted

        monitor_config = get_monitor_config(
            org_id=ORG_ID,
            dataset_id=DATASET_ID
        )

        for monitor in monitor_config["monitors"]:
            assert MONITOR_ID not in monitor["id"]

        with pytest.raises(NotFoundException):
            get_analyzer_ids(
                org_id=ORG_ID,
                dataset_id=DATASET_ID,
                monitor_id=MONITOR_ID
            )
