"""Collections of support algorithms."""
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, constr

from whylabs_toolkit.monitor.models.analyzer.baseline import (
    ReferenceProfileId,
    SingleBatchBaseline,
    TimeRangeBaseline,
    TrailingWindowBaseline,
)
from whylabs_toolkit.monitor.models.commons import NoExtrasBaseModel, TimeRange
from whylabs_toolkit.monitor.models.utils import COLUMN_NAME_TYPE, anyOf_to_oneOf


class AlgorithmType(str, Enum):
    """Specify the algorithm type."""

    expected = "expected"
    column_list = "column_list"
    comparison = "comparison"
    diff = "diff"
    drift = "drift"
    stddev = "stddev"
    seasonal = "seasonal"
    fixed = "fixed"
    experimental = "experimental"


class DatasetMetric(str, Enum):
    """Metrics that are applicable at the dataset level."""

    # ingestion health. null value if not ingested yet
    profile_count = "profile.count"
    profile_last_ingestion_time = "profile.last_ingestion_time"
    profile_first_ingestion_time = "profile.first_ingestion_time"

    # within the batch
    column_row_count_sum = "column_row_count_sum"
    # shape metrics?
    shape_column_count = "shape_column_count"
    shape_row_count = "shape_row_count"
    input_count = "input.count"
    output_count = "output.count"

    # classification metrics
    classification_f1 = "classification.f1"
    classification_precision = "classification.precision"
    classification_recall = "classification.recall"
    classification_accuracy = "classification.accuracy"
    classification_auc = "classification.auc"

    # regression metrics
    regression_mse = "regression.mse"
    regression_mae = "regression.mae"
    regression_rmse = "regression.rmse"


class SimpleColumnMetric(str, Enum):
    """Simple column metrics that are basically just a single number."""

    count = "count"  # type: ignore
    median = "median"
    max = "max"
    min = "min"
    mean = "mean"
    stddev = "stddev"
    variance = "variance"
    unique_upper = "unique_upper"
    unique_upper_ratio = "unique_upper_ratio"
    unique_est = "unique_est"
    unique_est_ratio = "unique_est_ratio"
    unique_lower = "unique_lower"
    unique_lower_ratio = "unique_lower_ratio"

    # data type counts and ratios
    count_bool = "count_bool"
    count_bool_ratio = "count_bool_ratio"
    count_integral = "count_integral"
    count_integral_ratio = "count_integral_ratio"
    count_fractional = "count_fractional"
    count_fractional_ratio = "count_fractional_ratio"
    count_string = "count_string"
    count_string_ratio = "count_string_ratio"

    # also missing values
    count_null = "count_null"
    count_null_ratio = "count_null_ratio"

    # this is a string metric
    inferred_data_type = "inferred_data_type"

    # quantiles
    quantile_p5 = "quantile_5"
    quantile_p75 = "quantile_75"
    quantile_p25 = "quantile_25"
    quantile_p90 = "quantile_90"
    quantile_p95 = "quantile_95"
    quantile_p99 = "quantile_99"


class ComplexMetrics(str, Enum):
    """Sketch-based metrics that can only be processed by certain algorithms."""

    histogram = "histogram"
    frequent_items = "frequent_items"
    unique_sketch = "unique_sketch"
    # list of columns
    column_list = "column_list"


class AlgorithmConfig(NoExtrasBaseModel):
    """Base algorithm config."""

    schemaVersion: Optional[int] = Field(
        None,
        description="The schema version of an algorithm. Typically this value" "is not required.",
        title="SchemaVersion",
    )
    params: Optional[Dict[constr(max_length=100), constr(max_length=1000)]] = Field(  # type: ignore
        None,
        description="Extra parameters for the algorithm",
    )
    metric: Union[DatasetMetric, SimpleColumnMetric, constr(max_length=100)] = Field(  # type: ignore
        description="The target metric. This field cannot be change once the analyzer is created.",
    )

    class Config:
        """Updates JSON schema anyOf to oneOf for baseline."""

        # noinspection PyUnusedLocal
        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: BaseModel) -> None:
            """Update specific fields here (for Union type, specifically)."""
            anyOf_to_oneOf(schema, "baseline")


