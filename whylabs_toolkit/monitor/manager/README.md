# Monitor creation workflow

This package gives users a workflow to author and modify existing WhyLabs Monitors. 
Users want to use and modify monitors to capture unexpected changes on their data based on their business logics and needs. 
A Data Monitor can be briefly described as: a way to be **alerted** when a certain **criteria** is met.
 

## Set your credentials
The first step is to set your credentials to access WhyLabs. Define your environment variables:
```python
import os

os.environ["ORG_ID"] = "org-id"
os.environ["WHYLABS_API_KEY"] = "api-key"

# Option 1: set your dataset_id as an env var 
os.environ["DATASET_ID"] = "dataset-id"
```

## Create a Monitor Builder

You will need to create a `MonitorBuilder` object. The `monitor_id` passed to 
the builder is the unique name given to a monitor. If there is an existing monitor under that ID, 
the builder will try to fetch it first. Otherwise, it will create a default one.

```python
from whylabs_toolkit.monitor.manager import MonitorBuilder

builder = MonitorBuilder(
    monitor_id="my-awesome-monitor",
    dataset_id=None # Option 2: set your dataset_id as an argument 
)
```

## Add a configuration
 
A configuration (or *criteria*) declares **how** WhyLabs will **detect an anomaly** and will then trigger alerts. 
Here is an example configuration to detect Drift:

```python
from whylabs_toolkit.monitor.models import *

builder.config = StddevConfig(
        metric=SimpleColumnMetric.median,
        factor=2.0,
        baseline=TrailingWindowBaseline(size=14)
)
```

## Add alert actions 
Now that you have a logic to which you will generate alerts, you need to define **how** you wish to be notified:

```python
from pydantic.networks import HttpUrl, parse_obj_as

builder.actions = [
        SendEmail(target="some_mail@example.com"),
        SlackWebhook(target=parse_obj_as(HttpUrl, "https://slack.web.hook.com"))
]
```

## Define a schedule
You will also need to define **when** your criteria will run to check if it will meet your expectations.

```python
builder.schedule = FixedCadenceSchedule(cadence=Cadence.weekly)
```


## Build the Monitor object

You need to build your changes to the object to be able to persist them to WhyLabs later on.

```python
builder.build()
```

## Interact with the created Monitor


To persist your monitor to WhyLabs, you will create a `MonitorManager`
object and save it:

```python
from whylabs_toolkit.monitor.manager import MonitorManager

manager = MonitorManager(
    builder=builder
)

manager.save()
```
Which will validate and push changes to your WhyLabs monitors.

### Other Monitor interactions

With the `MonitorManager`, you are also able to either dump the monitor config to a JSON configuration with `dump()` 
or `validate()` it to check if you've set things correctly.
```python
manager.validate()

print(manager.dump())
```
Which will print the following JSON object to the console:
```bash
{
  "schemaVersion": 1,
  "orgId": "org-id",
  "datasetId": "dataset-id",
  "granularity": "monthly",
  "analyzers": [
    {
      "id": "my-awesome-monitor-3-analyzer",
      "displayName": "my-awesome-monitor-3-analyzer",
      "tags": [],
      "schedule": {
        "type": "fixed",
        "cadence": "weekly"
      },
      "targetMatrix": {
        "segments": [],
        "type": "column",
        "include": [
          "*"
        ],
        "exclude": []
      },
      "config": {
        "metric": "median",
        "type": "stddev",
        "factor": 2.0,
        "minBatchSize": 1,
        "baseline": {
          "type": "TrailingWindow",
          "size": 14
        }
      }
    }
  ],
  "monitors": [
    {
      "id": "my-awesome-monitor-3",
      "displayName": "my-awesome-monitor-3",
      "tags": [],
      "analyzerIds": [
        "my-awesome-monitor-3-analyzer"
      ],
      "schedule": {
        "type": "immediate"
      },
      "disabled": false,
      "severity": 3,
      "mode": {
        "type": "DIGEST"
      },
      "actions": [
        {
          "type": "email",
          "target": "some_mail@example.com"
        },
        {
          "type": "slack",
          "target": "https://slack.web.hook.com"
        }
      ]
    }
  ]
}
```
It can be used to interact with WhyLabs' API endpoints as the request body. The validation method call is optional at this point.

## Monitor examples

What usually differs from monitors is **how** data changes will trigger alerts for the users.
In here we will see a couple of different examples on how to set different monitor configurations
into three main categories. All of them are relying on understanding the Monitor authoring workflow
[previously explained](#add-a-configuration) on this tutorial.


### Diff
To capture a % difference in the F1-Score, you can create a `DiffConfig`, 
and compare it either to a fixed Reference Profile:
```python
from whylabs_toolkit.monitor.models import *

builder.config = DiffConfig(
    metric=DatasetMetric.classification_f1, 
    baseline=ReferenceProfileId(profileId="ref-prof-id"), 
    mode=DiffMode.pct, # or DiffMode.abs 
    threshold=5
)
```

or to a Trailing Window Baseline:
```python
from whylabs_toolkit.monitor.models import *

builder.config = DiffConfig(
    metric=DatasetMetric.classification_f1, 
    baseline=TrailingWindowBaseline(size=14), 
    mode=DiffMode.pct, # or DiffMode.abs 
    threshold=5
)
```

***IMPORTANT:*** For both of these algorithms, you will need to change the Target Matrix property of the Builder
to a Dataset-level, since these aren't related to a particular column, as follows:

```python
builder.target_matrix = DatasetMatrix()
```

### Null counts ratio
To compare the ratio of the null counts on a particular column to a certain time range.
```python
from whylabs_toolkit.monitor.models import *

builder.config = StddevConfig(
    factor = 1.5,
    metric = SimpleColumnMetric.count_null_ratio,
    baseline = TrailingWindowBaseline(size=14)
)

```

### Drift
To detect Drift on a continuous feature, you can use the `DriftConfig` object with its default
drift calculation algorithm: Hellinger's Distance. 

```python
from whylabs_toolkit.monitor.models import *

builder.config = DriftConfig(
    metric = ComplexMetrics.histogram,
    threshold = 0.6,
    baseline = TrailingWindowBaseline(size=7),
)
```


## Modify properties of existing Monitors
In case you have an existing Monitor, and you wish to change one thing about it,
you can instantiate again a `MonitorBuilder`, make the changes and `manager.save()` it again.
Here are a few examples of other things you can do before building your monitor:

```python
from datetime import datetime

builder = MonitorBuilder(
    monitor_id="existing-monitor-id"
)

# Set a fixed time range, with a helper method
builder.set_fixed_dates_baseline(
    start_date=datetime(2022,1,12),
    end_date=datetime(2022,1,29)
)

# Include only certain columns to be monitored
builder.set_target_columns(columns=["feature_1", "feature_2"])

# Exclude other unnecessary colums
builder.exclude_target_columns(columns=["id_column"])


# Include ALL DISCRETE columns
builder.set_target_columns(columns=["group: discrete"])

# Exclude ALL OUTPUT columns
builder.exclude_target_columns(columns=["group:output"])


# Instead of setting a new action, extend the existing ones
builder.actions.extend([SendEmail(target="other_email@example.com")])

## Save your modifications
builder.build()

manager = MonitorManager(builder=builder)
manager.save()

```

## Other configurations

Use Songbird's DEV endpoint. Default is PROD. 
```python
import os

os.environ["WHYLABS_HOST"] = "https://songbird.development.whylabsdev.com"
```