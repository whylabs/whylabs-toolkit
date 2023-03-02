import logging

from whylabs_toolkit.monitor.manager.builder import MonitorBuilder
from whylabs_toolkit.monitor.models import *
from whylabs_toolkit.monitor.models.analyzer.algorithms import *
from whylabs_toolkit.helpers.utils import get_models_api, get_notification_api, get_notification_request_payload


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitorManager:
    def __init__(self, builder: MonitorBuilder) -> None:
        self._builder = builder
        self.__notifications_api = get_notification_api()
        self.__models_api = get_models_api()

    def deactivate(self) -> None:
        # TODO implement
        pass

    def get_granularity(self) -> Optional[Granularity]:
        model_meta = self.__models_api.get_model(
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

    def _get_existing_notification_actions(self) -> List[str]:
        actions_dict_list = self.__notifications_api.list_notification_actions(org_id=self._builder.credentials.org_id)
        action_ids = []
        for action in actions_dict_list:
            action_ids.append(action.get("id"))
        return action_ids
    
    
    def _parse_monitor_actions(self) -> None:
        existing_actions: List[str] = self._get_existing_notification_actions()
        if not self._builder.monitor:
            raise ValueError("You must call build() on your MonitorBuilder object!")
        
        # only designed for slack and email actions
        for action in self._builder.monitor.actions:
            payload_key = get_notification_request_payload(action=action)
            
            if action.id not in existing_actions:
                logger.info(f"Didn't find a {action.type} action under the ID {action.id}, creating one now!")
                self.__notifications_api.put_notification_action(
                    org_id=self._builder.credentials.org_id,
                    type=action.type.upper(),
                    action_id=action.id,
                    body={payload_key: action.destination}
                )
            
        self._builder.monitor.actions = [GlobalAction(target=action.id) for action in self._builder.monitor.actions]
            

    
    def dump(self) -> Any:
        self._parse_monitor_actions()
        
        doc = Document(
            orgId=self._builder.credentials.org_id,
            datasetId=self._builder.credentials.dataset_id,
            granularity=self.get_granularity(),
            analyzers=[self._builder.analyzer],
            monitors=[self._builder.monitor],
        )
        return doc.json(indent=2, exclude_none=True)

    def validate(self) -> bool:
        try:
            Monitor.validate(self._builder.monitor)
            Analyzer.validate(self._builder.analyzer)
        finally:
            return True

    def save(self) -> None:
        if self.validate() is True:
            
            self.__models_api.put_analyzer(
                org_id=self._builder.credentials.org_id,
                dataset_id=self._builder.credentials.dataset_id,
                analyzer_id=self._builder.credentials.analyzer_id,
                body=self._builder.analyzer.dict(exclude_none=True),  # type: ignore
            )
            self.__models_api.put_monitor(
                org_id=self._builder.credentials.org_id,
                dataset_id=self._builder.credentials.dataset_id,
                monitor_id=self._builder.credentials.monitor_id,
                body=self._builder.monitor.dict(exclude_none=True),  # type: ignore
            )
