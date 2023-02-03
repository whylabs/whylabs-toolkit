from whylabs_toolkit.monitor.models.monitor import SendEmail, SlackWebhook

from .builder import MonitorBuilder


class MonitorManager:
    def __init__(self, monitor_id: str, monitor_builder: MonitorBuilder) -> None:
        self.monitor_id = monitor_id
        self.__builder = monitor_builder
        
    def build(self):
        self.__builder.add_analyzer()
        self.__builder.add_monitor()


if __name__ == "__main__":
    builder = MonitorBuilder()
    builder.add_actions(
        actions=[
            SendEmail(type="email", target="some_mail@example.com")
        ]
    )
    # builder.add_schedule(
    #     schedule = Cadence.daily
    # )


    print(builder.monitor)
    print(builder.analyzer)

    # manager = MonitorManager(
    #     monitor_id="my_awesome_monitor",
    #     monitor_builder=builder
    # )