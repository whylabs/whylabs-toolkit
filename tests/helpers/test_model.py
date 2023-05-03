import os

import pytest
from whylabs_client.api.models_api import ModelsApi

from whylabs_toolkit.helpers.models import update_model_metadata
from whylabs_toolkit.helpers.utils import get_models_api

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
