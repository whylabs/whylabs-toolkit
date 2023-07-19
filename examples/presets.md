# WhyLabs Monitors Presets

In this section we will present some existing presets available on the WhyLabs platform, using `whylabs-toolkit`.

On a general line, the configuration workflow will always consist of: 

1. Create a `MonitorSetup` object
```python
monitor_setup = MonitorSetup(monitor_id=...)
```
2. Add a config
```python
monitor_setup.config = SomeConfig(...)
monitor_setup.apply()
```
3. Save it to WhyLabs with `MonitorManager`
```python
manager = MonitorManager(monitor_setup)
manager.save()
```

To understand what other options are available to be set, please check the [Manager Docs](../whylabs_toolkit/monitor/manager/README.md).

## Drift

### Discrete inputs
```python
from whylabs_toolkit.monitor import MonitorSetup, MonitorManager
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="drift_with_discrete_inputs")

monitor_setup.config = DriftConfig(
    metric = ComplexMetrics.frequent_items,
    baseline = TrailingWindowBaseline(size=7),
)

monitor_setup.set_target_columns(columns=["group:discrete"])
monitor_setup.exclude_target_columns(columns=["group:output"])

monitor_setup.apply()

manager = MonitorManager(setup=monitor_setup)
manager.save()
```

### Continuous inputs
```python
from whylabs_toolkit.monitor import MonitorSetup, MonitorManager
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="drift_with_continuous_inputs")

monitor_setup.config = DriftConfig(
    metric = ComplexMetrics.histogram,
    baseline = TrailingWindowBaseline(size=7),
)

monitor_setup.set_target_columns(columns=["group:continuous"])
monitor_setup.exclude_target_columns(columns=["group:output"])

monitor_setup.apply()

manager = MonitorManager(setup=monitor_setup)
manager.save()
```

## Data Quality

### Missing values
```python
from whylabs_toolkit.monitor import MonitorSetup, MonitorManager
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="missing_value_ratio_monitor")

monitor_setup.config = StddevConfig(
    metric = SimpleColumnMetric.count_null_ratio,
    baseline = TrailingWindowBaseline(size=7),
)

monitor_setup.apply()

manager = MonitorManager(setup=monitor_setup)
manager.save()
```

### Unique values: duplicate changes
```python
from whylabs_toolkit.monitor import MonitorSetup, MonitorManager
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="unique_values_estimation")

monitor_setup.config = StddevConfig(
    metric = SimpleColumnMetric.unique_est,
    baseline = TrailingWindowBaseline(size=7),
)

monitor_setup.apply()

manager = MonitorManager(setup=monitor_setup)
manager.save()
```

### Data Type: detect mixed schema
```python
from whylabs_toolkit.monitor import MonitorSetup, MonitorManager
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="monitor_data_type_changes")

monitor_setup.config = ComparisonConfig(
    metric = SimpleColumnMetric.inferred_data_type,
    baseline = TrailingWindowBaseline(size=7),
    operator = ComparisonOperator.eq
)

monitor_setup.apply()

manager = MonitorManager(setup=monitor_setup)
manager.save()
```

### List Comparison

```python
from whylabs_toolkit.monitor import MonitorSetup, MonitorManager
from whylabs_toolkit.monitor.models import *

setup = MonitorSetup(monitor_id="monitor_list_comparison")
setup.config = ListComparisonConfig(
    operator=ListComparisonOperator.in_list,
    expected=[
        ExpectedValue(
            str="expected"
        ),
        ExpectedValue(
            int=123229
        )
    ],
    baseline=TrailingWindowBaseline(size=7),
    metric=SimpleColumnMetric.count_bool
)
setup.apply()

mm = MonitorManager(setup=setup)
mm.save()
```

### Frequent Items
```python
from whylabs_toolkit.monitor import MonitorSetup, MonitorManager
from whylabs_toolkit.monitor.models import *


setup = MonitorSetup(monitor_id="frequent_items")
setup.config = FrequentStringComparisonConfig(
    operator=FrequentStringComparisonOperator.eq,
    baseline=TrailingWindowBaseline(size=7)
)
setup.apply()

mm = MonitorManager(setup=setup)
mm.save()
```

## Model Performance

### F1 Score
```python
from whylabs_toolkit.monitor import MonitorSetup, MonitorManager
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="f1_score_monitor")

monitor_setup.config = DiffConfig(
    metric = DatasetMetric.classification_f1,
    mode = DiffMode.pct,
    threshold = 10,
    baseline = TrailingWindowBaseline(size=7)
)

monitor_setup.apply()

manager = MonitorManager(setup=monitor_setup)
manager.save()
```
### Precision
```python
from whylabs_toolkit.monitor import MonitorSetup, MonitorManager
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="precision_score_monitor")

monitor_setup.config = DiffConfig(
    metric = DatasetMetric.classification_precision,
    mode = DiffMode.pct,
    threshold = 10,
    baseline = TrailingWindowBaseline(size=7)
)

monitor_setup.apply()

manager = MonitorManager(setup=monitor_setup)
manager.save()
```
### Recall
```python
from whylabs_toolkit.monitor import MonitorSetup, MonitorManager
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="recall_score_monitor")

monitor_setup.config = DiffConfig(
    metric = DatasetMetric.classification_recall,
    mode = DiffMode.pct,
    threshold = 10,
    baseline = TrailingWindowBaseline(size=7)
)

monitor_setup.apply()

manager = MonitorManager(setup=monitor_setup)
manager.save()
```
### Accuracy
```python
from whylabs_toolkit.monitor import MonitorSetup, MonitorManager
from whylabs_toolkit.monitor.models import *

monitor_setup = MonitorSetup(monitor_id="accuracy_score_monitor")

monitor_setup.config = DiffConfig(
    metric = DatasetMetric.classification_accuracy,
    mode = DiffMode.pct,
    threshold = 10,
    baseline = TrailingWindowBaseline(size=7)
)

monitor_setup.apply()

manager = MonitorManager(setup=monitor_setup)
manager.save()
```