# Monitor creation workflow

This package gives users a workflow to author and modify existing WhyLabs Monitors.

## 1. Set your credentials
The first step is to set your credentials to WhyLabs with `MonitorCredentials`.

```python
import os

from whylabs_toolkit.monitor.manager.credentials import MonitorCredentials

os.environ["ORG_ID"] = "org-id"
os.environ["DATASET_ID"] = "dataset-id"

credentials = MonitorCredentials(
    monitor_id="my-awesome-monitor-3",
    dataset_id=None  # Optionally, you might set the `dataset_id` as an argument instead
)
```

## 2. Create a MonitorBuilder object

Then, you will need to create a `MonitorBuilder` object, 
either for a generic monitor configuration or an available preset. The `monitor_id` passed to 
the `MonitorCredentials` is the unique name given to a monitor. If there is an existing monitor, 
the builder will try to fetch it, otherwise, it will create a default one.

```python
from whylabs_toolkit.monitor.manager import MonitorBuilder

builder = MonitorBuilder(
    credentials=credentials,
)
```

### Add a configuration
This is probably the most important to be configured on a default `MonitorBuilder`. 
It declares how WhyLabs will detect an anomaly and trigger alerts. 
Here is an example configuration to detect Drift:

```python
from datetime import datetime
from whylabs_toolkit.monitor.models import *

# Add a DriftConfig with a Trailing window Baseline
builder.config = StddevConfig(
        metric=SimpleColumnMetric.median,
        factor=2.0,
        baseline=TrailingWindowBaseline(size=14)
)

# Or with a fixed TimeRange, with a helper method

builder.set_fixed_dates_baseline(
    start_date=datetime(2022,1,12),
    end_date=datetime(2022,1,29)
)
```

### Add alert actions 

```python
from pydantic.networks import HttpUrl, parse_obj_as
from whylabs_toolkit.monitor.models.monitor import SendEmail, SlackWebhook

builder.actions = [
        SendEmail(target="some_mail@example.com"),
        SlackWebhook(target=parse_obj_as(HttpUrl, "https://slack.web.hook.com"))
]
```

### Build the Monitor object

This step is important. If you don't build the configured Monitor, you will not be able to
persist changes to WhyLabs, nor get the JSON configuration schema from it.

```python
builder.build()
```

## 3. Interact with the created monitor

```python
from whylabs_toolkit.monitor.manager import MonitorManager

manager = MonitorManager(
    builder=builder
)
```
With the `MonitorManager`, you are able to either dump the monitor config to a JSON configuration with `dump()` 
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
        "cadence": "daily"
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
In case you want to persist changes to your monitor to WhyLabs, you can `save`:

```python
manager.save()
```
Which will validate and push changes to your WhyLabs monitors.