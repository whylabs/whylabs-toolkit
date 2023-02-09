from typing import List, Optional

from whylabs_client.exceptions import NotFoundException

from whylabs_toolkit.helpers.monitor_helpers import get_analyzers, get_monitor
from whylabs_toolkit.monitor.models import *
from whylabs_toolkit.monitor.models.analyzer.algorithms import *

class MonitorBuilder:
    analyzer: Analyzer
    monitor: Monitor

    def __init__(self, org_id: str, dataset_id: str, monitor_id: str) -> None:
        self.org_id = org_id
        self.dataset_id = dataset_id
        self.monitor_id = monitor_id
        self.analyzer_id = f"{monitor_id}-analyzer"

    def _check_if_monitor_exists(self) -> Optional[Monitor]:
        try:
            existing_monitor = get_monitor(org_id=self.org_id, dataset_id=self.dataset_id, monitor_id=self.monitor_id)
            existing_monitor = Monitor.parse_obj(existing_monitor)
        except NotFoundException:
            existing_monitor = None
        return existing_monitor

    def _check_if_analyzer_exists(self) -> Optional[Analyzer]:
        try:
            existing_analyzers = get_analyzers(
                org_id=self.org_id, dataset_id=self.dataset_id, monitor_id=self.monitor_id
            )
            existing_analyzer = Analyzer.parse_obj(existing_analyzers[0])

        except NotFoundException:
            existing_analyzer = None
        return existing_analyzer

    def add_analyzer(self) -> None:
        existing_analyzer = self._check_if_analyzer_exists()

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
        existing_monitor = self._check_if_monitor_exists()

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


class MissingDataMonitorBuilder(MonitorBuilder):
    """
    Use this preset MonitorBuilder to monitor Percentage change on missing Data compared to a fixed threshold

    Args:
         :columns: A list of the targeted columns to monitor against the reference profile. Defaults to None
         :type columns: List[str], Optional

         :percentage: The percentage change that should trigger an alert.
         Value must be greater or equal to 0 and lesser or equal to 100.
         :type percentage: int
    """
    def __init__(self, org_id: str, dataset_id: str, monitor_id: str, percentage: int, columns: Optional[List[str]] = None):
        super().__init__(org_id=org_id, dataset_id=dataset_id, monitor_id=monitor_id)
        self.percentage = percentage
        self.columns = columns
        self.__validate_input()

    def __validate_input(self):
        if type(self.percentage) != int:
            raise ValueError("percentage must be an int")
        if self.percentage >= 100 or self.percentage < 0:
            raise ValueError("percentage must be between 0 and 100")
        if self.columns:
            if type(self.columns) != list or not all(isinstance(column, str) for column in self.columns):
                raise ValueError("columns must be a List of strings")

    def add_monitor(self) -> None:
        existing_monitor = self._check_if_monitor_exists()

        self.monitor = existing_monitor or Monitor(
            id = self.monitor_id,
            disabled=False,
            displayName=self.monitor_id,
            analyzerIds=[self.analyzer_id],
            schedule=ImmediateSchedule(type="immediate"),
            mode=DigestMode(type="DIGEST"),
            actions=[]
        )

    def add_analyzer(self) -> None:
        existing_analyzer = self._check_if_analyzer_exists()

        self.analyzer = existing_analyzer or Analyzer(
            id=self.analyzer_id,
            displayName=self.analyzer_id,
            targetMatrix=
            ColumnMatrix(
                include=self.columns
            ) if self.columns else
            ColumnMatrix(
                type=TargetLevel.column,
                include=["*"],
            ),
            tags=[],
            schedule=FixedCadenceSchedule(type="fixed", cadence=Cadence.daily),
            config=DiffConfig(
                type=AlgorithmType.diff,
                mode=DiffMode.pct,
                metric=SimpleColumnMetric.count_null_ratio,
                threshold=self.percentage,
                baseline=TrailingWindowBaseline(type=BaselineType.TrailingWindow, size=14)
            ),
        )

class FixedCountsMonitorBuilder(MonitorBuilder):
    pass

class DynamicCountsMonitorBuilder(MonitorBuilder):
    def __init__(self, org_id: str, dataset_id: str, monitor_id: str, percentage: int, trailing_window_size: int):
        super().__init__(org_id=org_id, dataset_id=dataset_id, monitor_id=monitor_id)

    def __validate_input(self):
        # 100 <= percentage >= 0
        # upper_lower
        pass

    def __get_proper_config(self):
        pass
    def add_monitor(self) -> None:
        pass

    def add_analyzer(self) -> None:
        pass