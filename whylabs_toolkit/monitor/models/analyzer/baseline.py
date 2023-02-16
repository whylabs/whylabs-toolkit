"""Define various baselines."""
from enum import Enum
from typing import List, Literal, Optional

from pydantic import Field

from whylabs_toolkit.monitor.models.commons import DATASET_ID_DEF, NoExtrasBaseModel, TimeRange


class BaselineType(str, Enum):
    """Supported baseline types."""

    BatchTimestamp = "BatchTimestamp"
    Reference = "Reference"
    TrailingWindow = "TrailingWindow"
    TimeRange = "TimeRange"
    CurrentBatch = "CurrentBatch"


class _Baseline(NoExtrasBaseModel):
    """Base class for a baseline."""

    datasetId: Optional[str] = DATASET_ID_DEF


class _SegmentBaseline(_Baseline):
    inheritSegment: Optional[bool] = Field(
        None,
        title="InheritSegment",
        description="Default to false. Whether to use the segment from the target to filter down the baseline",
    )


class ReferenceProfileId(_Baseline):
    """A baseline based on a static reference profile.

    A typical use case is to use a "gold" dataset and upload its profile to WhyLabs. This can be a training dataset
    as well for an ML model.
    """

    type: Literal[BaselineType.Reference] = BaselineType.Reference
    profileId: str = Field(
        title="ProfileId",
        description="The unique profile ID for the reference profile",
        max_length=100,
    )


class TrailingWindowBaseline(_SegmentBaseline):
    """A dynamic trailing window.

    This is useful if you don't have a static baseline to monitor against. This is the default mode for most
    monitors.
    """

    type: Optional[Literal[BaselineType.TrailingWindow]] = Field(BaselineType.TrailingWindow)
    size: int = Field(description="Window size", le=90, gt=3)
    offset: Optional[int] = Field(
        None,
        description="Offset from the current batch for the range of the trailing window. Default to 1 (the previous "
        "batch). This means that if set this to 0, the baseline will include the current batch's value, or"
        "if we set it o 7, then the window is off by 7.",
    )
    exclusionRanges: Optional[List[TimeRange]] = Field(
        None,
        title="ExclusionRanges",
        description="The list of exclusion ranges",
        max_items=100,
    )


class TimeRangeBaseline(_SegmentBaseline):
    """A static time range.

    Instead of using a single profile or a trailing window, user can lock in a "good" period.
    """

    type: Literal[BaselineType.TimeRange] = BaselineType.TimeRange
    range: TimeRange = Field(description="The range to set the time range with")


class SingleBatchBaseline(_SegmentBaseline):
    """Using current batch.

    This is used when you want to use one batch to monitor another batch in a different metric entity.
    """

    type: Literal[BaselineType.CurrentBatch] = BaselineType.CurrentBatch
    offset: Optional[int] = Field(
        None,
        description="Offset from the current batch for the baseline. Default to 0 - (the current batch). This means "
        "that if this field set this to 0, the baseline be the current batch's value. The dataset field"
        "is required to be set for this baseline config."
        "Typical use case is to use another entity to monitor against the current entity",
    )
    datasetId: str = DATASET_ID_DEF
