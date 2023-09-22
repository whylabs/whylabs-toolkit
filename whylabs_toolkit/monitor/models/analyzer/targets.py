"""Define what targets for the analyses."""
from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import Field

from whylabs_toolkit.monitor.models.commons import NoExtrasBaseModel
from whylabs_toolkit.monitor.models.segments import Segment
from whylabs_toolkit.monitor.models.utils import COLUMN_NAME_TYPE


class TargetLevel(str, Enum):
    """Which nested level we are targeting."""

    dataset = "dataset"
    column = "column"


class _BaseMatrix(NoExtrasBaseModel):
    segments: Optional[List[Segment]] = Field(
        None,
        description="List of targeted segments. If not set, default to the overall segment",
        max_items=1000,
    )


class DatasetMatrix(_BaseMatrix):
    """Define the matrix of fields and segments to fan out for monitoring.

    .
    """

    type: Literal[TargetLevel.dataset] = Field(
        TargetLevel.dataset,
        description="Must be 'dataset' level",
    )


class ColumnGroups(str, Enum):
    """Standard column groupings."""

    group_continuous = "group:continuous"
    group_discrete = "group:discrete"

    # based on classification
    group_input = "group:input"
    group_output = "group:output"

    # based on data types
    group_bool = "group:bool"
    group_int = "group:int"
    group_frac = "group:frac"
    group_str = "group:str"


class ColumnMatrix(_BaseMatrix):
    """Define the matrix of columns and segments to fan out for monitoring."""

    type: Literal[TargetLevel.column] = TargetLevel.column
    include: Optional[List[Union[ColumnGroups, COLUMN_NAME_TYPE]]] = Field(  # type: ignore
        None,
        description="List of allowed fields/features/columns. Could be a grouping as well.",
        max_items=1000,
    )
    exclude: Optional[List[Union[ColumnGroups, COLUMN_NAME_TYPE]]] = Field(  # type: ignore
        None,
        description="List of blocked fields/features/columns. Could be a grouping as well. This setting is "
        "evaluated AFTER the 'include' field and thus should be used with caution.",
        max_items=1000,
    )
    profileId: Optional[str] = Field(
        default=None,
        description="The unique profile ID for the reference profile",
        max_length=100,
    )
