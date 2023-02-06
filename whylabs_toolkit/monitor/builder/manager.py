import os
from typing import List, Union, Dict

from whylabs_toolkit.monitor.builder.builder import MonitorBuilder
from whylabs_toolkit.monitor.models import *
from whylabs_toolkit.helpers.utils import get_models_api


class MonitorManager:
    def __init__(self, monitor_builder: MonitorBuilder) -> None:
        self.monitor_id = monitor_builder.monitor_id
        self.__builder = monitor_builder
        self.__builder.add_analyzer()
        self.__builder.add_monitor()

    def add_schedule(self, schedule: Union[CronSchedule, FixedCadenceSchedule]):
        monitor_schedule = ImmediateSchedule(type="immediate")
        analyzer_schedule = schedule
        self.__builder.monitor.schedule = monitor_schedule
        self.__builder.analyzer.schedule = analyzer_schedule

    def add_target(self, target: Union[ColumnMatrix, DatasetMatrix]):
        self.__builder.analyzer.targetMatrix = target

    def add_config(self, config: Union[
        DiffConfig,
        ComparisonConfig,
        ColumnListChangeConfig,
        FixedThresholdsConfig,
        StddevConfig,
        DriftConfig,
        ExperimentalConfig,
        SeasonalConfig,
    ]):
        self.__builder.analyzer.config = config

    def add_severity(self, severity: int):
        self.__builder.monitor.severity = severity

    def add_mode(self, mode: Union[EveryAnomalyMode, DigestMode]):
        self.__builder.monitor.mode = mode

    def add_actions(self, actions: List[Union[GlobalAction, SendEmail, SlackWebhook, RawWebhook]]):
        for action in actions:
            self.__builder.monitor.actions.append(action)


    def dump(self) -> Dict:
        # TODO build Document object with Metadata, Monitor and Analyzer
        pass

    def validate(self):
        Monitor.validate(self.__builder.monitor)
        Analyzer.validate(self.__builder.analyzer)

    def save(self):
        self.validate()
        api = get_models_api()
        api.put_analyzer(
            org_id=self.__builder.org_id,
            dataset_id=self.__builder.dataset_id,
            analyzer_id=self.__builder.analyzer_id,
            body=self.__builder.analyzer.dict() # type: ignore
        )
        api.put_monitor(
            org_id=self.__builder.org_id,
            dataset_id=self.__builder.dataset_id,
            monitor_id=self.__builder.monitor_id,
            body=self.__builder.monitor.dict().update({"mode": {"type": "DIGEST"}}) # type: ignore
        )


if __name__ == "__main__":
    builder = MonitorBuilder(
        org_id=os.environ["ORG_ID"],
        dataset_id=os.environ["DATASET_ID"],
        monitor_id="my-awesome-monitor"
    )

    manager = MonitorManager(
        monitor_builder=builder
    )

    manager.add_actions(
        actions=[
            SendEmail(type="email", target="some_mail@example.com")
        ]
    )
    manager.save()