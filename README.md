# WhyLabs Toolkit

The WhyLabs Toolkit package contains helper methods to help users interact with our internal APIs. Users will benefit from using it if they want to abstract some of WhyLabs' internal logic and also automate recurring API calls.

## Configuration
In order to configure `whylabs_toolkit`, you will need to set `WHYLABS_API_KEY` as an environment variable. With that, the package will be able to authenticate with WhyLabs' API endpoints. You can configure a token for your account directly on the platform. 

To manage dependencies we use [Poetry](https://python-poetry.org/) and also a handful of `Makefile` commands. To install all necessary dependencies and activate the virtual environment, run:

```bash
make setup && poetry shell
```

## Usage
In here we will describe some examples on how to use the package. You can also check [the integration tests directory](./tests/) to have more insights on how things are built to be used.
### Models
Users can change their model type between `REGRESSION`, `CLASSIFICATION` and `EMBEDDINGS`, using the models helpers, as the example shows:
```python
from whylabs_toolkit.helpers.models import update_model_metadata

update_model_metadata(
    org_id="org_id",
    dataset_id="dataset_id",
    model_type="CLASSIFICATION"
)
```

And to change the model granularity:

```python
from whylabs_toolkit.helpers.models import update_model_metadata

update_model_metadata(
    dataset_id="dataset_id", 
    org_id="org_id", 
    time_period="P1M"
)
```

>**NOTE**: Learn more on the time period config options with the `whylabs_client.model.time_period.TimePeriod` class, available after you've configured your environment with the described make command above.

### Entity Schema
Entity Schema helpers assist users to change some of their dataset metadata, such as data types, discreteness and column classification (between inputs and outputs). Here's an example that covers all three cases:

#### Column Classes
```python
from whylabs_toolkit.helpers.schema import (
    UpdateColumnClassifiers, 
    ColumnsClassifiers,
)

# Note that you don't need to specify all existing columns, but only those you wish to modify

classifiers = ColumnsClassifiers(
    outputs=["actual_temperature", "predicted_temperature"]
)

update_entity = UpdateColumnClassifiers(
    classifiers=classifiers,
    dataset_id="dataset_id",
    org_id="org_id"
)

update_entity.update()

```
#### Data types
```python
from whylabs_toolkit.helpers.schema import UpdateEntityDataTypes
from whylabs_toolkit.monitor_schema.models.column_schema import ColumnDataType

columns_schema = {
    "temperature": ColumnDataType.fractional,
    "is_active": ColumnDataType.boolean
}

update_data_types = UpdateEntityDataTypes(
    dataset_id="dataset_id",
    columns_schema=columns_schema,
    org_id="org_id"
)

update_data_types.update()
```
#### Discreteness
```python
from whylabs_toolkit.helpers.schema import (
    UpdateColumnsDiscreteness,
    ColumnsDiscreteness
)

columns = ColumnsDiscreteness(
    discrete=["temperature"]
)

update_discreteness = UpdateColumnsDiscreteness(
    dataset_id="dataset_id",
    columns=columns,
    org_id="org_id"
)

update_discreteness.update()
```
### Monitors
The Monitors helpers will help you manage existing alerts on WhyLabs' platform.

#### Delete monitor

```python
from whylabs_toolkit.helpers.monitor_helpers import delete_monitor

delete_monitor(
    org_id="org_id",
    dataset_id="dataset_id",
    monitor_id="monitor_id"
)
```

## Get in touch
If you want to learn more how you can benefit from this package or if there is anything missing, please [contact our support](https://whylabs.ai/contact-us), we'll be more than happy to help you!