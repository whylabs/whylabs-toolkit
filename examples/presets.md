# WhyLabs Monitors Presets

In this section we will present some existing presets available on the WhyLabs platform, using `whylabs-toolkit`.

The configuration workflow will always be: 

1. Create a `MonitorSetup` object
```python
monitor_setup = MonitorSetup(monitor_id=...)
```
2. Add a config
```python
monitor_setup.config = DriftConfig(...)
```
3. Save it to WhyLabs with `MonitorManager`
```python
manager = MonitorManager(monitor_setup)
manager.save()
```

And for this reason, this document will focus only on step 2, as steps 1 and 3 can be found with more detailed 
explanation and examples on the [Manager Docs](../whylabs_toolkit/monitor/manager/README.md).

## Drift

### Discrete inputs
```python
from whylabs_toolkit.monitor import MonitorSetup
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="drift_with_discrete_inputs")

monitor_setup.config = DriftConfig(
    metric = ComplexMetrics.frequent_items,
    baseline = TrailingWindowBaseline(size=7),
)

monitor_setup.set_target_columns(columns=["group:discrete"])
monitor_setup.exclude_target_columns(columns=["group:output"])
```

### Continuous inputs
```python
from whylabs_toolkit.monitor import MonitorSetup
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="drift_with_continuous_inputs")

monitor_setup.config = DriftConfig(
    metric = ComplexMetrics.histogram,
    baseline = TrailingWindowBaseline(size=7),
)

monitor_setup.set_target_columns(columns=["group:continuous"])
monitor_setup.exclude_target_columns(columns=["group:output"])
```

## Data Quality

### Missing values
```python
from whylabs_toolkit.monitor import MonitorSetup
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="missing_value_ratio_monitor")

monitor_setup.config = StddevConfig(
    metric = SimpleColumnMetric.count_null_ratio,
    baseline = TrailingWindowBaseline(size=7),
)
```

### Unique values: duplicate changes
```python
from whylabs_toolkit.monitor import MonitorSetup
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="unique_values_estimation")

monitor_setup.config = StddevConfig(
    metric = SimpleColumnMetric.unique_est,
    baseline = TrailingWindowBaseline(size=7),
)
```

### Data Type: detect mixed schema
```python
from whylabs_toolkit.monitor import MonitorSetup
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="monitor_data_type_changes")

monitor_setup.config = ComparisonConfig(
    metric = SimpleColumnMetric.inferred_data_type,
    baseline = TrailingWindowBaseline(size=7),
    operator = ComparisonOperator.eq
)
```

## Model Performance

### F1 Score
```python
from whylabs_toolkit.monitor import MonitorSetup
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="f1_score_monitor")

monitor_setup.config = DiffConfig(
    metric = DatasetMetric.classification_f1,
    mode = DiffMode.pct,
    threshold = 10,
    baseline = TrailingWindowBaseline(size=7)
)
```
### Precision
```python
from whylabs_toolkit.monitor import MonitorSetup
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="precision_score_monitor")

monitor_setup.config = DiffConfig(
    metric = DatasetMetric.classification_precision,
    mode = DiffMode.pct,
    threshold = 10,
    baseline = TrailingWindowBaseline(size=7)
)
```
### Recall
```python
from whylabs_toolkit.monitor import MonitorSetup
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="recall_score_monitor")

monitor_setup.config = DiffConfig(
    metric = DatasetMetric.classification_recall,
    mode = DiffMode.pct,
    threshold = 10,
    baseline = TrailingWindowBaseline(size=7)
)
```
### Accuracy
```python
from whylabs_toolkit.monitor import MonitorSetup
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="accuracy_score_monitor")

monitor_setup.config = DiffConfig(
    metric = DatasetMetric.classification_accuracy,
    mode = DiffMode.pct,
    threshold = 10,
    baseline = TrailingWindowBaseline(size=7)
)
```