"""Schema for configuring a monitor."""
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, HttpUrl, constr

from whylabs_toolkit.monitor.models.commons import (
    CronSchedule,
    FixedCadenceSchedule,
    ImmediateSchedule,
    Metadata,
    NoExtrasBaseModel,
)
from whylabs_toolkit.monitor.models.utils import COLUMN_NAME_TYPE, METRIC_NAME_STR, anyOf_to_oneOf


class MonitorConfigMetadata(NoExtrasBaseModel):
    """Metadata related to a monitor."""

    revision: int = Field(title="Revision number")
    update_timestamp: int = Field(title="Last update timestamp of this config")
    update_author: str = Field(title="The entity that updated this config", max_length=1000)


class GlobalAction(NoExtrasBaseModel):
    """Actions that are configured at the team/organization level."""

    type: Literal["global"] = "global"
    target: str = Field(description="The unique action ID in the platform", regex="[a-zA-Z0-9\\-_]+", max_length=100)


class SendEmail(NoExtrasBaseModel):
    """Action to send an email."""

    type: Literal["email"] = "email"
    target: str = Field(description="Destination email", format="email", max_length=1000)


class SlackWebhook(NoExtrasBaseModel):
    """Action to send a Slack webhook."""

    type: Literal["slack"] = "slack"
    target: HttpUrl = Field(description="The Slack webhook")


class RawWebhook(NoExtrasBaseModel):
    """Action to send a Slack webhook."""

    type: Literal["raw"] = "raw"
    target: HttpUrl = Field(description="Sending raw unformatted message in JSON format to a webhook")


class AnomalyFilter(NoExtrasBaseModel):
    """Filter the anomalies based on certain criteria. If the alerts are filtered down to 0, the monitor won't fire."""

    includeColumns: Optional[List[COLUMN_NAME_TYPE]] = Field(  # type: ignore
        None,
        title="IncludeColumns",
        description="If set, we only include anomalies from these columns",
        max_items=1000,
    )
    excludeColumns: Optional[List[COLUMN_NAME_TYPE]] = Field(  # type: ignore
        None,
        title="ExcludeColumns",
        description="If set, we will exclude anomalies from these columns. This is applied AFTER the includeColumns",
        max_items=1000,
    )
    minWeight: Optional[float] = Field(
        None,
        title="MinWeight",
        description="We will include only features with weights greater "
        "than or equal to this value. NOT SUPPORTED YET",
    )
    maxWeight: Optional[float] = Field(
        None,
        title="MaxWeight",
        description="We will include only features with weights less than" "or equal to this value. NOT SUPPORTED YET",
    )
    minRankByWeight: Optional[int] = Field(
        None,
        title="MinRankByWeight",
        description="Include only features ranked greater than or equal to"
        "this value by weight. If features have the same weight"
        ", we order them alphabetically. NOT SUPPORTED YET",
    )
    maxRankByWeight: Optional[int] = Field(
        None,
        title="MaxRankByWeight",
        description="Include only features ranked less than or equal to"
        "this value by weight. If features have the same "
        "weight, we order them alphabetically. NOT "
        "SUPPORTED YET",
    )
    minTotalWeight: Optional[float] = Field(
        None,
        title="MinTotalWeight",
        description="Only fire the monitor if the total weights of the"
        " alerts (based on feature weights) is greater than or "
        "equal to this value. NOT SUPPORTED YET",
    )
    maxTotalWeight: Optional[float] = Field(
        None,
        title="MaxTotalWeight",
        description="Only fire the monitor if the total weights of the"
        " alerts (based on feature weights) is less than or "
        "equal to this value. NOT SUPPORTED YET",
    )
    minAlertCount: Optional[int] = Field(
        None,
        title="MinAlertCount",
        description="If the total alert count is less than this value, the " "monitor won't fire. NOT SUPPORTED YET",
    )
    maxAlertCount: Optional[int] = Field(
        None,
        title="MaxAlertCount",
        description="If the total alert count is greater than this value, " "the monitor won't fire. NOT SUPPORTED YET",
    )
    includeMetrics: Optional[List[METRIC_NAME_STR]] = Field(  # type: ignore
        None,
        title="IncludeMetrics",
        description="Metrics to filter by. NOT SUPPORTED YET",
        max_items=100,
    )


