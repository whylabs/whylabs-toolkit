# Monitor Builder workflow

This package gives users a workflow to author and modify existing WhyLabs Monitors.

## 1. Set your credentials
The first step is to set your credentials to WhyLabs with `MonitorCredentials`. 

```python
import os

from whylabs_toolkit.monitor.builder.credentials import MonitorCredentials

os.environ["ORG_ID"] = "org-id" 
os.environ["DATASET_ID"] = "dataset-id" 

credentials = MonitorCredentials(
    monitor_id="my-awesome-monitor-3",
    dataset_id=None # Optionally, you might set the `dataset_id` as an argument instead
)
```

## 2. Create a Builder object

Then, you will need to create a `MonitorBuilder` object, 
either for a generic monitor configuration or an available preset. The `monitor_id` passed to 
the `MonitorCredentials` is the unique name given to a monitor. If there is an existing monitor, 
the Builder will fetch it. Otherwise, it will create a default one.


```python
from whylabs_toolkit.monitor.builder.builder import MonitorBuilder

builder = MonitorBuilder(
    credentials=credentials,
)
```

## 3. Manage the Monitor

```python
from whylabs_toolkit.monitor.builder.manager import MonitorManager

manager = MonitorManager(
    monitor_builder=builder
)
```

### 3.1 Add a configuration
This is probably the most important to be configured on a default `MonitorBuilder`. 
It declares how WhyLabs will detect an anomaly and trigger alerts. Here are a few examples:

#### 3.1.1 Drift config
```python
import pytz
from datetime import datetime

from whylabs_toolkit.monitor.models.analyzer.algorithms import (
    StddevConfig,
    TimeRangeBaseline, 
    TimeRange,
    SimpleColumnMetric,
    TrailingWindowBaseline
)

# Fixed time range Baseline 
manager.add_config(
    config=StddevConfig(
        metric=SimpleColumnMetric.median,
        factor=2.0, # Multiplier used with stddev to build the upper and lower bounds
        baseline=TimeRangeBaseline(
            TimeRange(
                start=datetime(2022,12,1, tzinfo=pytz.utc),
                end=datetime(2022,12,31, tzinfo=pytz.utc)
            )
        )
    )
)

# Or a Trailing window Baseline
manager.add_config(
    config=StddevConfig(
        metric=SimpleColumnMetric.median,
        factor=2.0,
        baseline=TrailingWindowBaseline(
            size=14,
            # Optionally, set a timerange to be excluded from the trailing window
            exclusionRanges=TimeRange(
                start=datetime(2022,12,1, tzinfo=pytz.utc),
                end=datetime(2022,12,31, tzinfo=pytz.utc)
            )
        )
    )
)
```

### 3.2 Add alert actions 

```python
from pydantic.networks import HttpUrl
from whylabs_toolkit.monitor.models.monitor import SendEmail, SlackWebhook

manager.add_actions(
    actions=[
        SendEmail(type="email", target="some_mail@example.com"),
        SlackWebhook(type="slack", target=HttpUrl("https://slack.web.hook.com"))
    ]
)
```


## 4. Validate and Save

With the modified Manager, you are able to either dump the monitor config to a JSON-string with `dump()` or `validate()` it to check if you've set things correctly.
```python
manager.validate()

print(manager.dump())
```

In case you want to persist changes to WhyLabs directly, you can call:
```python
manager.save()
```
Which will validate and push changes to your WhyLabs monitors.