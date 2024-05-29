import logging
import json
from pathlib import Path
from typing import Optional, Any

from jsonschema import validate, ValidationError
from whylabs_client.api.monitor_api import MonitorApi

from whylabs_toolkit.monitor.manager.monitor_setup import MonitorSetup
from whylabs_toolkit.monitor.models import *
from whylabs_toolkit.helpers.monitor_helpers import get_model_granularity
from whylabs_toolkit.helpers.config import Config
from whylabs_toolkit.helpers.utils import get_monitor_api


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitorManager:
    def __init__(
        self,
        setup: MonitorSetup,
        eager: Optional[bool] = None,
        monitor_api: Optional[MonitorApi] = None,
        config: Config = Config(),
    ) -> None:
        self._setup = setup
        self.__monitor_api = monitor_api or get_monitor_api(config=config)
        self.__eager = eager

    def _get_current_monitor_config(self) -> Optional[Any]:
        monitor_config = self.__monitor_api.get_monitor_config_v3(
            org_id=self._setup.credentials.org_id, dataset_id=self._setup.credentials.dataset_id
        )
        return monitor_config

    def dump(self) -> Any:
        doc = Document(
            orgId=self._setup.credentials.org_id,
            datasetId=self._setup.credentials.dataset_id,
            granularity=get_model_granularity(
                org_id=self._setup.credentials.org_id, dataset_id=self._setup.credentials.dataset_id  # type: ignore
            ),
            analyzers=[self._setup.analyzer],
            monitors=[self._setup.monitor],
            allowPartialTargetBatches=self.__eager,
        )
        return doc.json(indent=2, exclude_none=True)

    def validate(self) -> bool:
        try:
            Monitor.validate(self._setup.monitor)
            Analyzer.validate(self._setup.analyzer)

            with open(f"{Path(__file__).parent.parent.resolve()}/schema/schema.json", "r") as f:
                schema = json.load(f)
            document = self.dump()
            validate(instance=json.loads(document), schema=schema)
            return True
        except ValidationError as e:
            raise e

    def save(self) -> None:
        if self.validate() is True:
            self.__monitor_api.put_analyzer(
                org_id=self._setup.credentials.org_id,
                dataset_id=self._setup.credentials.dataset_id,
                analyzer_id=self._setup.credentials.analyzer_id,
                body=self._setup.analyzer.dict(exclude_none=True),  # type: ignore
            )
            self.__monitor_api.put_monitor(
                org_id=self._setup.credentials.org_id,
                dataset_id=self._setup.credentials.dataset_id,
                monitor_id=self._setup.credentials.monitor_id,
                body=self._setup.monitor.dict(exclude_none=True),  # type: ignore
            )
        if self.__eager is not None:
            current_config = self._get_current_monitor_config()

            if self.__eager != current_config.get("allowPartialTargetBatches"):  # type: ignore
                current_config["allowPartialTargetBatches"] = self.__eager  # type: ignore
                self.__monitor_api.put_monitor_config_v3(
                    org_id=self._setup.credentials.org_id,
                    dataset_id=self._setup.credentials.dataset_id,
                    body=current_config,
                )