excludeMetrics: Optional[List[METRIC_NAME_STR]] = Field(  # type: ignore
    None,
    title="ExcludeMetrics",
    description="Metrics to filter by. NOT SUPPORTED YET",
    max_items=100,
)


class EveryAnomalyMode(NoExtrasBaseModel):
    """Config mode that indicates the monitor will send out individual messages per anomaly."""

    type: Literal["EVERY_ANOMALY"] = "EVERY_ANOMALY"
    filter: Optional[AnomalyFilter] = Field(None, description="Filter for anomalies")


class DigestModeGrouping(str, Enum):
    """Enable the ability to group digest by various fields."""

    byField = "byColumn"
    byDataset = "byDataset"
    byAnalyzer = "byAnalyzer"
    byDay = "byDay"
    byHour = "byHour"


class DigestMode(NoExtrasBaseModel):
    """Config mode that indicates the monitor will send out a digest message."""

    type: Literal["DIGEST"] = Field("DIGEST")
    filter: Optional[AnomalyFilter] = Field(None, description="Filter for anomalies")
    creationTimeOffset: Optional[str] = Field(
        None,
        # format='duration', # TODO: is not supported by draft-7, only in draft 2019
        title="CreationTimeOffset",
        description="Optional for Immediate digest, required for Scheduled digest. The earliest creation timestamp"
        " that we will "
        "filter by to build the digest. ISO 8601 "
        "format for timedelta.",
        max_length=20,
    )
    datasetTimestampOffset: Optional[str] = Field(
        None,
        # format='duration',
        title="DatasetTimestampOffset",
        description="Optional for Immediate digest, required for Scheduled digest. "
        "The earliest dataset timestamp that we will filter by in the digest",
        max_length=20,
    )
    groupBy: Optional[List[DigestModeGrouping]] = Field(
        None,
        description="Default is None.If this is set, we will group alerts by these groupings and emit multiple messages"
        " per group.",
        max_items=10,
    )


class Monitor(NoExtrasBaseModel):
    """Customer specified monitor configs."""

    metadata: Optional[Metadata] = Field(None, description="Meta. This is to track various metadata for auditing.")
    id: str = Field(
        None,
        description="A human-readable alias for a monitor. Must be readable",
        min_length=10,
        max_length=128,
        regex="[0-9a-zA-Z\\-_]+",
    )
    displayName: Optional[str] = Field(
        None,
        id="DisplayName",
        description="A display name for the monitor if view through WhyLabs UI. Can only contain dashes, underscores,"
        "spaces, and alphanumeric characters",
        min_length=10,
        max_length=256,
        regex="[0-9a-zA-Z \\-_]+",
    )
    tags: Optional[  # type: ignore
        List[constr(min_length=3, max_length=32, regex="[0-9a-zA-Z\\-_]")]  # noqa F722
    ] = Field(None, description="A list of tags that are associated with the monitor.")
    analyzerIds: List[constr(regex="^[A-Za-z0-9_\\-]+$")] = Field(  # type: ignore # noqa: F722
        title="AnalyzerIds",
        description="The corresponding analyzer ID. Even though it's plural, we only support one analyzer at the "
        "moment",
        max_items=100,
    )
    schedule: Union[FixedCadenceSchedule, CronSchedule, ImmediateSchedule] = Field(
        description="Schedule of the monitor. We only support hourly monitor at " "the finest granularity",
    )
    disabled: Optional[bool] = Field(None, description="Whether the monitor is enabled or not")
    severity: Optional[int] = Field(3, description="The severity of the monitor messages")
    mode: Union[EveryAnomalyMode, DigestMode] = Field(
        description="Notification mode and how we might handle different analysis",
        discriminator="type",
    )
    actions: List[Union[GlobalAction, SendEmail, SlackWebhook, RawWebhook]] = Field(
        description="List of destination for the outgoing messages",
        max_items=100,
    )

    class Config:
        """Updates JSON schema anyOf to oneOf."""

        # noinspection PyUnusedLocal
        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: BaseModel) -> None:
            """Update specific fields here (for Union type, specifically)."""
            anyOf_to_oneOf(schema, "mode")
            anyOf_to_oneOf(schema, "schedule")
