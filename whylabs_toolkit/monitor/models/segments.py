"""Segment definitions."""
from typing import List

from pydantic import Field

from whylabs_toolkit.monitor.models.commons import NoExtrasBaseModel


class SegmentTag(NoExtrasBaseModel):
    """A single tag key value pair for a segment."""

    key: str = Field(max_length=1000)
    value: str = Field(max_length=1000)


class Segment(NoExtrasBaseModel):
    """A segment is a list of tags.

    We normalize these in the backend.
    """

    tags: List[SegmentTag] = Field(
        description="List of tags that define the specific segment",
        max_items=10,
    )
