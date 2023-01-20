import os

import pytest

from whylabs_toolkit.helpers.schema import (
    ColumnsClasses,
    ColumnsDiscreteness,
    UpdateColumnClasses,
    UpdateColumnsDiscreteness,
    UpdateEntityDataTypes
)

ORG_ID = os.environ["ORG_ID"]
DATASET_ID = os.environ["DATASET_ID"]


def test_change_columns_input_output() -> None:
    classes = ColumnsClasses(
        inputs=["temperature"],
        outputs=["prediction_temperature"]
    )

    update_entity = UpdateColumnClasses(
        classes=classes,
        dataset_id=DATASET_ID,
        org_id=ORG_ID
    )

    update_entity.update()

    assert update_entity.current_entity_schema["columns"]["temperature"]["classifier"] == "input"
    assert update_entity.current_entity_schema["columns"]["prediction_temperature"]["classifier"] == "output"

    correct_classes = ColumnsClasses(outputs=["temperature"])

    update_entity = UpdateColumnClasses(
        classes=correct_classes,
        dataset_id=DATASET_ID,
        org_id=ORG_ID
    )

    update_entity.update()

    assert update_entity.current_entity_schema["columns"]["temperature"]["classifier"] == "output"


def test_change_columns_discreteness() -> None:
    columns_discrete = ColumnsDiscreteness(
        discrete=["prediction_temperature"],
        continuous=["temperature"]
    )

    update_discreteness = UpdateColumnsDiscreteness(
        dataset_id=DATASET_ID,
        classes=columns_discrete,
        org_id=ORG_ID
    )

    update_discreteness.update()

    assert update_discreteness.current_entity_schema["columns"]["temperature"]["discreteness"] == "continuous"
    assert update_discreteness.current_entity_schema["columns"]["prediction_temperature"][
               "discreteness"] == "discrete"

    columns_discrete = ColumnsDiscreteness(
        discrete=["temperature"],
        continuous=["prediction_temperature"]
    )

    update_discreteness = UpdateColumnsDiscreteness(
        dataset_id=DATASET_ID,
        classes=columns_discrete,
        org_id=ORG_ID
    )

    update_discreteness.update()

    assert update_discreteness.current_entity_schema["columns"]["temperature"]["discreteness"] == "discrete"
    assert update_discreteness.current_entity_schema["columns"]["prediction_temperature"][
               "discreteness"] == "continuous"


def test_change_columns_schema():
    columns_schema = {"temperature": "bool"}

    update_data_types = UpdateEntityDataTypes(
        dataset_id=DATASET_ID,
        columns_schema=columns_schema,
        org_id=ORG_ID
    )

    update_data_types.update()

    assert update_data_types.current_entity_schema["columns"]["temperature"]["dataType"] == "bool"

    columns_schema = {"temperature": "fractional"}

    update_data_types = UpdateEntityDataTypes(
        dataset_id=DATASET_ID,
        columns_schema=columns_schema,
        org_id=ORG_ID
    )

    update_data_types.update()

    assert update_data_types.current_entity_schema["columns"]["temperature"]["dataType"] == "fractional"


def test_wrong_configuration_on_data_types():
    # If the specified column does not exist
    columns_schema = {"some_weird_column": "bool"}

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
