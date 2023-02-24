from dataclasses import dataclass, field

from whylabs_toolkit.helpers.config import Config


# TODO get Whylabs API Key *after* instantiating the builder, and not when importing MonitorCredentials

@dataclass
class MonitorCredentials:
    monitor_id: str
    dataset_id: str = field(default=None)  # type: ignore

    def __post_init__(self) -> None:
        self.org_id = Config().get_default_org_id()
        self.analyzer_id = f"{self.monitor_id}-analyzer"
        if not self.dataset_id:
            self.dataset_id = Config().get_default_dataset_id()
