# Monitor Builder workflow

This package gives users a workflow to author and modify existing WhyLabs Monitors, 
using a Builder-Manager approach.

```python
# org_id and dataset_id are both defined through env_vars: DATASET_ID and ORG_ID

credentials = MonitorCredentials(
    monitor_id="my-awesome-monitor-3"
)


builder = MonitorBuilder(
    credentials=credentials,
    percentage=20,
)

manager = MonitorManager(
    monitor_builder=builder
)

manager.add_actions(
    actions=[
        SendEmail(type="email", target="some_mail@example.com")
    ]
)
```

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