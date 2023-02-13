from abc import ABC
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class Metrics(Enum):
    COUNTS = "counts"


class MonitorConfig(ABC):
    pass


@dataclass
class FixedThresholdConfig(MonitorConfig):
    threshold: int
    direction: str  # should be "upper", "lower" or None (both directions)
    metric: Metrics
    start_date: datetime = field(default=None)  # type: ignore
    end_date: datetime = field(default=None)  # type: ignore


@dataclass
class MovingAverageDiff(MonitorConfig):
    window_size: int  # in days
