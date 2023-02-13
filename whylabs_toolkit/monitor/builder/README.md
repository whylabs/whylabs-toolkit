# Monitor Builder workflow

This package gives users a workflow to author and modify existing WhyLabs Monitors, 
using a Builder-Manager approach.

```python
builder = MissingDataMonitorBuilder(
    org_id=os.environ["ORG_ID"],
    dataset_id=os.environ["DATASET_ID"],
    monitor_id="my-awesome-monitor-3",
    percentage=20,
)

# defaults to trailing window of 14 days

builder.configure_fixed_dates_baseline(
    start_date=datetime(2022,12,8),
    end_date=datetime(2022,12,14)
)

manager = MonitorManager(
    monitor_builder=builder
)

manager.add_actions(
    actions=[
        SendEmail(type="email", target="some_mail@example.com")
    ]
)

print(manager.dump())
manager.validate()
manager.save()
```