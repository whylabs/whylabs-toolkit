from typing import Optional
from dataclasses import dataclass, field

from whylabs_toolkit.helpers.config import Config


@dataclass
class MonitorCredentials:
    monitor_id: str
    dataset_id: Optional[str] = field(default=None)  # type: ignore
    config: Config = field(default=Config())  # type: ignore

    def __post_init__(self) -> None:
        self.org_id = self.config.get_default_org_id()
        self.analyzer_id = f"{self.monitor_id}-analyzer"
        if not self.dataset_id:
            self.dataset_id = self.config.get_default_dataset_id()
