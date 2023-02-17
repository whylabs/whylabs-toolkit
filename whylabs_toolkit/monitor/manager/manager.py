import pytz
from datetime import datetime

from whylabs_toolkit.monitor.manager.builder import MonitorBuilder
from whylabs_toolkit.monitor.models import *
from whylabs_toolkit.monitor.models.analyzer.algorithms import *
from whylabs_toolkit.helpers.utils import get_models_api


class MonitorManager:
    def __init__(self, builder: MonitorBuilder) -> None:
        self._builder = builder

    def deactivate(self) -> None:
        # TODO implement
        pass

    def get_granularity(self) -> Optional[Granularity]:
        api = get_models_api()
        model_meta = api.get_model(
            org_id=self._builder.credentials.org_id, model_id=self._builder.credentials.dataset_id
        )

        time_period_to_gran = {
            "H": Granularity.hourly,
            "D": Granularity.daily,
            "W": Granularity.weekly,
            "M": Granularity.monthly,
        }

        for key, value in time_period_to_gran.items():
            if key in model_meta["time_period"].value:
                return value
        return None

    def dump(self) -> Any:
        doc = Document(
            orgId=self._builder.credentials.org_id,
            datasetId=self._builder.credentials.dataset_id,
            granularity=self.get_granularity(),
            analyzers=[self._builder.analyzer],
            monitors=[self._builder.monitor],
        )
        return doc.json(indent=2, exclude_none=True)

    def validate(self) -> None:
        Monitor.validate(self._builder.monitor)
        Analyzer.validate(self._builder.analyzer)

    def save(self) -> None:
        self.validate()
        api = get_models_api()
        api.put_analyzer(
            org_id=self._builder.credentials.org_id,
            dataset_id=self._builder.credentials.dataset_id,
            analyzer_id=self._builder.credentials.analyzer_id,
            body=self._builder.analyzer.dict(exclude_none=True),  # type: ignore
        )
        api.put_monitor(
            org_id=self._builder.credentials.org_id,
            dataset_id=self._builder.credentials.dataset_id,
            monitor_id=self._builder.credentials.monitor_id,
            body=self._builder.monitor.dict(exclude_none=True),  # type: ignore
        )
