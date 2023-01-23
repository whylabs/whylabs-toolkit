import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from whylabs_toolkit.helpers.client import client
from whylabs_toolkit.helpers.config import Config
from whylabs_toolkit.helpers.utils import get_models_api

BASE_ENDPOINT = "https://api.whylabsapp.com"

logger = logging.getLogger(__name__)


# TODO make arguments more generic and meaningful


class UpdateEntity(ABC):
    def __init__(self, dataset_id: str, org_id: Optional[str] = None):
        self.dataset_id = dataset_id
        self.org_id = org_id or Config().get_default_org_id()
        self.api = get_models_api()

    def _get_entity_schema(self) -> Any:
        entity_schema = self.api.get_entity_schema(org_id=self.org_id, dataset_id=self.dataset_id)
        return entity_schema

    def _put_entity_schema(self, schema: Dict) -> None:
        self.api.put_entity_schema(org_id=self.org_id, dataset_id=self.dataset_id, body=schema)

    def _get_current_entity_schema(self) -> None:
        self.current_entity_schema = self._get_entity_schema()
        self.columns_dict = self.current_entity_schema["columns"]

    @abstractmethod
    def _validate_input(self) -> None:
        pass

    @abstractmethod
    def _update_entity_schema(self) -> None:
        pass

    def _put_updated_entity_schema(self) -> None:
        metadata_dict = self.current_entity_schema["metadata"]
        entity_schema_dict = {"columns": self.columns_dict, "metadata": metadata_dict}
        self._put_entity_schema(schema=entity_schema_dict)

    def update(self) -> None:
        self._validate_input()
        self._get_current_entity_schema()
        self._update_entity_schema()
        self._put_updated_entity_schema()


@dataclass
class ColumnsClasses:
    inputs: List[str] = field(default=None)  # type: ignore
    outputs: List[str] = field(default=None)  # type: ignore

    def __post_init__(self) -> None:
        if self.inputs is None:
            self.inputs = []
        if self.outputs is None:
            self.outputs = []


class UpdateColumnClasses(UpdateEntity):
    def __init__(self, dataset_id: str, classes: ColumnsClasses, org_id: Optional[str] = None):
        super().__init__(dataset_id, org_id)
        self.classes = classes

    def _validate_input(self) -> None:
        if self.classes.inputs == [] and self.classes.outputs == []:
            logger.error("You must define either input or output features to use this function.")
            raise ValueError

    def _update_entity_schema(self) -> Any:
        for key in self.columns_dict.keys():
            if key in self.classes.inputs and self.columns_dict[key]["classifier"] != "input":
                self.columns_dict[key].update({"classifier": "input"})
            elif key in self.classes.outputs and self.columns_dict[key]["classifier"] != "output":
                self.columns_dict[key].update({"classifier": "output"})


class UpdateEntityDataTypes(UpdateEntity):
    """
    Update data types on each column of the dataset

    Arguments
    ----
    columns_schema: Dict[str, str]
        The keys are column names and the values are the
        desired data_types, as the example below shows

    ```python
    columns_schema = {
        "column_1": "fractional",
        "column_2": "bool",
        "column_3": "string"
    }
    ```

    These are the currently supported data types:
    ---
    - integral
    - fractional
    - bool
    - string
    - unknown
    - null
    ---
    """

    def __init__(self, dataset_id: str, columns_schema: Dict[str, str], org_id: Optional[str] = None):
        super().__init__(dataset_id, org_id)
        self.columns_schema = columns_schema

    def _validate_input(self) -> None:
        possible_data_types = ["integral", "fractional", "bool", "string", "unknown", "null"]
        for value in self.columns_schema.values():
            if value not in possible_data_types:
                logger.error("{value} is not an accepted data type! Refer to this functions help to learn more.")
                raise ValueError

    def _update_entity_schema(self) -> None:
        for key, value in self.columns_schema.items():
            if key in self.columns_dict.keys() and self.columns_dict[key]["dataType"] != value:
                self.columns_dict[key].update({"dataType": self.columns_schema[key]})


@dataclass
class ColumnsDiscreteness:
    discrete: List[str] = field(default=None)  # type: ignore
    continuous: List[str] = field(default=None)  # type: ignore

    def __post_init__(self) -> None:
        if self.discrete is None:
            self.discrete = []
        if self.continuous is None:
            self.continuous = []


class UpdateColumnsDiscreteness(UpdateEntity):
    def __init__(self, dataset_id: str, classes: ColumnsDiscreteness, org_id: Optional[str] = None):
        super().__init__(dataset_id, org_id)
        self.classes = classes

    def _validate_input(self) -> None:
        if self.classes.discrete == [] and self.classes.continuous == []:
            logger.error("You must define either discrete or continuous columns to use this.")
            raise ValueError

    def _update_entity_schema(self) -> Any:
        for key in self.columns_dict.keys():
            if key in self.classes.discrete and self.columns_dict[key]["discreteness"] != "discrete":
                self.columns_dict[key].update({"discreteness": "discrete"})
            elif key in self.classes.continuous and self.columns_dict[key]["discreteness"] != "continuous":
                self.columns_dict[key].update({"discreteness": "continuous"})
