from typing import List, Union

from whylabs_toolkit.monitor.models import (
    Monitor,
    Analyzer,
    GlobalAction,
    SlackWebhook,
    SendEmail,
    RawWebhook
)

# TODO add default Monitor object
# TODO add default Analyzer object
# TODO add_target
# TODO add_config
# TODO add_severity
# TODO add_schedule
# TODO add_mode


class MonitorBuilder:
    def __init__(self) -> None:
        self.analyzer = None
        self.monitor = None

    def add_schedule(self):
        pass
    
    def add_target(self):
        pass
    
    def add_config(self):
        pass
    
    def add_severity(self):
        pass
    
    def add_mode(self):
        # digest or everyAnomaly
        # filter out anomalies
        pass
    
    def add_actions(self, actions: List[Union[GlobalAction, SendEmail, SlackWebhook, RawWebhook]]):
        allowed_actions = (GlobalAction, SendEmail, SlackWebhook, RawWebhook)
        for action in actions:
            if not isinstance(action, allowed_actions):
                raise ValueError(f"actions must be one of the supported types: {allowed_actions}!")
            self.monitor.actions.append(action)

    # def add_analyzer(self) -> None:
    #     self.analyzer: Analyzer = Analyzer()
    #     self.add_schedule()
    #     self.add_target()
    #     self.add_config()

    # def add_monitor(self) -> None:
    #     self.monitor: Monitor = Monitor()
    #     self.add_severity()
    #     self.add_actions()
    #     self.add_mode()
