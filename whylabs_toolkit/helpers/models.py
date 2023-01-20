import logging
from typing import Optional

from whylabs_client.exceptions import ApiValueError
from whylabs_client.model.model_type import ModelType
from whylabs_client.model.time_period import TimePeriod

from whylabs_toolkit.helpers.utils import get_models_api

logger = logging.getLogger(__name__)


def update_model_metadata(
    dataset_id: str, org_id: Optional[str] = None, time_period: Optional[str] = None, model_type: Optional[str] = None
) -> None:
    """
    Update model attributes like model type and period.
    """
    api = get_models_api()

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


if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    update_model_metadata(dataset_id="model-7", org_id="org-fjx9Rz", time_period="P1M")
