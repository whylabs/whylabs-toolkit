import os

import pytest
from whylabs_client.api.models_api import ModelsApi

from whylabs_toolkit.helpers.models import update_model_metadata, add_custom_metric
from whylabs_toolkit.helpers.utils import get_models_api
from whylabs_toolkit.helpers.config import Config

ORG_ID = os.environ["ORG_ID"]
DATASET_ID = os.environ["DATASET_ID"]


@pytest.fixture
def models_api() -> ModelsApi:
    return get_models_api()


def test_update_model_time_period(models_api: ModelsApi) -> None:
    update_model_metadata(dataset_id=DATASET_ID, org_id=ORG_ID, time_period="P1D")
    model_meta = models_api.get_model(model_id=DATASET_ID, org_id=ORG_ID)
    
    assert model_meta["time_period"] == "P1D"
    
    update_model_metadata(dataset_id=DATASET_ID, org_id=ORG_ID, time_period="P1M")
    model_meta = models_api.get_model(model_id=DATASET_ID, org_id=ORG_ID)
    
    assert model_meta["time_period"] == "P1M"


def test_update_model_type(models_api: ModelsApi) -> None:
    update_model_metadata(dataset_id=DATASET_ID, org_id=ORG_ID, model_type="REGRESSION")
    model_meta = models_api.get_model(model_id=DATASET_ID, org_id=ORG_ID)
    
    assert model_meta["model_type"] == "REGRESSION"
    
    update_model_metadata(dataset_id=DATASET_ID, org_id=ORG_ID, model_type="CLASSIFICATION")
    model_meta = models_api.get_model(model_id=DATASET_ID, org_id=ORG_ID)
    
    assert model_meta["model_type"] == "CLASSIFICATION"


def test_create_custom_metric(models_api: ModelsApi) -> None:
    add_custom_metric(
        dataset_id="model-7",
        label="temperature.median",
        column="temperature",
        default_metric="median",
    )
    
    org_id = Config().get_default_org_id()
    
    entity = models_api.get_entity_schema(dataset_id="model-7", org_id=org_id)
    
    assert entity["metrics"]["temperature.median"].to_dict() == {'column': 'temperature', 'default_metric': 'median','label': 'temperature.median'}
    
    models_api.delete_entity_schema_metric(org_id=org_id, dataset_id="model-7", metric_label="temperature.median")