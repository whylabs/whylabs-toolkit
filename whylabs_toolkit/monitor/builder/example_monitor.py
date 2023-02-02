from typing import Optional

from whylabs_toolkit.helpers.config import Config
from .configs import FixedThresholdConfig, Metrics, MonitorConfig

class MonitorManager:
    def __init__(self, dataset_id: str, org_id: Optional[str] = None):
        self.dataset_id = dataset_id
        self.org_id = org_id or Config().get_default_org_id()

    def _generate_analyzer_template(self):
        # TODO return an Analyzer object with default fields
        pass

    def _generate_monitor_template(self):
        # TODO return a Monitor object with default fields
        pass

    def create_monitor(self, monitor_id: str, config: MonitorConfig):
        pass

manager = MonitorManager(
    org_id="some_org",
    dataset_id="some_id"
)

column_1_config = FixedThresholdConfig(
    threshold=20,
    direction="upper",
    metric=Metrics.COUNTS
)

manager.create_monitor(
    monitor_id="my_monitor_id",
    config=FixedThresholdConfig, # type: ignore
)

manager.update_monitor(...)
manager.pause_monitor(...)
manager.delete_monitor(...)