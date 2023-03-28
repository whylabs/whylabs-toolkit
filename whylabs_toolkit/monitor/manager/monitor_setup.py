import pytz
import logging
from datetime import datetime
from typing import Optional, List, Union, Any

from whylabs_client.exceptions import NotFoundException

from whylabs_toolkit.helpers.utils import get_models_api
from whylabs_toolkit.monitor.models import *
from whylabs_toolkit.monitor.models.analyzer.targets import ColumnGroups
from whylabs_toolkit.monitor.manager.credentials import MonitorCredentials
from whylabs_toolkit.helpers.monitor_helpers import get_analyzers, get_monitor, get_model_granularity
from whylabs_toolkit.helpers.config import Config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitorSetup:
    def __init__(self, monitor_id: str, dataset_id: Optional[str] = None, config: Config = Config()) -> None:

        self.credentials = MonitorCredentials(monitor_id=monitor_id, dataset_id=dataset_id, config=config)
        self._config = config
        self.monitor: Optional[Monitor] = self._check_if_monitor_exists()
        self.analyzer: Optional[Analyzer] = self._check_if_analyzer_exists()

        self._models_api = get_models_api(config=self._config)

        self._monitor_mode: Optional[Union[EveryAnomalyMode, DigestMode]] = None
        self._monitor_actions: Optional[List[Union[GlobalAction, EmailRecipient, SlackWebhook]]] = None
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
                config=self._config,
            )
            existing_monitor = Monitor.parse_obj(existing_monitor)
            logger.info(f"Got existing {self.credentials.monitor_id} from WhyLabs!")
        except NotFoundException:
            logger.info(f"Did not find a monitor with {self.credentials.monitor_id}, creating a new one.")
            existing_monitor = None
        return existing_monitor

    def _check_if_analyzer_exists(self) -> Any:
        try:
            existing_analyzers = get_analyzers(
                org_id=self.credentials.org_id,
                dataset_id=self.credentials.dataset_id,
                monitor_id=self.credentials.monitor_id,
                config=self._config,
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
    def actions(self) -> Optional[List[Union[GlobalAction, EmailRecipient, SlackWebhook]]]:
        return self._monitor_actions

    @actions.setter
    def actions(self, actions: List[Union[GlobalAction, EmailRecipient, SlackWebhook]]) -> None:
        self._monitor_actions = actions

    @property
    def mode(self) -> Optional[Union[EveryAnomalyMode, DigestMode]]:
        return self._monitor_mode

    @mode.setter
    def mode(self, mode: Union[EveryAnomalyMode, DigestMode]) -> None:
        self._monitor_mode = mode

    def _validate_columns_input(self, columns: List[str]) -> bool:
        if type(columns) != list or not all(isinstance(column, str) for column in columns):
            raise ValueError("columns argument must be a List of strings")

        if "group:" in columns[0]:
            return True

        schema = self._models_api.get_entity_schema(
            org_id=self.credentials.org_id, dataset_id=self.credentials.dataset_id
        )
        columns_dict = schema["columns"]

        for col in columns:
            if col not in columns_dict.keys():
                raise ValueError(
                    f"{col} is not present on {self.credentials.dataset_id}. Available columns are: {columns_dict.keys()}"
                )

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
        # TODO make baseline nullable and default baseline to be TrailingWindowBaseline(size=14)
        self._analyzer_config.baseline = TimeRangeBaseline(  # type: ignore
            range=TimeRange(start=start_date, end=end_date)
        )

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

    def __configure_target_matrix(self) -> None:
        self._target_matrix = self._target_matrix or ColumnMatrix(
            include=self._target_columns or ["*"], exclude=self._exclude_columns, segments=[]
        )
        if self.analyzer:
            if isinstance(self.analyzer.config.metric, DatasetMetric):
                self._target_matrix = DatasetMatrix()

    def apply(self) -> None:
        monitor_mode = self._monitor_mode or DigestMode()
        actions = self._monitor_actions or []
        self._analyzer_schedule = self._analyzer_schedule or FixedCadenceSchedule(
            cadence=get_model_granularity(
                org_id=self.credentials.org_id, dataset_id=self.credentials.dataset_id  # type: ignore
            )
        )

        self.__set_monitor(monitor_mode=monitor_mode, monitor_actions=actions)

        self.__configure_target_matrix()
        self.__set_analyzer()