class ExpectedValue(NoExtrasBaseModel):
    """Expected value: one of these fields must be set."""

    str: Optional[constr(max_length=100)]  # type: ignore
    int: Optional[int]
    float: Optional[float]


class ComparisonOperator(str, Enum):
    """Operators for performing a comparison."""

    eq = "eq"
    gt = "gt"
    lt = "lt"
    ge = "ge"
    le = "le"


class ComparisonConfig(AlgorithmConfig):
    """Compare whether the target against a value or against a baseline's metric.

    This is useful to detect data type change, for instance.
    """

    type: Literal[AlgorithmType.comparison] = AlgorithmType.comparison
    operator: ComparisonOperator = Field(
        description="The operator for the comparison. The right hand side is the target batch's metric. The left hand"
        "side is the expected value or a baseline's metric."
    )
    expected: Optional[ExpectedValue] = Field(
        None,
        description="The expected value of the equality. If the value is not set we will extract the corresponding "
        "metric from the baseline and perform the comparison",
    )
    baseline: Optional[Union[TrailingWindowBaseline, ReferenceProfileId, TimeRangeBaseline, SingleBatchBaseline]]


class ColumnListChangeConfig(AlgorithmConfig):
    """Compare whether the target is equal to a value or not.

    This is useful to detect data type change, for instance.
    """

    type: Literal[AlgorithmType.column_list] = AlgorithmType.column_list
    mode: Literal["ON_ADD_AND_REMOVE", "ON_ADD", "ON_REMOVE"] = "ON_ADD_AND_REMOVE"
    metric: Literal[ComplexMetrics.column_list]
    exclude: Optional[List[COLUMN_NAME_TYPE]] = Field(  # type: ignore
        None,
        description="Ignore these column names. User can specify a list of regex",
        max_items=1000,
    )

    baseline: Union[TrailingWindowBaseline, ReferenceProfileId, TimeRangeBaseline, SingleBatchBaseline]


class FixedThresholdsConfig(AlgorithmConfig):
    """Fixed threshold analysis.

    If user fails to set both upper bound and lower bound, this algorithm becomes a no-op.
    WhyLabs might enforce the present of either fields in the future.
    """

    type: Literal[AlgorithmType.fixed] = AlgorithmType.fixed
    upper: Optional[float] = Field(None, description="Upper bound of the static threshold")
    lower: Optional[float] = Field(None, description="Lower bound of the static threshold")


class _ThresholdBaseConfig(AlgorithmConfig):
    maxUpperThreshold: Optional[float] = Field(
        None,
        description="Capping the threshold by this value. This value only becomes effective if the calculated upper "
        "threshold from the calculation is greater than this value.",
    )

    minLowerThreshold: Optional[float] = Field(
        None,
        description="Capping the minimum threshold by this value. This value only becomes effective if the calculated "
        "lower threshold from the calculation is lesser than this value",
    )


class StddevConfig(_ThresholdBaseConfig):
    """Calculates upper bounds and lower bounds based on stddev from a series of numbers.

    An analyzer using stddev for a window of time range.

    This calculation will fall back to Poisson distribution if there is only 1 value in the baseline.
    For 2 values, we use the formula sqrt((x_i - avg(x))^2 / n - 1)
    """

    type: Optional[Literal[AlgorithmType.stddev]] = Field(AlgorithmType.stddev)
    factor: Optional[float] = Field(
        3.0, description="The multiplier used with stddev to build the upper and lower bounds."
    )
    minBatchSize: Optional[int] = Field(
        1, title="MinBatchSize", ge=1, description="Minimum number of batches that is required"
    )
    baseline: Union[TrailingWindowBaseline, TimeRangeBaseline, ReferenceProfileId]


