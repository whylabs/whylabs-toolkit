import logging
from typing import Any, List, Optional

from whylabs_client.exceptions import ApiValueError
from whylabs_client.exceptions import NotFoundException

from whylabs_toolkit.helpers.config import Config
from whylabs_toolkit.helpers.utils import get_monitor_api, get_models_api
from whylabs_toolkit.monitor.models import Granularity

BASE_ENDPOINT = "https://api.whylabsapp.com"
logger = logging.getLogger(__name__)


# TODO create deactivate_monitor


def get_monitor_config(org_id: str, dataset_id: str, config: Config = Config()) -> Any:
    api = get_monitor_api(config=config)
    monitor_config = api.get_monitor_config_v3(org_id=org_id, dataset_id=dataset_id)
    return monitor_config


def get_monitor(monitor_id: str, org_id: Optional[str], dataset_id: Optional[str], config: Config = Config()) -> Any:
    if not org_id:
        org_id = config.get_default_org_id()
    if not dataset_id:
        dataset_id = config.get_default_dataset_id()
    api = get_monitor_api(config=config)
    return api.get_monitor(org_id=org_id, dataset_id=dataset_id, monitor_id=monitor_id)


def get_analyzer_ids(org_id: str, dataset_id: str, monitor_id: str, config: Config = Config()) -> Any:
    monitor_config = get_monitor_config(org_id=org_id, dataset_id=dataset_id, config=config)
    for item in monitor_config["monitors"]:
        if item["id"] == monitor_id:
            resp = item["analyzerIds"]
            return resp


def get_analyzers(
    monitor_id: str, org_id: Optional[str], dataset_id: Optional[str], config: Config = Config()
) -> List[Any]:
    if not org_id:
        org_id = config.get_default_org_id()
    if not dataset_id:
        dataset_id = config.get_default_dataset_id()
    api = get_monitor_api(config=config)
    analyzers = []
    analyzer_ids = get_analyzer_ids(org_id=org_id, dataset_id=dataset_id, monitor_id=monitor_id, config=config)
    if analyzer_ids:
        for analyzer in analyzer_ids:
            analyzers.append(api.get_analyzer(org_id=org_id, dataset_id=dataset_id, analyzer_id=analyzer))
        return analyzers
    else:
        raise NotFoundException


def get_model_granularity(org_id: str, dataset_id: str, config: Config = Config()) -> Optional[Granularity]:
    api = get_models_api(config=config)
    model_meta = api.get_model(org_id=org_id, model_id=dataset_id)

    time_period_to_gran = {
        "H": Granularity.hourly,
        "D": Granularity.daily,
        "W": Granularity.weekly,
        "M": Granularity.monthly,
    }

    for key, value in time_period_to_gran.items():
        if key in model_meta["time_period"]:
            return value
    return None


def delete_monitor(org_id: str, dataset_id: str, monitor_id: str, config: Config = Config()) -> None:
    api = get_monitor_api(config=config)
    try:
        analyzer_ids = get_analyzer_ids(org_id=org_id, dataset_id=dataset_id, monitor_id=monitor_id, config=config)
        if analyzer_ids is None:
            return
        for analyzer_id in analyzer_ids:
            resp_analyzer = api.delete_analyzer(org_id=org_id, dataset_id=dataset_id, analyzer_id=analyzer_id)
            logger.debug(f"Deleted analyzer with Resp:{resp_analyzer}")
        resp_monitor = api.delete_monitor(org_id=org_id, dataset_id=dataset_id, monitor_id=monitor_id)
        logger.debug(f"Deleted monitor with Resp:{resp_monitor}")
    except ApiValueError as e:
        raise e
