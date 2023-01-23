import os

from whylabs_toolkit.helpers.monitor_config import (
    delete_monitor,
    get_analyzer_ids,
    get_monitor_config
)

ORG_ID = os.environ["ORG_ID"]
DATASET_ID = os.environ["DATASET_ID"]
MONITOR_ID = os.environ["MONITOR_ID"]


class TestDeleteMonitor:
    @classmethod
    def setup_class(cls) -> None:
        # TODO configure monitor + analyzer
        # put monitor
        # put analyzer
        pass

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

        analyzers_list = get_analyzer_ids(
            org_id=ORG_ID,
            dataset_id=DATASET_ID,
            monitor_id=MONITOR_ID
        )
        assert not analyzers_list
