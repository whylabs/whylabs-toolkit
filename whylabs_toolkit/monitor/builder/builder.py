from whylabs_client.exceptions import NotFoundException

from whylabs_toolkit.helpers.monitor_helpers import get_analyzers, get_monitor
from whylabs_toolkit.monitor.models import *

class MonitorBuilder:
    analyzer: Analyzer
    monitor: Monitor

    def __init__(self, org_id: str, dataset_id: str, monitor_id: str) -> None:
        self.org_id = org_id
        self.dataset_id = dataset_id
        self.monitor_id = monitor_id
        self.analyzer_id = f"{monitor_id}-analyzer"

    def add_analyzer(self) -> None:
        try:
            existing_analyzers = get_analyzers(
                org_id=self.org_id, dataset_id=self.dataset_id, monitor_id=self.monitor_id
            )
            existing_analyzer = Analyzer.parse_obj(existing_analyzers[0])

        except NotFoundException:
            existing_analyzer = None
            pass

        self.analyzer = existing_analyzer or Analyzer(
            id=self.analyzer_id,
            displayName=self.analyzer_id,
            targetMatrix=DatasetMatrix(
                type=TargetLevel.dataset,
                segments=[Segment(tags=[])],
            ),
            tags=[],
            schedule=FixedCadenceSchedule(type="fixed", cadence=Cadence.monthly),
            config=DriftConfig(
                type='drift',
                metric='histogram',
                algorithm='hellinger',
                threshold=0.7,
                baseline=TrailingWindowBaseline(type=BaselineType.TrailingWindow, size=14),
            ),
        )

    def add_monitor(self) -> None:
        # TODO make sure existing Monitor will return valid object
        try:
            existing_monitor = get_monitor(org_id=self.org_id, dataset_id=self.dataset_id, monitor_id=self.monitor_id)
            existing_monitor = Monitor.parse_obj(existing_monitor)
        except NotFoundException:
            existing_monitor = None
            pass

        self.monitor = existing_monitor or Monitor(
            id = self.monitor_id,
            disabled=False,
            displayName=self.monitor_id,
            tags=[],
            analyzerIds=[self.analyzer_id],
            schedule=ImmediateSchedule(type="immediate"),
            mode=DigestMode(type="DIGEST"),
            actions=[]
        )


class FixedThresholdMonitorBuilder(MonitorBuilder):
    def __init__(self, org_id, dataset_id, monitor_id):
        super().__init__(org_id=org_id, dataset_id=dataset_id, monitor_id=monitor_id)

    def add_monitor(self) -> None:
        pass

    def add_analyzer(self) -> None:
        pass