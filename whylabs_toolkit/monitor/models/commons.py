"""Common schema definitions."""
from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Extra
from pydantic.fields import Field

CRON_REGEX = "(@(annually|yearly|monthly|weekly|daily|hourly))|" "((((\\d+,)+\\d+|(\\d+(\\/|-)\\d+)|\\d+|\\*) ?){5,7})"
DATASET_ID_REGEX = "[a-zA-Z0-9\\-_\\.]+"

DATASET_ID_DEF = Field(
    title="DatasetId",
    description="The unique ID of an dataset. This is specific to WhyLabs. If the dataset ID "
    "does not exist, user will get a validation exception when saving the "
    "config with WhyLabs API",
    regex=DATASET_ID_REGEX,
    max_length=100,
)


class NoExtrasBaseModel(BaseModel, extra=Extra.forbid):  # type: ignore
    """No extras base model.

    Inherit to prevent accidental extra fields.
    """


class ImmediateSchedule(NoExtrasBaseModel):
    """Schedule the monitor to run immediately."""

    type: Literal["immediate"] = "immediate"


class TimeRange(NoExtrasBaseModel):
    """Support for a specific time range."""

    start: datetime = Field(description="Inclusive. Start time of a time range.")
    end: datetime = Field(description="Exclusive. End time of a time range.")


class CronSchedule(NoExtrasBaseModel):
    """Support for scheduling."""

    type: Literal["cron"] = "cron"
    cron: str = Field(
        description="Cron expression",
        regex=CRON_REGEX,
    )
    exclusionRanges: Optional[List[TimeRange]] = Field(
        title="ExclusionRanges", description="The ranges of dates during which this Analyzer is NOT run."
    )
    # TODO: support other mode of configuring scheduling


class Cadence(str, Enum):
    """Cadence for an analyzer or monitor run."""

    hourly = "hourly"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class FixedCadenceSchedule(NoExtrasBaseModel):
    """Support for scheduling based on a predefined cadence."""

    type: Literal["fixed"] = "fixed"
    cadence: Literal[Cadence.hourly, Cadence.daily, Cadence.weekly, Cadence.monthly] = Field(
        description="Frequency to run the analyzer or monitor, based on UTC time. The monitor will run at the start of "
        "the cadence with some SLA depending on the customer tiers.",
    )
    exclusionRanges: Optional[List[TimeRange]] = Field(
        title="ExclusionRanges", description="Ranges of dates during which this Analyzer is NOT run."
    )


class Metadata(NoExtrasBaseModel):
    """Metadata for a top-level objects such as monitors, analyzers, and schema.

    This object is managed by WhyLabs. Any user-provided values will be ignored on WhyLabs side.
    """

    version: int = Field(description="A monotonically increasing numer that indicates the version of the object.")
    schemaVersion: Optional[int] = Field(
        None,
        description="The version of the schema. Currently the accepted value is 1.",
        le=1,
        ge=1,
    )
    updatedTimestamp: int = Field(
        description="Last updated timestamp",
        gt=0,
    )
    author: str = Field(
        description="The author of the change. It can be an API Key ID, a user ID, or a WhyLabs system ID.",
        max_length=100,
        regex="[0-9a-zA-Z-_.+]+",
    )
    description: Optional[str] = Field(
        None,
        description="A description of the object",
        max_length=1000,
    )
