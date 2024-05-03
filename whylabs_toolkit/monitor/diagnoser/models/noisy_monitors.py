from typing import Optional, List

from pydantic import BaseModel
from whylabs_toolkit.monitor.models import Segment


class NoisyMonitorStats(BaseModel):
    monitor_id: Optional[str]
    analyzer_id: str
    metric: str
    column_count: int
    segment_count: int
    anomaly_count: int
    max_anomaly_per_column: int
    min_anomaly_per_column: int
    avg_anomaly_per_column: int
    action_count: int
    action_targets: List[str]


class FailedMonitorStats(BaseModel):
    monitor_id: Optional[str]
    analyzer_id: str
    metric: str
    failed_count: int
    max_failed_per_column: int
    min_failed_per_column: int
    avg_failed_per_column: int
    action_count: int
    action_targets: List[str]


class NoisySegmentStats(BaseModel):
    segment: Segment
    total_anomalies: int
    batch_count: int


class FailedSegmentStats(BaseModel):
    segment: Segment
    total_failed: int


class NoisyColumnStats(BaseModel):
    column: str
    total_anomalies: int
