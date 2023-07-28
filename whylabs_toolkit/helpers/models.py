import logging
from typing import Optional

from whylabs_client.exceptions import ApiValueError, ApiException
from whylabs_client.model.model_type import ModelType
from whylabs_client.model.time_period import TimePeriod
from whylabs_client.model.metric_schema import MetricSchema

from whylabs_toolkit.helpers.utils import get_models_api
from whylabs_toolkit.helpers.config import Config

logger = logging.getLogger(__name__)


def update_model_metadata(
    dataset_id: Optional[str] = None,
    org_id: Optional[str] = None,
    time_period: Optional[str] = None,
    model_type: Optional[str] = None,
    config: Config = Config(),
) -> None:
    """
    Update model attributes like model type and period.
    """
    org_id = org_id or config.get_default_org_id()
    dataset_id = dataset_id or config.get_default_dataset_id()

    api = get_models_api(config=config)

    model_metadata = api.get_model(org_id=org_id, model_id=dataset_id)
    logger.debug(f"Updating dataset with current metadata: \n {model_metadata}")

    try:
        resp = api.update_model(
            org_id=org_id,
            model_id=dataset_id,
            model_name=model_metadata["name"],
            time_period=TimePeriod(time_period) if time_period else model_metadata["time_period"],
            model_type=ModelType(model_type) if model_type else model_metadata["model_type"],
        )
        logger.debug(f"Updated sucessfully! Resp: {resp}")
    except ApiValueError as e:
        raise e


def add_custom_metric(
    label: str,
    column: str,
    default_metric: str,
    org_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    config: Config = Config(),
) -> None:

    org_id = org_id or config.get_default_org_id()
    dataset_id = dataset_id or config.get_default_dataset_id()

    api = get_models_api(config=config)
    metric_schema = MetricSchema(label=label, column=column, default_metric=default_metric)

    try:
        api.put_entity_schema_metric(org_id, dataset_id, metric_schema)
        logger.info(f"Updated entity schema metric!")
    except ApiException as e:
        logger.error("Exception when calling ModelsApi -> put_entity_schema_metric\n")
        raise e
