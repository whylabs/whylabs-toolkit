# flake8: noqa
"""Console script for monitor_schema."""
from .analyzer import *
from .column_schema import *
from .commons import *
from .document import *
from .monitor import *
from .segments import *

# TODO add all algorithms


__all__ = [
    "DatasetMetric",
    "SimpleColumnMetric",
    "ComplexMetrics",
    "Metadata",
    # analyzer
    "Analyzer",
    # baseline
    "BaselineType",
    "ReferenceProfileId",
    "TimeRangeBaseline",
    "TimeRange",
    "TrailingWindowBaseline",
    "SingleBatchBaseline",
    # configs
    "DiffConfig",
    "DriftConfig",
    "ComparisonConfig",
    "ComparisonOperator",
    "ExperimentalConfig",
    "FixedThresholdsConfig",
    "ColumnListChangeConfig",
    "SeasonalConfig",
    "StddevConfig",
    # targets
    "DatasetMatrix",
    "ColumnMatrix",
    "Segment",
    "SegmentTag",
    "TargetLevel",
    # monitors
    "Monitor",
    "EveryAnomalyMode",
    "DigestMode",
    "AnomalyFilter",
    # scheduling
    "ImmediateSchedule",
    "CronSchedule",
    "FixedCadenceSchedule",
    "Cadence",
    # monitor actions
    # "RawWebhook",
    "SlackWebhook",
    "EmailRecipient",
    "GlobalAction",
    # big document
    "Document",
    # schema
    "EntitySchema",
    "ColumnSchema",
    "ColumnDataType",
    "ColumnDiscreteness",
    "WeightConfig",
    "SegmentWeightConfig",
    "Granularity",
    # enums
    "DiffMode",
    "ThresholdType",
    "AlgorithmType",
    "DatasetMetric",
    "SimpleColumnMetric",
    "ComplexMetrics",
]
