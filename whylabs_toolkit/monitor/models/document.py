"""The overall document for monitor."""
import uuid
from enum import Enum
from typing import List, Literal, Optional

from pydantic import Field

from whylabs_toolkit.monitor.models.commons import NoExtrasBaseModel

from .analyzer import Analyzer
from .column_schema import EntitySchema, EntityWeights
from .commons import DATASET_ID_DEF, Metadata
from .monitor import Monitor


class Granularity(str, Enum):
    """Supported granularity."""

    hourly = "hourly"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class Document(NoExtrasBaseModel):
    """The main document that dictates how the monitor should be run. This document is managed by WhyLabs internally."""

    id: Optional[uuid.UUID] = Field(None, description="A unique ID for the document")
    schemaVersion: Literal[1] = Field(
        description="The schema version of the document",
        title="SchemaVersion",
        default=1,
    )
    metadata: Optional[Metadata] = Field(
        None, description="WhyLabs-managed metadata. This is to track various metadata for auditing."
    )
    orgId: str = Field(title="OrgId", description="Organization ID for the document", max_length=100)
    datasetId: str = DATASET_ID_DEF
    granularity: Granularity = Field(description="Granularity of the entity")
    allowPartialTargetBatches: Optional[bool] = Field(
        None,
        title="AllowPartialTargetBatches",
        description="""The standard 
        flow waits for a target batch as defined by the dataset granularity 
        setting to conclude before running analysis. For example, on monthly datasets datapoints in the 
        current month would be analyzed at midnight on the last day of the month anticipating additional 
        data may be profiled. With allowPartialTargetBatches enabled a target batch may be analyzed as 
        soon as the data is present and dataReadinessDuration/batchCooldownPeriod (if configured) 
        conditions have been met. This can be ideal for data pipelines that upload a single profile per 
        dataset granularity to reduce the waiting time for analysis.""",
    )
    entitySchema: Optional[EntitySchema] = Field(description="Schema configuration for the entity")
    weightConfig: Optional[EntityWeights] = Field(None, description="Weight configuration for the entity")
    analyzers: List[Analyzer] = Field(description="List of analyzers", max_items=1000)
    monitors: List[Monitor] = Field(description="List of monitors", max_items=1000)