class SeasonalConfig(_ThresholdBaseConfig):
    """An analyzer using stddev for a window of time range.

    This will fall back to Poisson distribution if there is only 1 value in the baseline.

    This only works with TrailingWindow baseline (TODO: add backend validation)
    """

    type: Literal[AlgorithmType.seasonal] = AlgorithmType.seasonal
    algorithm: Literal["arima", "rego", "stastforecast"] = Field(
        "arima", description="The algorithm implementation for seasonal analysis"
    )
    minBatchSize: Optional[int] = Field(
        30,
        title="MinBatchSize",
        description="Minimum number of batches that is required",
    )
    alpha: Optional[float] = Field(
        default=0.05,
        description="significance level for the confidence interval produced around predictions. If 0.05 then the "
        "algorithm will calculate a 95% confidence interval around predictions",
    )
    baseline: TrailingWindowBaseline
    stddevTimeRanges: Optional[List[TimeRange]] = Field(
        title="StddevTimeRanges",
        description="Ranges of time where we will apply standard deviation for confidence "
        "intervals rather than the confidence interval from the algorithm. This "
        "is to prevent data from special"
        "events from making the bands very wide for timeseries-based predictions.",
    )
    stddevMaxBatchSize: Optional[int] = Field(
        description="Maxinum number of data points to consider for calculating stddev. These are the data points"
        "preceeding the target batch."
    )
    stddevFactor: Optional[float] = Field(
        default=1.0,
        description="The multiplier factor for calculating upper bounds and lower bounds from the prediction.",
    )


class DriftConfig(AlgorithmConfig):
    """An analyzer using stddev for a window of time range.

    This analysis will detect whether the data drifts or not. By default, we use hellinger distance with a threshold
    of 0.7.
    """

    type: Literal[AlgorithmType.drift] = AlgorithmType.drift
    algorithm: Literal["hellinger", "ks_test", "kl_divergence", "variation_distance"] = Field(
        "hellinger", description="The algorithm to use when calculating drift."
    )
    metric: Literal[ComplexMetrics.histogram, ComplexMetrics.frequent_items]
    threshold: float = Field(
        0.7,
        description="The threshold for the distance algorithm. Depending on the algorithm, this threshold"
        "is used for greater than or less than comparison.",
    )
    minBatchSize: Optional[int] = Field(
        1,
        title="MinBatchSize",
        description="Minimum number of batches that is required",
        ge=1,
    )
    baseline: Union[TrailingWindowBaseline, ReferenceProfileId, TimeRangeBaseline, SingleBatchBaseline]


class ExperimentalConfig(AlgorithmConfig):
    """Experimental algorithm that is not standardized by the above ones yet."""

    type: Literal[AlgorithmType.experimental] = AlgorithmType.experimental
    implementation: str = Field(description="The implementation of an experimental config", max_length=100)
    baseline: Union[TrailingWindowBaseline, ReferenceProfileId, TimeRangeBaseline, SingleBatchBaseline]
    stub: Optional[AlgorithmType] = Field(description="Stub field to flow algoirthm type into the schema. Do not use.")


class DiffMode(str, Enum):
    """Whether to use the absolute difference or the percentage to calculate the difference."""

    abs = "abs"
    pct = "pct"


class ThresholdType(str, Enum):
    """By default, an anomaly will be generated when the target is above or below the baseline
    by the specified threshold.

    If its only desirable to alert when the target is above the
    baseline and not the other way around, specify upper for your ThresholdType."""

    lower = "lower"  # type: ignore
    upper = "upper"  # type: ignore


class DiffConfig(AlgorithmConfig):
    """Detecting the differences between two numerical metrics."""

    type: Literal[AlgorithmType.diff] = AlgorithmType.diff
    mode: DiffMode
    thresholdType: Optional[ThresholdType]
    threshold: float = Field(
        description="The minimum threshold that will trigger an anomaly. The monitor detect the difference between"
        "the target's metric and the baseline metric. Both of these metrics MUST be in rolled up form",
    )
    baseline: Union[TrailingWindowBaseline, ReferenceProfileId, TimeRangeBaseline, SingleBatchBaseline]
