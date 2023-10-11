"""Schema for analyses."""
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, constr

from whylabs_toolkit.monitor.models.commons import NoExtrasBaseModel

from ..commons import CronSchedule, FixedCadenceSchedule, Metadata
from ..utils import anyOf_to_oneOf, duration_field
from .algorithms import (
    ColumnListChangeConfig,
    ComparisonConfig,
    ListComparisonConfig,
    FrequentStringComparisonConfig,
    DiffConfig,
    DriftConfig,
    ExperimentalConfig,
    FixedThresholdsConfig,
    SeasonalConfig,
    StddevConfig,
    ConjunctionConfig,
    DisjunctionConfig,
)
from .targets import ColumnMatrix, DatasetMatrix


class Analyzer(NoExtrasBaseModel):
    """Configuration for running an analysis.

    An analysis targets a metric (note that a metric could be a complex object) for one or multiple fields in
    one or multiple segments. The output is a list of 'anomalies' that might show issues with data.
    """

    metadata: Optional[Metadata] = Field(
        None, description="WhyLabs-managed metadata. This is to track various metadata for auditing."
    )

    id: str = Field(
        None,
        description="A unique, human readable ID for an analyzer. "
        "Can only contain alpha numeric characters, underscores and dashes",
        min_length=10,
        max_length=128,
        regex="[0-9a-zA-Z\\-_]+",
    )
    displayName: Optional[str] = Field(
        None,
        id="DisplayName",
        description="A display name for the analyzer if view through WhyLabs UI. Can only contain dashes, underscores,"
        "spaces, and alphanumeric characters",
        min_length=10,
        max_length=256,
        regex="[0-9a-zA-Z \\-_]+",
    )
    tags: Optional[  # type: ignore
        List[constr(min_length=3, max_length=32, regex="[0-9a-zA-Z\\-_]")]  # noqa
    ] = Field(  # noqa F722
        None, description="A list of tags that are associated with the analyzer."
    )
    # disabling CronSchedule as it can be tricky on the BE
    schedule: Optional[FixedCadenceSchedule] = Field(  # Optional[Union[CronSchedule, FixedCadenceSchedule]] = Field(
        None,
        description="A schedule for running the analyzer. If not set, the analyzer's considered disabled",
    )
    disabled: Optional[bool] = Field(
        None,
        description="Whether the analyzer is disabled. "
        "This allows user to keep the configuration"
        "around without having to delete the analyzer config",
    )
    disableTargetRollup: Optional[bool] = Field(
        None,
        description="For customers with individual profile storage enabled on their account (contact us), this "
        "allows a user to monitor individual profiles without rolling them up. When enabled, analysis "
        "will be timestamped 1:1 with the profile's dataset timestamp rather than being truncated "
        "to the dataset granularity. ",
    )
    targetMatrix: Union[ColumnMatrix, DatasetMatrix] = Field(
        description="A matrix for possible locations of the target",
        discriminator="type",
    )
    dataReadinessDuration: Optional[str] = duration_field(
        title="DataReadinessDuration",
        description="ISO 8610 duration format. The duration determines how fast data is ready for the monitor. For "
        "example, if your pipeline takes 2 days to deliver profiles to WhyLabs, the value should be"
        "P2D. Note that this value will be used to evaluate missing data as well",
    )
    batchCoolDownPeriod: Optional[str] = duration_field(
        title="BatchCoolDownPeriod",
        description="ISO 8610 duration format. Specifies the duration that the monitor will wait from the last time"
        "a profile arrives Any batch involved in the calculation must have received the last profile by "
        "the duration.",
    )
    backfillGracePeriodDuration: Optional[str] = duration_field(
        title="BackfillGracePeriodDuration",
        description="ISO 8610 duration format. How far back an analyzer will attempt to backfill late data. Note that "
        "we will only backfill batches not previously analyzed. If the batch was already analyzed, "
        "even with partial data, the backfill will ignore the new data unless you trigger an explicit "
        "backfill request. We support 48 hours for hourly data, 30 days for daily data, and 6 months for "
        "monthly data.",
    )

    # NOT YET IMPLEMENTED:
    # ExperimentalConfig,
    # ColumnListChangeConfig,

    config: Union[
        DiffConfig,
        FixedThresholdsConfig,
        ListComparisonConfig,
        FrequentStringComparisonConfig,
        StddevConfig,
        DriftConfig,
        ComparisonConfig,
        SeasonalConfig,
        ConjunctionConfig,
        DisjunctionConfig,
    ] = Field(description="The configuration map of the analyzer", discriminator="type")

    class Config:
        """Updates JSON schema anyOf to oneOf."""

        # noinspection PyUnusedLocal
        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: BaseModel) -> None:
            """Update specific fields here (for Union type, specifically)."""
            anyOf_to_oneOf(schema, "config")
            anyOf_to_oneOf(schema, "targetMatrix")
