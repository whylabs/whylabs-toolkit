import os

import pytest

from whylabs_toolkit.helpers.schema import (
    ColumnsClassifiers,
    ColumnsDiscreteness,
    UpdateColumnClassifiers,
    UpdateColumnsDiscreteness,
    UpdateEntityDataTypes
)
from whylabs_toolkit.monitor.models.column_schema import ColumnDataType

ORG_ID = os.environ["ORG_ID"]
DATASET_ID = os.environ["DATASET_ID"]


def test_change_columns_input_output() -> None:
    classifiers = ColumnsClassifiers(
        inputs=["temperature"],
        outputs=["prediction_temperature"]
    )

    update_entity = UpdateColumnClassifiers(
        classifiers=classifiers,
        dataset_id=DATASET_ID,
        org_id=ORG_ID
    )

    update_entity.update()

    assert update_entity.current_entity_schema["columns"]["temperature"]["classifier"] == "input"
    assert update_entity.current_entity_schema["columns"]["prediction_temperature"]["classifier"] == "output"

    correct_classifiers = ColumnsClassifiers(outputs=["temperature"])

    update_entity = UpdateColumnClassifiers(
        classifiers=correct_classifiers,
        dataset_id=DATASET_ID,
        org_id=ORG_ID
    )

    update_entity.update()

    assert update_entity.current_entity_schema["columns"]["temperature"]["classifier"] == "output"


def test_change_columns_discreteness() -> None:
    columns = ColumnsDiscreteness(
        discrete=["prediction_temperature"],
        continuous=["temperature"]
    )

    update_discreteness = UpdateColumnsDiscreteness(
        dataset_id=DATASET_ID,
        columns=columns,
        org_id=ORG_ID
    )

    update_discreteness.update()

    assert update_discreteness.current_entity_schema["columns"]["temperature"]["discreteness"] == "continuous"
    assert update_discreteness.current_entity_schema["columns"]["prediction_temperature"][
               "discreteness"] == "discrete"

    columns = ColumnsDiscreteness(
        discrete=["temperature"],
        continuous=["prediction_temperature"]
    )

    update_discreteness = UpdateColumnsDiscreteness(
        dataset_id=DATASET_ID,
        columns=columns,
        org_id=ORG_ID
    )

    update_discreteness.update()

    assert update_discreteness.current_entity_schema["columns"]["temperature"]["discreteness"] == "discrete"
    assert update_discreteness.current_entity_schema["columns"]["prediction_temperature"][
               "discreteness"] == "continuous"


def test_same_column_on_both_parameters_should_raise():
    columns = ColumnsDiscreteness(
        discrete=["temperature"],
        continuous=["temperature"]
    )

    update_discreteness = UpdateColumnsDiscreteness(
        dataset_id=DATASET_ID,
        columns=columns,
        org_id=ORG_ID
    )
    with pytest.raises(ValueError):
        update_discreteness.update()

    classifiers = ColumnsClassifiers(
        inputs=["temperature"],
        outputs=["temperature"]
    )

    update_entity = UpdateColumnClassifiers(
        classifiers=classifiers,
        dataset_id=DATASET_ID,
        org_id=ORG_ID
    )
    with pytest.raises(ValueError):
        update_entity.update()


def test_change_columns_schema():
    columns_schema = {"temperature": ColumnDataType.boolean}

    update_data_types = UpdateEntityDataTypes(
        dataset_id=DATASET_ID,
        columns_schema=columns_schema,
        org_id=ORG_ID
    )

    update_data_types.update()

    assert update_data_types.current_entity_schema["columns"]["temperature"]["data_type"] == "bool"

    columns_schema = {"temperature": ColumnDataType.fractional}

    update_data_types = UpdateEntityDataTypes(
        dataset_id=DATASET_ID,
        columns_schema=columns_schema,
        org_id=ORG_ID
    )

    update_data_types.update()

    assert update_data_types.current_entity_schema["columns"]["temperature"]["data_type"] == "fractional"


def test_wrong_configuration_on_data_types():
    # If the specified column does not exist
    columns_schema = {"some_weird_column": ColumnDataType.boolean}

    update_data_types = UpdateEntityDataTypes(
        dataset_id=DATASET_ID,
        columns_schema=columns_schema,
        org_id=ORG_ID
    )

    # Nothing gets updated

    update_data_types.update()

    # If a datatype doesn't exist
    columns_schema = {"temperature": "booleans"}

    update_data_types = UpdateEntityDataTypes(
        dataset_id=DATASET_ID,
        columns_schema=columns_schema,
        org_id=ORG_ID
    )

    # It throws an exception
    with pytest.raises(ValueError):
        update_data_types.update()
