import pytz
from datetime import datetime
from abc import abstractmethod

from whylabs_client.exceptions import NotFoundException

from whylabs_toolkit.helpers.monitor_helpers import get_analyzers, get_monitor
from whylabs_toolkit.monitor.models import *
from whylabs_toolkit.monitor.models.analyzer.algorithms import *
from whylabs_toolkit.monitor.manager.credentials import MonitorCredentials


class MonitorBuilder:
    def __init__(self, monitor_id: str, dataset_id: Optional[str] = None) -> None:

        self.credentials = MonitorCredentials(
            monitor_id=monitor_id,
            dataset_id=dataset_id
        )

        self.monitor: Optional[Monitor] = self._check_if_monitor_exists()
        self.analyzer: Optional[Analyzer] = self._check_if_analyzer_exists()

        self._monitor_mode: Optional[Union[EveryAnomalyMode, DigestMode]] = None
        self._monitor_actions: Optional[List[Union[GlobalAction, SendEmail, SlackWebhook, RawWebhook]]] = None
        self._analyzer_schedule: Optional[FixedCadenceSchedule] = None
        self._target_matrix: Optional[Union[ColumnMatrix, DatasetMatrix]] = None
        self._analyzer_config: Optional[
            Union[
                DiffConfig,
                FixedThresholdsConfig,
                StddevConfig,
                DriftConfig,
                SeasonalConfig,
            ]
        ] = None
        self._target_columns: Optional[List[str]] = []
        self._exclude_columns: Optional[List[str]] = []
        self._prefill_properties()

    def _check_if_monitor_exists(self) -> Any:
        try:
            existing_monitor = get_monitor(
                org_id=self.credentials.org_id,
                dataset_id=self.credentials.dataset_id,
                monitor_id=self.credentials.monitor_id,
            )
            existing_monitor = Monitor.parse_obj(existing_monitor)
        except NotFoundException:
            existing_monitor = None
        return existing_monitor

    def _check_if_analyzer_exists(self) -> Any:
        try:
            existing_analyzers = get_analyzers(
                org_id=self.credentials.org_id,
                dataset_id=self.credentials.dataset_id,
                monitor_id=self.credentials.monitor_id,
            )
            existing_analyzer = Analyzer.parse_obj(existing_analyzers[0])  # enforcing 1:1 relationship

        except NotFoundException:
            existing_analyzer = None
        return existing_analyzer

    def _prefill_properties(self) -> None:
        if self.monitor:
            self._monitor_mode = self.monitor.mode
            self._monitor_actions = self.monitor.actions
        if self.analyzer:
            self._analyzer_schedule = self.analyzer.schedule
            self._target_matrix = self.analyzer.targetMatrix
            self._analyzer_config = self.analyzer.config

    @property
    def schedule(self) -> Optional[Union[CronSchedule, FixedCadenceSchedule]]:
        return self._analyzer_schedule

    @schedule.setter
    def schedule(self, schedule: FixedCadenceSchedule) -> None:
        self._analyzer_schedule = schedule

    @property
    def target_matrix(self) -> Optional[Union[ColumnMatrix, DatasetMatrix]]:
        return self._target_matrix

    @target_matrix.setter
    def target_matrix(self, target: Union[ColumnMatrix, DatasetMatrix]) -> None:
        self._target_matrix = target

    @property
    def config(
        self,
    ) -> Optional[Union[DiffConfig, FixedThresholdsConfig, StddevConfig, DriftConfig, SeasonalConfig,]]:
        return self._analyzer_config

    @config.setter
    def config(
        self,
        config: Union[
            DiffConfig,
            FixedThresholdsConfig,
            StddevConfig,
            DriftConfig,
            SeasonalConfig,
        ],
    ) -> None:
        self._analyzer_config = config

    @property
    def actions(self) -> Optional[List[Union[GlobalAction, SendEmail, SlackWebhook, RawWebhook]]]:
        return self._monitor_actions

    @actions.setter
    def actions(self, actions: List[Union[GlobalAction, SendEmail, SlackWebhook, RawWebhook]]) -> None:
        self._monitor_actions = actions

    @property
    def mode(self) -> Optional[Union[EveryAnomalyMode, DigestMode]]:
        return self._monitor_mode

    @mode.setter
    def mode(self, mode: Union[EveryAnomalyMode, DigestMode]) -> None:
        self._monitor_mode = mode

    @staticmethod
    def _validate_columns_input(columns: List[str]) -> bool:
        # TODO validate if columns exist, throw exception
        # also use entity schema helpers from whylabs_toolkit
        if type(columns) != list or not all(isinstance(column, str) for column in columns):
            raise ValueError("columns must be a List of strings")
        return True

    def set_target_columns(self, columns: List[str]) -> None:
        """
        Args:
            :columns: A list of the targeted columns to monitor against the reference profile.
            :type columns: List[str]
        """
        if self._validate_columns_input(columns=columns):
            self._target_columns = columns
            self._target_matrix = ColumnMatrix(include=self._target_columns, exclude=self._exclude_columns, segments=[])

    def exclude_target_columns(self, columns: List[str]) -> None:
        if self._validate_columns_input(columns=columns):
            self._exclude_columns = columns
            self._target_matrix = ColumnMatrix(include=self._target_columns, exclude=self._exclude_columns, segments=[])

    def set_fixed_dates_baseline(self, start_date: datetime, end_date: datetime) -> None:
        if not start_date.tzinfo:
            start_date = start_date.replace(tzinfo=pytz.UTC)
        if not end_date.tzinfo:
            end_date = end_date.replace(tzinfo=pytz.UTC)

        self._analyzer_config.baseline = TimeRangeBaseline(  # type: ignore
            range=TimeRange(start=start_date, end=end_date)
        )

    @abstractmethod
    def __set_analyzer(self) -> None:
        self.analyzer = Analyzer(
            id=self.credentials.analyzer_id,
            displayName=self.credentials.analyzer_id,
            targetMatrix=self._target_matrix,
            tags=[],
            schedule=self._analyzer_schedule,
            config=self._analyzer_config,
        )

    def __set_monitor(
        self, monitor_mode: Optional[Union[EveryAnomalyMode, DigestMode]], monitor_actions: Optional[List[Any]]
    ) -> None:

        self.monitor = Monitor(
            id=self.credentials.monitor_id,
            disabled=False,
            displayName=self.credentials.monitor_id,
            tags=[],
            analyzerIds=[self.credentials.analyzer_id],
            schedule=ImmediateSchedule(),
            mode=monitor_mode,
            actions=monitor_actions,
        )

    def build(self) -> None:
        monitor_mode = self._monitor_mode or DigestMode()
        actions = self._monitor_actions or []
        self._analyzer_schedule = self._analyzer_schedule or FixedCadenceSchedule(cadence=Cadence.daily)
        self._target_matrix = self._target_matrix or ColumnMatrix(include=["*"], exclude=[], segments=[])

        self.__set_monitor(monitor_mode=monitor_mode, monitor_actions=actions)
        self.__set_analyzer()


class MissingDataMonitorBuilder(MonitorBuilder):
    """
    Use this preset MonitorOptions to monitor change on missing Data compared to a threshold

    Args:
         :percentage: The percentage change that should trigger an alert.
         Value must be greater or equal to 0 and lesser or equal to 100.
         :type percentage: int
    """
    def __set_analyzer(self) -> None:
        pass


class FixedCountsMonitorBuilder(MonitorBuilder):
    def __set_analyzer(self) -> None:
        pass


class DynamicCountsMonitorBuilder(MonitorBuilder):
    def __set_analyzer(self) -> None:
        pass
