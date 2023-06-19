import os

from whylabs_toolkit.helpers.monitor_helpers import (
    delete_monitor,
    get_model_granularity,
    get_monitor_config
)
from whylabs_toolkit.helpers.utils import get_monitor_api
from whylabs_toolkit.utils.granularity import Granularity


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
        "metric": "median",
        "type": "stddev",
        "factor": 2.0,
        "minBatchSize": 1,
        "baseline": {
          "type": "TrailingWindow",
          "size": 14
        }
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

class BaseTestMonitor:
    @classmethod
    def setup_class(cls) -> None:
        api = get_monitor_api()
        api.put_monitor(
            org_id=ORG_ID,
            dataset_id=DATASET_ID,
            monitor_id=MONITOR_ID,
            body=MONITOR_BODY  # type: ignore
        )

        api.put_analyzer(
            org_id=ORG_ID,
            dataset_id=DATASET_ID,
            analyzer_id=ANALYZER_ID,
            body=ANALYZER_BODY  # type: ignore
        )

    @classmethod
    def teardown_class(cls) -> None:
        delete_monitor(
            org_id=ORG_ID,
            dataset_id=DATASET_ID,
            monitor_id=MONITOR_ID
        )


class TestDeleteMonitor(BaseTestMonitor):
    @classmethod
    def teardown_class(cls) -> None:
        pass

    def test_get_analyzer_id(self) -> None:
        pass

    def test_get_analyzer_ids(self) -> None:
        pass

    def test_get_monitor_config(self) -> None:
        pass

    def test_get_monitor(self) -> None:
        pass

    def test_get_granularity(self) -> None:
        granularity = get_model_granularity(org_id=ORG_ID, dataset_id=DATASET_ID)
        assert granularity == Granularity.monthly


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

        for analyzer in monitor_config["analyzers"]:
            assert ANALYZER_ID not in analyzer["id"]