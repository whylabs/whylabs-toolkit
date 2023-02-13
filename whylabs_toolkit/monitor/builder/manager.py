from whylabs_toolkit.monitor.builder.builder import MonitorBuilder
from whylabs_toolkit.monitor.models import *
from whylabs_toolkit.monitor.models.analyzer.algorithms import *
from whylabs_toolkit.helpers.utils import get_models_api


class MonitorManager:
    def __init__(self, monitor_builder: MonitorBuilder) -> None:
        self.monitor_id = monitor_builder.monitor_id
        self.__builder = monitor_builder
        self.__builder.add_analyzer()
        self.__builder.add_monitor()

    def add_schedule(
        self, schedule: FixedCadenceSchedule
    ) -> None:  # in the future -> Union[CronSchedule, FixedCadenceSchedule]):
        monitor_schedule = ImmediateSchedule(type="immediate")
        analyzer_schedule = schedule
        self.__builder.monitor.schedule = monitor_schedule
        self.__builder.analyzer.schedule = analyzer_schedule

    def add_target(self, target: Union[ColumnMatrix, DatasetMatrix]) -> None:
        self.__builder.analyzer.targetMatrix = target

    def add_config(
        self,
        config: Union[
            DiffConfig,
            ComparisonConfig,
            ColumnListChangeConfig,
            FixedThresholdsConfig,
            StddevConfig,
            DriftConfig,
            SeasonalConfig,
        ],
    ) -> None:
        self.__builder.analyzer.config = config

    def add_severity(self, severity: int) -> None:
        self.__builder.monitor.severity = severity

    def add_mode(self, mode: Union[EveryAnomalyMode, DigestMode]) -> None:
        self.__builder.monitor.mode = mode

    def add_actions(self, actions: List[Union[GlobalAction, SendEmail, SlackWebhook, RawWebhook]]) -> None:
        for action in actions:
            self.__builder.monitor.actions.append(action)

    def get_model_granularity(self) -> Optional[Granularity]:
        api = get_models_api()
        model_meta = api.get_model(org_id=self.__builder.org_id, model_id=self.__builder.dataset_id)

        time_period_to_gran = {
            "H": Granularity.hourly,
            "D": Granularity.daily,
            "W": Granularity.weekly,
            "M": Granularity.monthly,
        }

        for key, value in time_period_to_gran.items():
            if key in model_meta["time_period"].value:
                return value
        return None

    def dump(self) -> Any:
        doc = Document(
            orgId=self.__builder.org_id,
            datasetId=self.__builder.dataset_id,
            granularity=self.get_model_granularity(),
            analyzers=[self.__builder.analyzer],
            monitors=[self.__builder.monitor],
        )
        return doc.json(indent=2, exclude_none=True)

    def validate(self) -> None:
        Monitor.validate(self.__builder.monitor)
        Analyzer.validate(self.__builder.analyzer)

    def save(self) -> None:
        self.validate()
        api = get_models_api()
        api.put_analyzer(
            org_id=self.__builder.org_id,
            dataset_id=self.__builder.dataset_id,
            analyzer_id=self.__builder.analyzer_id,
            body=self.__builder.analyzer.dict(exclude_none=True),  # type: ignore
        )
        api.put_monitor(
            org_id=self.__builder.org_id,
            dataset_id=self.__builder.dataset_id,
            monitor_id=self.__builder.monitor_id,
            body=self.__builder.monitor.dict(exclude_none=True),  # type: ignore
        )
