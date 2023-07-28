from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from whylabs_client.models import EntitySchema

from whylabs_toolkit.helpers.config import Config
from whylabs_toolkit.helpers.utils import get_models_api
from whylabs_toolkit.monitor.models.column_schema import ColumnDataType

BASE_ENDPOINT = "https://api.whylabsapp.com"


@dataclass
class ColumnsClassifiers:
    inputs: List[str] = field(default_factory=list)  # type: ignore
    outputs: List[str] = field(default_factory=list)  # type: ignore


@dataclass
class ColumnsDiscreteness:
    discrete: List[str] = field(default_factory=list)  # type: ignore
    continuous: List[str] = field(default_factory=list)  # type: ignore


class UpdateEntity(ABC):
    def __init__(self, dataset_id: Optional[str] = None, org_id: Optional[str] = None, config: Config = Config()):
        self.dataset_id = dataset_id or Config().get_default_dataset_id()
        self.org_id = org_id or Config().get_default_org_id()
        self.api = get_models_api(config=config)

    def _get_entity_schema(self) -> Any:
        entity_schema = self.api.get_entity_schema(org_id=self.org_id, dataset_id=self.dataset_id)
        return entity_schema

    def _put_entity_schema(self, schema: EntitySchema) -> None:
        self.api.put_entity_schema(org_id=self.org_id, dataset_id=self.dataset_id, entity_schema=schema)

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
        entity_schema_dict = EntitySchema(columns=self.columns_dict, metadata=metadata_dict)
        self._put_entity_schema(schema=entity_schema_dict)

    def update(self) -> None:
        self._validate_input()
        self._get_current_entity_schema()
        self._update_entity_schema()
        self._put_updated_entity_schema()


class UpdateColumnClassifiers(UpdateEntity):
    def __init__(self, classifiers: ColumnsClassifiers, org_id: Optional[str] = None, dataset_id: Optional[str] = None):
        super().__init__(dataset_id, org_id)
        self.classifiers = classifiers

    def _validate_input(self) -> None:
        if self.classifiers.inputs == [] and self.classifiers.outputs == []:
            raise ValueError("You must define either input or output features to use this function.")
        same_list = [item for item in self.classifiers.inputs if item in self.classifiers.outputs]
        if same_list:
            raise ValueError(f"Column {same_list[0]} must either be input or output.")

    def _update_entity_schema(self) -> Any:
        for key in self.columns_dict.keys():
            if key in self.classifiers.inputs and self.columns_dict[key]["classifier"] != "input":
                self.columns_dict[key].classifier = "input"
            elif key in self.classifiers.outputs and self.columns_dict[key]["classifier"] != "output":
                self.columns_dict[key].classifier = "output"


class UpdateEntityDataTypes(UpdateEntity):
    """
    Update data types on each column of the dataset

    Arguments
    ----
    columns_schema: Dict[str, ColumnDataType]
        The keys are column names and the values are the
        desired data_types, as the example below shows

    ```python
    columns_schema = {
        "column_1": ColumnDataType.fractional,
        "column_2": ColumnDataType.boolean,
        "column_3": ColumnDataType.string,
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

    def __init__(
        self, columns_schema: Dict[str, ColumnDataType], org_id: Optional[str] = None, dataset_id: Optional[str] = None
    ):
        super().__init__(dataset_id, org_id)
        self.columns_schema = columns_schema

    def _validate_input(self) -> None:
        for data_type in self.columns_schema.values():
            if not isinstance(data_type, ColumnDataType):
                raise ValueError(
                    f"{data_type} is not an accepted data type! Refer to this functions help to learn more."
                )

    def _update_entity_schema(self) -> None:
        for column, data_type in self.columns_schema.items():
            if column in self.columns_dict.keys() and self.columns_dict[column]["data_type"] != data_type.value:
                self.columns_dict[column].data_type = self.columns_schema[column].value


class UpdateColumnsDiscreteness(UpdateEntity):
    def __init__(
        self,
        columns: ColumnsDiscreteness,
        org_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
    ):
        super().__init__(dataset_id, org_id)
        self.columns = columns

    def _validate_input(self) -> None:
        if self.columns.discrete == [] and self.columns.continuous == []:
            raise ValueError("You must define either discrete or continuous columns to use this.")

        same_list = [item for item in self.columns.discrete if item in self.columns.continuous]
        if same_list:
            raise ValueError(f"Column {same_list[0]} must either be discrete or continuous.")

    def _update_entity_schema(self) -> Any:
        for key in self.columns_dict.keys():
            if key in self.columns.discrete and self.columns_dict[key]["discreteness"] != "discrete":
                self.columns_dict[key].discreteness = "discrete"
            elif key in self.columns.continuous and self.columns_dict[key]["discreteness"] != "continuous":
                self.columns_dict[key].discreteness = "continuous"
